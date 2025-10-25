# 新功能说明 (New Features)

本文档介绍了最新集成的功能模块。

## 1. 七牛云语音转文字 API

### 功能描述
集成了七牛云的语音转文字API，提供高质量的中文语音识别服务。

### 使用方法

#### 环境变量配置
```bash
export QINIU_SPEECH_API_KEY="your-qiniu-speech-api-key"
export QINIU_SPEECH_API_URL="https://api.qiniu.com/v1/speech/recognize"  # 可选，有默认值
```

#### 使用示例
运行程序时选择选项 `3. 七牛云语音输入`：
```bash
$ python main.py
请选择输入方式:
1. 文本输入
2. 语音输入 (本地/Google)
3. 七牛云语音输入
请选择 (1/2/3): 3
```

### 文件说明
- `qiniu_speech.py` - 七牛云语音识别模块
  - `QiniuSpeechRecognizer` - 主要的语音识别类
  - `get_qiniu_voice_input()` - 便捷函数，用于获取语音输入

## 2. 文本优化功能

### 功能描述
自动优化用户的导航请求文本，使其更加简洁和自然。

### 优化规则

#### 规则 1: "从xx到xx" → "我想到xx地方"
- 输入: `"我想从北京到上海"`
- 输出: `"我想到上海地方"`

#### 规则 2: "我想去xx" → "我想到xx地方"
- 输入: `"我想去杭州"`
- 输出: `"我想到杭州地方"`

#### 规则 3: 附近搜索优化
- 输入: `"我想喝附近的咖啡"`
- 输出: `"我想喝附近的咖啡"` (保持原样，但会触发当前位置获取)

### 使用示例
```python
from text_optimizer import optimize_text

text = "我想从北京到上海"
optimized, was_optimized = optimize_text(text)
print(f"优化结果: {optimized}")  # 输出: "我想到上海地方"
print(f"是否优化: {was_optimized}")  # 输出: True
```

### 文件说明
- `text_optimizer.py` - 文本优化模块
  - `TextOptimizer` - 文本优化类
  - `optimize_text()` - 便捷函数

## 3. 地理位置获取功能

### 功能描述
能够获取程序运行时的当前地理位置，支持多种定位方式。

### 支持的定位方式

#### 方式 1: 高德地图 IP 定位 (推荐)
基于 IP 地址使用高德地图API获取精确的地理位置。

**配置**:
```bash
export AMAP_API_KEY="your-amap-api-key"
```

**优点**:
- 精确度高
- 返回详细的省份、城市信息
- 与现有高德地图服务集成良好

#### 方式 2: IP 地址定位 (备用)
使用第三方 IP 定位服务 (ipapi.co) 获取大致位置。

**优点**:
- 无需配置
- 自动作为备用方案
- 覆盖全球

### 使用方法

#### 直接调用
```python
from location_service import get_current_location

# 获取当前位置
location = await get_current_location()
print(f"当前位置: {location['city']}")
print(f"坐标: ({location['longitude']}, {location['latitude']})")
```

#### 在导航请求中自动触发
当用户输入包含以下关键词时，系统会自动获取当前位置：
- "附近"
- "当前位置"
- "我的位置"
- 或者只提供目的地时

**示例**:
```
输入: "我想喝附近的咖啡"
→ 系统自动检测到"附近"
→ 获取当前地理位置
→ 将当前位置作为起点
```

### 文件说明
- `location_service.py` - 地理位置服务模块
  - `LocationService` - 位置服务类
  - `get_current_location()` - 便捷函数

### 返回数据格式
```python
{
    "name": "北京",
    "longitude": 116.397128,
    "latitude": 39.916527,
    "province": "北京市",
    "city": "北京市",
    "formatted_address": "北京市北京市"
}
```

## 集成示例

### 完整使用流程

1. **配置环境变量**
```bash
# AI 提供商 (二选一)
export AI_PROVIDER="openai"
export OPENAI_API_KEY="your-openai-key"
export OPENAI_BASE_URL="https://api.qiniu.com/v1"

# 七牛云语音识别
export QINIU_SPEECH_API_KEY="your-qiniu-speech-key"

# 高德地图 (用于地理位置和导航)
export AMAP_API_KEY="your-amap-key"
```

2. **运行程序**
```bash
python main.py
```

3. **选择语音输入**
```
请选择输入方式:
1. 文本输入
2. 语音输入 (本地/Google)
3. 七牛云语音输入
请选择 (1/2/3): 3
```

4. **语音输入**
```
请说出您的导航请求（例如：'从北京到上海'，'10秒内无输入将超时）...
[说话: "我想喝附近的咖啡"]
```

5. **自动处理**
- 七牛云API识别语音 → "我想喝附近的咖啡"
- 文本优化 → 保持原样（检测到"附近"）
- AI解析 → 起点: "当前位置", 终点: "咖啡"
- 自动获取当前地理位置
- 查询咖啡店坐标
- 在浏览器中打开导航

## 技术架构

```
用户输入
  ↓
[语音识别层]
  ├─ 本地识别 (Vosk)
  ├─ Google 语音识别
  └─ 七牛云语音识别 ✨ NEW
  ↓
[文本优化层] ✨ NEW
  └─ 规则引擎优化文本
  ↓
[AI 解析层]
  └─ 提取起点和终点
  ↓
[地理位置层] ✨ NEW
  ├─ 检测"当前位置"关键词
  ├─ 高德 IP 定位
  └─ 第三方 IP 定位
  ↓
[坐标查询层]
  └─ 高德地图 API / MCP Server
  ↓
[导航层]
  └─ 浏览器打开导航
```

## 依赖项

新增依赖已添加到 `requirements.txt`:
```
requests>=2.31.0
```

所有其他依赖保持不变。

## 故障排除

### 七牛云语音识别

**问题**: 初始化失败
```
七牛云语音识别初始化失败: QINIU_SPEECH_API_KEY not set
```
**解决方案**: 设置环境变量 `QINIU_SPEECH_API_KEY`

**问题**: API 返回错误
```
七牛云API返回错误: 401
```
**解决方案**: 检查 API Key 是否正确，确认账户权限和配额

### 地理位置获取

**问题**: 无法获取当前位置
```
⚠️  无法获取当前位置，使用默认位置
```
**解决方案**: 
1. 检查网络连接
2. 设置 `AMAP_API_KEY` 使用高德地图定位
3. 系统会自动使用默认位置（北京）

### 文本优化

文本优化是纯本地处理，不依赖外部服务，不会出现故障。

## 未来扩展

可能的扩展方向：
- [ ] 支持更多语音识别服务（讯飞、百度等）
- [ ] 更智能的文本优化规则（基于机器学习）
- [ ] GPS 定位支持（移动设备）
- [ ] 位置缓存机制
- [ ] 多语言支持
