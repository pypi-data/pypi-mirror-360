# Flutter Widget MCP Server

Flutter Widget MCP Server 是一个用于 Flutter Widget 组件库的 Model Context Protocol (MCP) 服务器。它提供了一个强大的 API 来查询和搜索 Flutter 组件的详细信息。

## 特性

- 组件查询：获取特定组件的详细信息
- 组件列表：获取所有可用组件的列表
- 组件搜索：根据关键词搜索组件
- 支持部分匹配和不区分大小写的查询

## 安装

推荐使用最新版本的pip来安装Flutter Widget MCP Server。首先，更新pip：

```
python -m pip install --upgrade pip
```

然后，使用pip安装Flutter Widget MCP Server：

```
pip install flutter-widget-mcp-server
```

如果遇到安装问题，可以尝试以下命令：

```
pip install "flutter-widget-mcp-server[all]"
```

这将安装所有必要的依赖项。

### 故障排除

如果在安装过程中遇到"No matching distribution found for fastapi-mcp==0.3.4"错误，可以尝试以下步骤：

1. 确保您的网络连接正常，可以访问PyPI。
2. 尝试使用以下命令安装特定版本范围的fastapi-mcp：

```
pip install "fastapi-mcp>=0.3.4,<0.4.0"
```

3. 如果问题仍然存在，请检查是否有更新的flutter-widget-mcp-server版本可用，并尝试安装最新版本。

## 快速开始

1. 安装包后，首先需要生成组件数据：

```python
from flutter_widget_mcp_server.app.gen_components_json import generate_components_json

generate_components_json('path/to/your/components/docs', 'path/to/output/components.json')
```

2. 运行服务器：

```python
from flutter_widget_mcp_server.app.main import run_server

run_server()
```

服务器将在 http://localhost:8000 上运行。

## API 使用

### 查询特定组件

```
GET /components/{component_name}
```

示例：
```
GET /components/YLElevatedButton
```

### 列出所有组件

```
GET /components
```

### 搜索组件

```
GET /components/search?query={search_term}
```

示例：
```
GET /components/search?query=button
```
