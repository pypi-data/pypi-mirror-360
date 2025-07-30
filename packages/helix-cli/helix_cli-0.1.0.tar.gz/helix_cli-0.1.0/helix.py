#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import re
import sys
import os
import json
import functools
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# Configuration
COMPONENT_TYPES = {
    "sdk": "http://sw-file.a-bug.org/k80/common/sdk/duca/release/",
    "toolchain": "http://sw-file.a-bug.org/k80/common/toolchain/release/",
    "qemu": "http://sw-file.a-bug.org/k80/common/sdk/qemu/release/",
    "nncase": "http://sw-file.a-bug.org/k80/common/nncase/release/",
    "pytorch": "http://sw-file.a-bug.org/k80/common/framework/release/"
}

CACHE_DIR = os.path.expanduser("~/.cache/sdk_manager")
CACHE_FILE = os.path.join(CACHE_DIR, "sdk_cache.json")
CACHE_TTL = 3600  # 1 hour

class CacheManager:
    """Handles caching and retrieval of component data"""
    def __init__(self):
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR, exist_ok=True)
            
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """Load cache from file if valid"""
        cache_data = {'timestamp': 0, 'data': {}}
        
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r') as f:
                    data = json.load(f)
                    # Validate cache freshness
                    if datetime.now().timestamp() - data.get('timestamp', 0) < CACHE_TTL:
                        # 确保缓存数据有正确的结构
                        if 'data' not in data:
                            data['data'] = {}
                        return data
            except Exception as e:
                print(f"Warning: Cache load failed: {e}", file=sys.stderr)
                
        return cache_data
    
    def save(self):
        """Save cache to disk"""
        try:
            self.cache['timestamp'] = datetime.now().timestamp()
            with open(CACHE_FILE, 'w') as f:
                json.dump(self.cache, f)
        except Exception as e:
            print(f"Warning: Cache save failed: {e}", file=sys.stderr)
    
    def get(self, key, component=""):
        """Retrieve cached data for specific key and component"""
        # 确保数据结构正确初始化
        if 'data' not in self.cache:
            self.cache['data'] = {}
        
        component_cache = self.cache['data'].get(component, {})
        return component_cache.get(key)
    
    def set(self, key, value, component=""):
        """Store data in cache"""
        # 确保数据结构正确初始化
        if 'data' not in self.cache:
            self.cache['data'] = {}
            
        if component not in self.cache['data']:
            self.cache['data'][component] = {}
        self.cache['data'][component][key] = value

