# AI 驱动的地图导航系统

基于 MCP (Model Context Protocol) 架构的智能导航系统，支持文字和语音输入，自动打开高德地图或百度地图并进入导航状态。

## ✨ 功能特性

- 🎤 **语音输入支持**: 集成七牛实时语音识别
- ⌨️ **文字输入支持**: 自然语言理解
- 🤖 **AI 智能解析**: 支持多种 AI 提供商（七牛 AI、Anthropic Claude）
- 🗺️ **多地图支持**: 高德地图和百度地图
- 🔧 **MCP 架构**: 完全基于 MCP 协议，无硬编码逻辑
- 🚀 **自动化导航**: 自动打开浏览器并设置导航路线

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────┐
│          用户输入层                          │
│    文字输入  │  语音输入(七牛语音识别)      │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│          AI 解析层                           │
│  七牛AI推理API / Anthropic Claude           │
│  (OpenAI兼容API)                            │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│        MCP 服务层                            │
│  ┌────────────┐      ┌──────────────┐       │
│  │高德MCP     │      │浏览器控制    │       │
│  │Server      │      │MCP Server    │       │
│  │(Streamable │      │(本地实现)    │       │
│  │ HTTP)      │      │              │       │
│  └────────────┘      └──────────────┘       │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│          执行层                              │
│       打开浏览器 → 地图导航                  │
└─────────────────────────────────────────────┘
```

## 📦 项目结构

```
Project/
├── main.py                    # 主程序入口
├── amap_mcp_client.py         # 高德地图 MCP 客户端
├── voice_input.py             # 七牛语音识别模块
├── mcp_browser_server.py      # 浏览器控制 MCP Server
├── config.json                # 配置文件
├── requirements.txt           # Python 依赖
├── .env.example              # 环境变量示例
└── README.md                 # 项目文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API 密钥

编辑 `config.json` 文件，填入您的 API 密钥：

```json
{
  "mcpServers": {
    "amap-maps-streamableHTTP": {
      "url": "https://mcp.amap.com/mcp?key=您的高德API_KEY"
    }
  },
  "qiniu": {
    "accessKey": "您的七牛AccessKey",
    "secretKey": "您的七牛SecretKey"
  },
  "ai": {
    "provider": "qiniu"
  }
}
```

**获取 API 密钥：**
- **高德地图**: https://console.amap.com/
- **七牛云**: https://portal.qiniu.com/

### 3. 运行程序

#### 文字输入模式（推荐）

```bash
python main.py --text
```

然后输入导航指令，例如：
- `从北京到上海`
- `去天安门`
- `用百度地图从杭州到苏州`

#### 语音输入模式

```bash
python main.py --voice --duration 5
```

说出导航指令（录音 5 秒）。

#### 交互模式

```bash
python main.py
```

持续输入导航指令，输入 `quit` 退出。

## 📖 使用示例

### 示例 1: 文字输入

```bash
$ python main.py --text

============================================================
🗺️  AI 地图导航系统
============================================================

⌨️  文字输入模式

请输入导航指令 (例如: 从北京到上海): 从杭州西湖到上海外滩

============================================================
🚀 开始导航流程
============================================================

🤖 AI 正在解析: "从杭州西湖到上海外滩"
✅ AI 解析结果: {'origin': '杭州西湖', 'destination': '上海外滩', 'map_service': 'amap'}

📍 导航信息:
   起点: 杭州西湖
   终点: 上海外滩
   地图: AMAP

[1/3] 🔍 查询起点坐标: 杭州西湖
   ✅ 杭州西湖: (120.1489, 30.2503)

[2/3] 🔍 查询终点坐标: 上海外滩
   ✅ 上海外滩: (121.4906, 31.2397)

[3/3] 🌐 打开浏览器导航...

✅ 已打开AMAP地图导航
📍 URL: https://uri.amap.com/navigation?from=120.1489,30.2503&to=121.4906,31.2397&policy=1&coordinate=gaode

✅ 导航启动完成!
```

### 示例 2: 语音输入

```bash
$ python main.py --voice --duration 5

============================================================
🗺️  AI 地图导航系统
============================================================

🎤 语音输入模式

🎤 开始录音（5 秒）...
✅ 录音完成

🎤 正在识别语音...
✅ 识别结果: "用高德地图从广州到深圳"

============================================================
🚀 开始导航流程
============================================================
...
```

