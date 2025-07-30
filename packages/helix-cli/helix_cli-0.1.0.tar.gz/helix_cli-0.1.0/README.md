# Helix - 软件包管理工具

这是一个命令⾏⼯具，⽤于管理和查询多种类型的软件包（Component），包括 SDK、⼯具链等。它可以快速获取版本信息、根据 commit 哈希查找对应的发布包，以及检查更新。

## 功能

- **多组件支持**：支持 `sdk`, `toolchain`, `qemu`, `nncase`, `pytorch` 等多种组件类型。
- **版本查询**：列出指定组件所有可用的版本。
- **按 Commit 搜索**：根据 Git 的 commit 哈希在所有版本中快速查找对应的软件包。
- **检查更新**：对⽐当前版本和最新版本，了解是否有可⽤更新。
- **并⾏处理**：利⽤并⾏请求加速查找过程，提升效率。
- **缓存机制**：内置缓存功能，减少重复⽹络请求，加快后续查询速度。

## 依赖项

在运⾏脚本之前，请确保安装以下 Python 包：

```bash
pip install requests beautifulsoup4
```

## 使⽤⽅法

所有命令都需要通过 `helix.py` 执⾏，并指定要操作的组件类型。

**⽀持的组件类型 (component):** `sdk`, `toolchain`, `qemu`, `nncase`, `pytorch`

---

### 1. 列出所有版本 (list)

列出指定组件的所有可⽤版本，按时间倒序排列。

**命令格式:**
```bash
python helix.py <component> list
```

**示例:**
```bash
# 列出所有可⽤的 sdk 版本
python helix.py sdk list

# 列出所有可⽤的 toolchain 版本
python helix.py toolchain list
```

---

### 2. 按 Commit 搜索 (search)

根据 commit 哈希查找匹配的软件包及其下载链接。

**命令格式:**
```bash
python helix.py <component> search <commit_hash>
```

**示例:**
```bash
# 在 nncase 组件中搜索包含特定 commit 的软件包
python helix.py nncase search 9ab1c2d

# 在 pytorch 组件中搜索
python helix.py pytorch search v1.13.0
```

---

### 3. 检查更新 (upgrade)

检查某个组件是否有⽐指定版本更新的版本。

**命令格式:**
```bash
python helix.py <component> upgrade <current_version>
```

**示例:**
```bash
# 检查 sdk 是否有⽐ v0.3.1 更新的版本
python helix.py sdk upgrade v0.3.1
```

---

### 4. 清除缓存 (clean-cache)

删除本地缓存，以便下次运⾏时强制从服务器获取最新数据。

**命令格式:**
```bash
python helix.py clean-cache
```
该命令不需要指定组件。

## ⼯作原理

1.  **数据获取**：⼯具通过 HTTP 请求从预设的服务器地址获取各组件的发布⽬录信息。
2.  **HTML 解析**：使⽤ `BeautifulSoup` 解析⽬录⻚⾯的 HTML，提取出版本号和软件包⽂件列表。
3.  **并⾏搜索**：在 `search` 操作中，⼯具会启动多个线程并⾏扫描所有版本⽬录，以加快匹配速度。
4.  **缓存策略**：首次获取的数据会以 JSON 格式存储在本地缓存中。在缓存有效期内，后续请求将直接从本地读取，避免了不必要的⽹络延迟。

## 注意事项

- **缓存位置**：缓存⽂件默认存储在 `~/.cache/sdk_manager/sdk_cache.json`。
- **缓存有效期**：缓存默认有效期为 1 ⼩时（3600 秒），可在脚本的 `CACHE_TTL` 全局变量中修改。
- **组件源**：各组件的下载地址在脚本内的 `COMPONENT_TYPES` 字典中定义。 