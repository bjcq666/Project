#!/usr/bin/env python3
"""
Qiniu Cloud Speech-to-Text Module
Provides speech-to-text capability using Qiniu Cloud API
"""

import asyncio
import json
import httpx
import os
from typing import Optional
import speech_recognition as sr


class QiniuSpeechRecognizer:
    def __init__(self, api_key: str = None, api_url: str = None):
        self.api_key = api_key or os.getenv("QINIU_SPEECH_API_KEY")
        self.api_url = api_url or os.getenv("QINIU_SPEECH_API_URL", "https://api.qiniu.com/v1/speech/recognize")
        
        if not self.api_key:
            raise ValueError("QINIU_SPEECH_API_KEY not set")
        
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
    
    def _adjust_for_noise(self):
        """调整识别器以适应环境噪音"""
        with self.microphone as source:
            print("正在调整麦克风以适应环境噪音，请稍候...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("麦克风调整完成!")
    
    async def recognize_speech(self, timeout: int = 10) -> Optional[str]:
        """
        使用七牛云API识别语音输入
        
        Args:
            timeout: 识别超时时间（秒）
        
        Returns:
            识别出的文本，识别失败则返回None
        """
        loop = asyncio.get_event_loop()
        
        try:
            await loop.run_in_executor(None, self._adjust_for_noise)
            
            print(f"\n请说出您的导航请求（例如：'从北京到上海'，'{timeout}秒内无输入将超时）...")
            
            def capture_speech():
                with self.microphone as source:
                    try:
                        audio = self.recognizer.listen(source, timeout=timeout)
                        return audio
                    except sr.WaitTimeoutError:
                        print("语音输入超时，请重试。")
                        return None
            
            audio_data = await asyncio.wait_for(
                loop.run_in_executor(None, capture_speech),
                timeout=timeout + 2
            )
            
            if not audio_data:
                return None
            
            print("正在使用七牛云API识别语音...")
            
            return await self._recognize_with_qiniu(audio_data)
            
        except asyncio.TimeoutError:
            print("语音识别过程超时。")
            return None
        except Exception as e:
            print(f"语音识别过程中发生错误: {e}")
            return None
    
    async def _recognize_with_qiniu(self, audio_data) -> Optional[str]:
        """使用七牛云API识别语音"""
        try:
            audio_bytes = audio_data.get_wav_data()
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "audio/wav"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    content=audio_bytes,
                    params={
                        "language": "zh-CN",
                        "format": "wav"
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    text = result.get("text", "")
                    
                    if text:
                        print(f"七牛云识别结果: {text}")
                        return text
                    else:
                        print("七牛云API未能识别出有效内容。")
                        return None
                else:
                    print(f"七牛云API返回错误: {response.status_code}")
                    print(f"错误信息: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"调用七牛云API时发生错误: {e}")
            return None


async def get_qiniu_voice_input() -> Optional[str]:
    """获取七牛云语音输入的便捷函数"""
    try:
        recognizer = QiniuSpeechRecognizer()
        return await recognizer.recognize_speech()
    except ValueError as e:
        print(f"七牛云语音识别初始化失败: {e}")
        print("请设置 QINIU_SPEECH_API_KEY 环境变量")
        return None