## ⚙️ 配置说明

### config.json 详解

```json
{
  "mcpServers": {
    "amap-maps-streamableHTTP": {
      "url": "https://mcp.amap.com/mcp?key=YOUR_KEY"
    }
  },
  "qiniu": {
    "accessKey": "YOUR_ACCESS_KEY",
    "secretKey": "YOUR_SECRET_KEY"
  },
  "ai": {
    "provider": "qiniu",
    "qiniu": {
      "apiUrl": "https://api.qiniu.com/v1/ai/inference",
      "model": "gpt-3.5-turbo"
    },
    "anthropic": {
      "apiKey": "YOUR_ANTHROPIC_KEY",
      "model": "claude-3-5-sonnet-20241022"
    }
  },
  "defaultMapService": "amap"
}
```

### AI 提供商切换

**使用七牛 AI（推荐）：**
```json
{
  "ai": {
    "provider": "qiniu"
  }
}
```

**使用 Anthropic Claude：**
```json
{
  "ai": {
    "provider": "anthropic",
    "anthropic": {
      "apiKey": "sk-ant-..."
    }
  }
}
```

## 🔧 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| **语音识别** | 七牛实时语音识别 | https://developer.qiniu.com/dora/8084/real-time-speech-recognition |
| **AI 推理** | 七牛 AI 推理 API (OpenAI 兼容) | https://developer.qiniu.com/aitokenapi/12882/ai-inference-api |
| **地图服务** | 高德地图 MCP Server (Streamable HTTP) | https://lbs.amap.com/api/mcp-server/gettingstarted |
| **浏览器控制** | webbrowser + MCP 封装 | 本地实现 |
| **编程语言** | Python 3.8+ | - |

## 🎯 MCP 实现说明

本项目**完全基于 MCP 协议**实现，体现在：

### 1. 高德地图 MCP 客户端
- 使用官方 Streamable HTTP 接入方式
- 通过 JSON-RPC 2.0 协议调用工具
- 实现了 `geocode`、`reverse_geocode`、`search_poi` 等功能

### 2. 浏览器控制 MCP Server
- 符合 MCP 标准的本地 Server
- 提供 `open_url` 和 `open_map_navigation` 工具
- 支持多地图服务（高德、百度）

### 3. 无硬编码逻辑
- 地图服务通过 MCP 工具调用
- 浏览器控制通过 MCP 工具调用
- AI 解析驱动整个流程

## 🧪 开发与测试

### Mock 模式

未配置 API Key 时，系统自动使用 Mock 模式：

**高德 MCP Mock:**
- 支持 10 个主要城市（北京、上海、广州等）
- 无需真实 API Key 即可测试

**语音识别 Mock:**
- 返回固定测试语句
- 用于开发调试

### 添加新的地图服务

在 `mcp_browser_server.py` 中添加：

```python
def _build_newmap_url(self, start_lng, start_lat, end_lng, end_lat) -> str:
    # 实现新地图的 URL 构建逻辑
    pass
```

## 📝 常见问题

**Q: 为什么需要七牛云账号？**  
A: 用于语音识别和 AI 推理服务。如果只使用文字输入，可以不配置七牛密钥（使用 Mock 模式）。

**Q: 可以只使用高德地图吗？**  
A: 可以。只需配置高德 API Key，系统会自动使用高德地图。

**Q: 语音识别不工作怎么办？**  
A: 
1. 确保已安装 `sounddevice`: `pip install sounddevice`
2. 检查麦克风权限
3. 使用文字输入作为替代

**Q: 支持哪些输入格式？**  
A: 
- `从北京到上海`
- `去天安门`
- `用百度地图从杭州到苏州`
- `我要从广州去深圳`
- 其他自然语言表达

## 🔮 后续扩展计划

- [ ] 支持路线偏好设置（避开高速、最短时间等）
- [ ] 支持更多地图服务（腾讯地图等）
- [ ] Web 界面
- [ ] 桌面应用（Electron）
- [ ] 路线实时追踪

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请提交 Issue 或联系开发团队。

---

**⭐ 如果这个项目对您有帮助，请给个 Star！**
