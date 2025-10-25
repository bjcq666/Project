# AI 智能导航系统 - 安装与配置指南

## 系统简介

这是一个基于 AI 的智能导航程序，通过自然语言理解用户的导航需求，并自动调用高德地图服务规划路线，最后在浏览器中打开高德地图 Web 版显示导航结果。

## 技术栈

- **Python 3.8+**: 主要开发语言
- **高德地图 MCP Server**: 官方地图服务
- **DeepSeek API**: 自然语言理解
- **Playwright**: 浏览器自动化
- **MCP (Model Context Protocol)**: 工具调用协议

## 前置要求

### 1. Python 环境
确保已安装 Python 3.8 或更高版本：
```bash
python --version
```

### 2. Node.js 环境
高德地图 MCP Server 需要 Node.js 运行环境：
```bash
node --version
npm --version
```

如未安装，请访问 https://nodejs.org/ 下载安装。

### 3. 申请 API 密钥

#### 高德地图 API Key
1. 访问 https://lbs.amap.com/
2. 注册/登录账号
3. 进入控制台创建应用
4. 获取 Web 服务 API Key

#### DeepSeek API Key
1. 访问 https://platform.deepseek.com/
2. 注册/登录账号
3. 在 API Keys 页面创建新的密钥
4. 复制 API Key

## 安装步骤

### 1. 克隆/下载项目

```bash
git clone <repository-url>
cd Project
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 4. 安装 Playwright 浏览器

```bash
playwright install chromium
```

### 5. 配置环境变量

复制环境变量模板文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入您的 API 密钥：
```
AMAP_API_KEY=your_amap_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

### 6. 验证 MCP Server 安装

测试高德地图 MCP Server 是否可用：
```bash
npx -y @masx200/amap-maps-mcp-server
```

如果能正常启动（显示 MCP 服务信息），则说明安装成功。

## 使用方法

### 启动程序

```bash
python main.py
```

### 输入导航指令

程序会提示您输入导航指令，支持自然语言，例如：

- "我要从北京西站开车去颐和园，避开拥堵"
- "从天安门步行到故宫"
- "骑车从三里屯到鸟巢，走最短路线"
- "从上海虹桥机场到外滩，快一点"

### 导航参数说明

**起点**:
- 如果不指定，默认为"我的位置"
- 可以是地标、POI、详细地址

**终点**:
- 必须指定
- 可以是地标、POI、详细地址

**导航模式**:
- 驾车/开车 → `driving`
- 步行/走路 → `walking`
- 骑车/骑行 → `bicycling`

**路径策略**:
- 速度优先/快一点 → policy: 0
- 费用优先/省钱 → policy: 1
- 距离优先/最短路线 → policy: 2
- 躲避拥堵/不堵车 → policy: 4

## 项目结构

```
Project/
├── main.py                 # 主程序入口
├── ai_parser.py           # AI 意图解析模块
├── amap_mcp_client.py     # 高德地图 MCP 客户端
├── browser_controller.py  # 浏览器自动化控制器
├── config.py              # 配置管理
├── requirements.txt       # Python 依赖
├── .env.example          # 环境变量模板
├── .env                  # 环境变量配置（需自行创建）
├── SETUP.md              # 本文档
└── README.md             # 项目说明
```

## 模块说明

### 1. AI 意图解析模块 (`ai_parser.py`)
- 使用 DeepSeek API 解析自然语言输入
- 提取结构化的导航参数
- 返回 `NavigationIntent` 对象

### 2. MCP 客户端模块 (`amap_mcp_client.py`)
- 连接高德地图 MCP Server
- 提供地理编码功能 (`get_geocode`)
- 提供路线规划功能 (`get_route_plan`)
- 生成高德地图 Web 版 URL

### 3. 浏览器控制模块 (`browser_controller.py`)
- 使用 Playwright 控制浏览器
- 自动打开高德地图 Web 版
- 等待页面加载并显示路线

### 4. 主程序 (`main.py`)
- 整合各模块功能
- 实现完整的导航流程
- 提供友好的命令行交互

## 常见问题

### 1. 提示找不到 npx 命令
确保已安装 Node.js 并将其添加到系统 PATH 中。

### 2. MCP Server 连接失败
- 检查 AMAP_API_KEY 是否正确配置
- 确认网络连接正常
- 尝试手动运行: `npx -y @masx200/amap-maps-mcp-server`

### 3. AI 解析失败
- 检查 DEEPSEEK_API_KEY 是否正确
- 确认 DeepSeek API 余额充足
- 检查网络是否能访问 DeepSeek API

### 4. 浏览器无法打开
- 确认已安装 Playwright 浏览器: `playwright install chromium`
- 检查是否有权限启动浏览器进程

### 5. 地理编码失败
- 确认输入的地址/地标名称正确
- 尝试更详细的地址描述
- 检查高德地图 API 配额是否充足

## 扩展功能

### 语音输入（待实现）
可以集成 `speechrecognition` 库实现语音输入功能：
```bash
pip install speechrecognition pyaudio
```

### 多种浏览器支持
修改 `browser_controller.py` 中的浏览器类型：
```python
# 使用 Firefox
self.browser = await self.playwright.firefox.launch(...)

# 使用 WebKit (Safari)
self.browser = await self.playwright.webkit.launch(...)
```

## 技术支持

如遇到问题，请检查：
1. 所有依赖是否正确安装
2. API 密钥是否有效
3. 网络连接是否正常
4. Python 和 Node.js 版本是否符合要求

## 许可证

本项目仅供学习和研究使用。
