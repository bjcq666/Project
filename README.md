# AI 智能导航系统

基于 MCP 的 AI 驱动地图导航程序

## 功能特性

- 🗣️ **自然语言交互**: 通过自然语言描述导航需求
- 🤖 **AI 智能解析**: 使用 DeepSeek AI 准确理解用户意图
- 🗺️ **高德地图集成**: 调用官方高德地图 MCP Server 服务
- 🚗 **多种出行方式**: 支持驾车、步行、骑行三种导航模式
- 🎯 **智能路径规划**: 支持速度优先、费用优先、距离优先、躲避拥堵等策略
- 🌐 **自动打开地图**: 自动在浏览器中打开高德地图并显示规划路线

## 快速开始

### 安装

1. 克隆项目并进入目录
2. 安装依赖: `pip install -r requirements.txt`
3. 安装浏览器: `playwright install chromium`
4. 配置 API 密钥: 复制 `.env.example` 为 `.env` 并填入密钥

### 运行

```bash
python main.py
```

### 使用示例

```
请输入导航指令: 我要从北京西站开车去颐和园，避开拥堵
```

程序会自动：
1. 解析您的导航需求
2. 获取起点和终点的坐标
3. 规划最优路线
4. 在浏览器中打开高德地图显示导航

## 详细文档

完整的安装和配置指南请查看 [SETUP.md](SETUP.md)

## 技术架构

- **AI 解析**: DeepSeek API
- **地图服务**: 高德地图 MCP Server
- **浏览器自动化**: Playwright
- **开发语言**: Python 3.8+

## 项目结构

```
├── main.py                 # 主程序
├── ai_parser.py           # AI 意图解析
├── amap_mcp_client.py     # 高德地图客户端
├── browser_controller.py  # 浏览器控制
├── config.py              # 配置管理
└── requirements.txt       # 依赖列表
```

## 开源协议

本项目仅供学习和研究使用