class SDKManager:
    def __init__(self):
        self.session = requests.Session()
        self.cache = CacheManager()
    
    @functools.lru_cache(maxsize=128)
    def fetch_html(self, url):
        """Fetch and parse HTML content with caching"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"Error retrieving {url}: {e}", file=sys.stderr)
            return None
    
    def get_version_dirs(self, component_type):
        """Get available version directories for a component"""
        cache_key = "versions"
        cached = self.cache.get(cache_key, component_type)
        if cached:
            return cached
            
        base_url = COMPONENT_TYPES[component_type]
        soup = self.fetch_html(base_url)
        if not soup:
            return []
        
        versions = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href.startswith('v') and href.endswith('/'):
                versions.append(href.rstrip('/'))
        
        # 对版本进行排序，使用安全的解析方法
        try:
            versions.sort(key=self.parse_version, reverse=True)
        except Exception:
            # 如果排序失败，使用字典序排序
            versions.sort(reverse=True)
            
        self.cache.set(cache_key, versions, component_type)
        return versions
    
    def parse_version(self, version_str):
        """Parse version string into comparable tuple"""
        try:
            match = re.match(r'v(\d+)\.(\d+)\.(\d+)', version_str)
            if match:
                return tuple(int(part) for part in match.groups())
            return (0, 0, 0)  # 无法解析时返回默认值
        except Exception:
            return (0, 0, 0)
    
    def get_packages(self, component_type, version):
        """Get packages for specific component version"""
        cache_key = f"packages_{version}"
        cached = self.cache.get(cache_key, component_type)
        if cached:
            return cached
            
        base_url = COMPONENT_TYPES[component_type]
        url = urljoin(base_url, version + '/')
        soup = self.fetch_html(url)
        if not soup:
            return []
        
        packages = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and any(href.endswith(ext) for ext in ['.tar.gz', '.zip', '.run', '.whl']):
                packages.append(href)
        
        # Special handling for nncase wheels
        if component_type == "nncase":
            wheel_url = urljoin(url, 'wheel/')
            try:
                wheel_soup = self.fetch_html(wheel_url)
                if wheel_soup:
                    for link in wheel_soup.find_all('a'):
                        href = link.get('href')
                        if href and href.endswith('.whl'):
                            packages.append('wheel/' + href)
                else:
                    print(f"Note: No wheel subdirectory found for {component_type} version {version}")
            except Exception as e:
                print(f"Warning: Error accessing wheel subdirectory: {e}", file=sys.stderr)
        
        self.cache.set(cache_key, packages, component_type)
        return packages
    
    def match_commit(self, component_type, commit_hash):
        """Find matching package for a commit hash"""
        # Check cache first
        cache_key = f"commit_{commit_hash}"
        cached = self.cache.get(cache_key, component_type)
        if cached:
            return cached
        
        commit_hash = commit_hash.lower()
        versions = self.get_version_dirs(component_type)
        
        if not versions:
            print(f"No version directories found for {component_type}")
            return None
        
        # Direct version match for specific components
        if component_type in ["pytorch", "nncase"]:
            for version in versions:
                if commit_hash == version.lower() or (component_type == "nncase" and commit_hash == version[1:].lower()):
                    result = self.process_version(component_type, version, commit_hash)
                    if result:
                        self.cache.set(cache_key, result, component_type)
                        return result
        
        # Parallel search across versions
        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(
                self.process_version, 
                component_type, 
                version, 
                commit_hash
            ) for version in versions]
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)
        
        if not results:
            return None
        
        # Get latest matching version - 安全处理排序
        try:
            results.sort(key=lambda x: self.parse_version(x['version']), reverse=True)
        except Exception:
            # 排序失败时，使用字典序
            results.sort(key=lambda x: x['version'], reverse=True)
            
        self.cache.set(cache_key, results[0], component_type)
        return results[0]
    
    def process_version(self, component_type, version, commit_hash):
        """Process a single version for commit matching"""
        packages = self.get_packages(component_type, version)
        base_url = COMPONENT_TYPES[component_type]
        
        # 首先检查版本名称直接匹配的情况
        version_match = (version.lower() == commit_hash.lower() or 
                        (component_type == "nncase" and version[1:].lower() == commit_hash.lower()))
        
        # 特殊情况处理
        if component_type == "nncase" and version_match:
            return self.handle_nncase_version(version, packages, base_url)
        
        if component_type == "pytorch" and version_match:
            return self.handle_pytorch_version(version, packages, base_url)
        
        # 常规包名匹配
        for package in packages:
            package_name = package.split('/')[-1] if '/' in package else package
            if commit_hash.lower() in package_name.lower():
                # 构建完整URL
                package_path = package
                package_url = urljoin(urljoin(base_url, version + '/'), package_path)
                
                return {
                    'version': version,
                    'package': package_name,
                    'url': package_url
                }
        
        return None
    
    def handle_nncase_version(self, version, packages, base_url):
        """Handle nncase version match"""
        wheel_packages = []
        
        # 首先收集根目录下的 whl 包
        for package in packages:
            if package.endswith('.whl') and not package.startswith('wheel/'):
                wheel_packages.append({
                    'package': package,
                    'url': urljoin(urljoin(base_url, version + '/'), package),
                    'location': 'root'
                })
        
        # 再收集 wheel 子目录下的 whl 包
        for package in packages:
            if package.startswith('wheel/') and package.endswith('.whl'):
                wheel_packages.append({
                    'package': package.replace('wheel/', ''),
                    'url': urljoin(urljoin(base_url, version + '/'), package),
                    'location': 'wheel'
                })
        
        if wheel_packages:
            return {
                'version': version,
                'multiple_packages': True,
                'packages': wheel_packages
            }
        return None
    
    def handle_pytorch_version(self, version, packages, base_url):
        """Handle pytorch version match"""
        for package in packages:
            if package.endswith('.whl'):
                return {
                    'version': version,
                    'package': package,
                    'url': urljoin(urljoin(base_url, version + '/'), package)
                }
        return None
    
    def find_new_versions(self, component_type, current_version):
        """Find versions newer than current"""
        versions = self.get_version_dirs(component_type)
        
        try:
            current_tuple = self.parse_version(current_version)
            return [v for v in versions if self.parse_version(v) > current_tuple]
        except Exception as e:
            print(f"Error comparing versions: {e}", file=sys.stderr)
            return []

def create_cli():
    """Create command-line interface"""
    parser = argparse.ArgumentParser(
        prog='sdk-manager',
        description='Component Management Utility',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Component selection
    parser.add_argument('-c', '--component', 
                        choices=COMPONENT_TYPES.keys(), 
                        default='sdk',
                        help='Target component type (default: sdk)')
    
    subparsers = parser.add_subparsers(
        title='commands',
        dest='command',
        metavar="<command>",
        help='[ls|search|upgrade|clear-cache]'
    )
    
    # List command
    list_parser = subparsers.add_parser(
        'ls', 
        help='List available versions and packages'
    )
    list_parser.add_argument('--no-cache', action='store_true', 
                             help='Bypass cache')
    
    # Search command
    search_parser = subparsers.add_parser(
        'search', 
        help='Find package for commit hash'
    )
    search_parser.add_argument(
        'commit',
        help='Commit SHA or version identifier'
    )
    search_parser.add_argument('--no-cache', action='store_true', 
                              help='Bypass cache')
    
    # Upgrade check command
    upgrade_parser = subparsers.add_parser(
        'upgrade', 
        help='Check for newer versions'
    )
    upgrade_parser.add_argument(
        'version',
        help='Current version (e.g., v0.3.1)'
    )
    upgrade_parser.add_argument('--no-cache', action='store_true', 
                               help='Bypass cache')
    
    # Cache command
    subparsers.add_parser(
        'clear-cache', 
        help='Clear local cache'
    )
    
    return parser

def print_package_list(manager, component):
    """Print formatted package listing"""
    try:
        versions = manager.get_version_dirs(component)
        if not versions:
            print(f"No versions found for {component}")
            return
            
        print(f"{len(versions)} versions available for {component}:")
        print("-" * 60)
        
        for version in versions:
            packages = manager.get_packages(component, version)
            print(f"\nVersion: {version}")
            if packages:
                for package in sorted(packages):
                    print(f"  • {package}")
            else:
                print("  (No packages)")
                
        print()
    except Exception as e:
        print(f"Error listing packages: {str(e)}")

def print_search_results(manager, component, commit):
    """Print commit search results"""
    try:
        result = manager.match_commit(component, commit)
        if not result:
            print(f"No matching package found for {commit}")
            return
            
        if result.get('multiple_packages'):
            print(f"Found multiple packages for {component} version {result['version']}:")
            print("-" * 60)
            
            # 按位置分组显示
            root_packages = [pkg for pkg in result['packages'] if pkg.get('location') == 'root']
            wheel_packages = [pkg for pkg in result['packages'] if pkg.get('location') == 'wheel']
            
            if root_packages:
                print("\nRoot directory packages:")
                for pkg in root_packages:
                    print(f"  • Package: {pkg['package']}")
                    print(f"    URL:     {pkg['url']}")
                    print(f"    Install: pip install {pkg['url']}")
            
            if wheel_packages:
                print("\nWheel subdirectory packages:")
                for pkg in wheel_packages:
                    print(f"  • Package: {pkg['package']}")
                    print(f"    URL:     {pkg['url']}")
                    print(f"    Install: pip install {pkg['url']}")
        else:
            print(f"Matched package:")
            print(f"Version:  {result['version']}")
            print(f"Package:  {result['package']}")
            print(f"URL:      {result['url']}")
            if result['package'].endswith('.whl'):
                print(f"Install:  pip install {result['url']}")
            else:
                print(f"Download: wget {result['url']}")
        print()
    except Exception as e:
        print(f"Error searching for package: {str(e)}")

def print_upgrade_info(manager, component, current_version):
    """Print upgrade information"""
    try:
        new_versions = manager.find_new_versions(component, current_version)
        if not new_versions:
            print(f"Current version {current_version} is latest")
            return
            
        print(f"Found {len(new_versions)} newer versions:")
        for idx, version in enumerate(new_versions[:3], 1):
            print(f"  {idx}. {version}")
        
        if not new_versions:
            return
            
        latest = new_versions[0]
        packages = manager.get_packages(component, latest)
        
        if packages:
            print(f"\nLatest version {latest} includes:")
            for package in sorted(packages)[:5]:
                print(f"  • {package}")
            
            if packages:
                base_url = COMPONENT_TYPES[component]
                sample_pkg = packages[0]
                pkg_url = urljoin(urljoin(base_url, latest + '/'), sample_pkg)
                if sample_pkg.endswith('.whl'):
                    print(f"\nInstall: pip install {pkg_url}")
                else:
                    print(f"\nDownload: wget {pkg_url}")
        print()
    except Exception as e:
        print(f"Error checking for upgrades: {str(e)}")

def main():
    parser = create_cli()
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    
    if args.command == 'clear-cache':
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
            print("Cache cleared successfully")
        else:
            print("No cache found")
        return
    
    manager = SDKManager()
    
    # Bypass cache if requested
    if hasattr(args, 'no_cache') and args.no_cache:
        # 重置缓存时间戳，强制刷新
        if 'cache' in manager.__dict__ and hasattr(manager.cache, 'cache'):
            manager.cache.cache['timestamp'] = 0
    
    try:
        if args.command == 'ls':
            print_package_list(manager, args.component)
        elif args.command == 'search':
            print_search_results(manager, args.component, args.commit)
        elif args.command == 'upgrade':
            print_upgrade_info(manager, args.component, args.version)
        else:
            parser.print_help()
    finally:
        # 保存缓存
        if 'cache' in manager.__dict__ and hasattr(manager.cache, 'save'):
            manager.cache.save()

if __name__ == "__main__":
    main()