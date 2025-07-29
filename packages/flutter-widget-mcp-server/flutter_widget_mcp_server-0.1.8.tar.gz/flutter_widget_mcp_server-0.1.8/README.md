# Flutter Widget MCP Server

Flutter Widget MCP Server 是一个用于 Flutter Widget 组件库的 Model Context Protocol (MCP) 服务器。它提供了一个强大的 API 来查询和搜索 Flutter 组件的详细信息。

## 特性

- 组件查询：获取特定组件的详细信息
- 组件列表：获取所有可用组件的列表
- 组件搜索：根据关键词搜索组件
- 支持部分匹配和不区分大小写的查询

## 安装

使用 pip 安装 Flutter Widget MCP Server：

```
pip install flutter-widget-mcp-server
```

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
