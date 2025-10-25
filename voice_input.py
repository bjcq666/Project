"""
七牛实时语音识别模块
文档: https://developer.qiniu.com/dora/8084/real-time-speech-recognition
"""

import json
import base64
import hmac
import hashlib
import time
from typing import Optional, Dict, Any
import httpx


class QiniuVoiceRecognizer:
    """七牛实时语音识别客户端"""
    
    def __init__(self, access_key: str, secret_key: str):
        """
        初始化七牛语音识别客户端
        
        Args:
            access_key: 七牛 Access Key
            secret_key: 七牛 Secret Key
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.api_url = "https://ap-gate-z0.qiniuapi.com/asr/v1/audio"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _generate_token(self, method: str, path: str, body: bytes = b"") -> str:
        """
        生成七牛认证 Token
        
        Args:
            method: HTTP 方法
            path: 请求路径
            body: 请求体
            
        Returns:
            认证 Token
        """
        data = f"{method} {path}\nHost: ap-gate-z0.qiniuapi.com\nContent-Type: application/json\n\n"
        
        if body:
            data += body.decode("utf-8")
        
        sign = hmac.new(
            self.secret_key.encode("utf-8"),
            data.encode("utf-8"),
            hashlib.sha1
        ).digest()
        
        encoded_sign = base64.urlsafe_b64encode(sign).decode("utf-8")
        
        return f"Qiniu {self.access_key}:{encoded_sign}"
    
    async def recognize_audio_file(
        self,
        audio_data: bytes,
        audio_format: str = "wav",
        sample_rate: int = 16000,
        language: str = "zh-CN"
    ) -> str:
        """
        识别音频文件
        
        Args:
            audio_data: 音频数据（字节）
            audio_format: 音频格式 (wav, mp3, pcm)
            sample_rate: 采样率 (8000 或 16000)
            language: 语言 (zh-CN 或 en-US)
            
        Returns:
            识别结果文本
        """
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")
        
        request_body = {
            "audio": audio_base64,
            "format": audio_format,
            "rate": sample_rate,
            "language": language
        }
        
        body_bytes = json.dumps(request_body).encode("utf-8")
        
        token = self._generate_token("POST", "/asr/v1/audio", body_bytes)
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        try:
            response = await self.client.post(
                self.api_url,
                content=body_bytes,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "result" in result and len(result["result"]) > 0:
                return result["result"][0].get("text", "")
            
            raise Exception("语音识别结果为空")
        
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"语音识别失败: {str(e)}")
    
    async def recognize_url(
        self,
        audio_url: str,
        audio_format: str = "wav",
        sample_rate: int = 16000,
        language: str = "zh-CN"
    ) -> str:
        """
        识别在线音频文件
        
        Args:
            audio_url: 音频文件 URL
            audio_format: 音频格式
            sample_rate: 采样率
            language: 语言
            
        Returns:
            识别结果文本
        """
        async with httpx.AsyncClient() as client:
            audio_response = await client.get(audio_url)
            audio_response.raise_for_status()
            audio_data = audio_response.content
        
        return await self.recognize_audio_file(audio_data, audio_format, sample_rate, language)


class LocalMicrophoneRecorder:
    """本地麦克风录音器（使用 sounddevice）"""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        """
        初始化麦克风录音器
        
        Args:
            sample_rate: 采样率
            channels: 声道数
        """
        self.sample_rate = sample_rate
        self.channels = channels
    
    def record_audio(self, duration: int = 5) -> bytes:
        """
        录制音频
        
        Args:
            duration: 录制时长（秒）
            
        Returns:
            音频数据（WAV 格式）
        """
        try:
            import sounddevice as sd
            import numpy as np
            import wave
            import io
            
            print(f"🎤 开始录音（{duration} 秒）...")
            
            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.int16
            )
            sd.wait()
            
            print("✅ 录音完成")
            
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio.tobytes())
            
            return buffer.getvalue()
        
        except ImportError:
            raise Exception(
                "sounddevice 未安装。请运行: pip install sounddevice numpy"
            )
        except Exception as e:
            raise Exception(f"录音失败: {str(e)}")


class MockVoiceRecognizer:
    """模拟语音识别器 - 用于开发测试"""
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def recognize_audio_file(
        self,
        audio_data: bytes,
        audio_format: str = "wav",
        sample_rate: int = 16000,
        language: str = "zh-CN"
    ) -> str:
        """模拟语音识别"""
        print("⚠️  使用 Mock 语音识别模式")
        return "从北京到上海"


def create_voice_recognizer(config: Dict[str, Any]):
    """
    创建语音识别器
    
    Args:
        config: 配置字典
        
    Returns:
        QiniuVoiceRecognizer 或 MockVoiceRecognizer 实例
    """
    qiniu_config = config.get("qiniu", {})
    access_key = qiniu_config.get("accessKey", "")
    secret_key = qiniu_config.get("secretKey", "")
    
    if not access_key or not secret_key or "YOUR_QINIU" in access_key:
        print("⚠️  未配置七牛密钥，语音识别将使用 Mock 模式")
        return MockVoiceRecognizer()
    
    print("✅ 初始化七牛语音识别...")
    return QiniuVoiceRecognizer(access_key, secret_key)
