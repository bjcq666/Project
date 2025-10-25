#!/usr/bin/env python3
"""
Text Optimization Module
Optimizes navigation text requests for better user experience
"""

import re
from typing import Tuple, Optional


class TextOptimizer:
    def __init__(self):
        self.patterns = [
            (r'我想从(.+?)到(.+?)$', self._optimize_from_to),
            (r'从(.+?)到(.+?)$', self._optimize_from_to),
            (r'我要从(.+?)去(.+?)$', self._optimize_from_to),
            (r'我想到(.+?)地方$', self._optimize_to_place),
            (r'我想去(.+?)$', self._optimize_go_to),
            (r'我想(喝|吃|找|看)附近的(.+?)$', self._optimize_nearby),
        ]
    
    def optimize(self, text: str) -> Tuple[str, bool]:
        """
        优化文本请求
        
        Args:
            text: 原始文本
        
        Returns:
            (优化后的文本, 是否进行了优化)
        """
        text = text.strip()
        
        for pattern, handler in self.patterns:
            match = re.match(pattern, text)
            if match:
                optimized = handler(match, text)
                if optimized and optimized != text:
                    return optimized, True
        
        return text, False
    
    def _optimize_from_to(self, match, original: str) -> str:
        """优化 '从xx到xx' 格式"""
        start = match.group(1).strip()
        end = match.group(2).strip()
        
        return f"我想到{end}地方"
    
    def _optimize_to_place(self, match, original: str) -> str:
        """优化 '我想到xx地方' 格式（已是优化格式，不需要修改）"""
        return original
    
    def _optimize_go_to(self, match, original: str) -> str:
        """优化 '我想去xx' 格式"""
        destination = match.group(1).strip()
        return f"我想到{destination}地方"
    
    def _optimize_nearby(self, match, original: str) -> str:
        """优化 '我想喝/吃/找附近的xx' 格式（需要添加当前位置）"""
        action = match.group(1)
        target = match.group(2).strip()
        
        return f"我想{action}附近的{target}"


def optimize_text(text: str) -> Tuple[str, bool]:
    """
    便捷函数：优化文本
    
    Args:
        text: 原始文本
    
    Returns:
        (优化后的文本, 是否进行了优化)
    """
    optimizer = TextOptimizer()
    return optimizer.optimize(text)
