"""
日志工具 - 支持将日志同时输出到控制台和文件
"""
import os
import sys
from datetime import datetime
from typing import Optional
import io


class LoggerUtil:
    """日志工具类，支持同时输出到控制台和文件"""
    
    _instances = {}  # 存储不同玩家的日志实例
    
    def __init__(self, player_name: str = "default", log_dir: str = ".\\log"):
        """
        初始化日志工具
        
        Args:
            player_name: 玩家名称，用于创建独立的日志文件
            log_dir: 日志目录
        """
        self.player_name = player_name
        self.log_dir = log_dir
        self.log_file = None
        self._setup_log_file()
    
    def _setup_log_file(self):
        """设置日志文件"""
        # 确保日志目录存在
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)
        
        # 创建日志文件名：player_name_YYYYMMDD_HHMMSS.log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 清理玩家名称中的特殊字符，避免文件名问题
        safe_name = "".join(c for c in self.player_name if c.isalnum() or c in ('_', '-'))
        log_filename = f"{safe_name}_{timestamp}.log"
        log_path = os.path.join(self.log_dir, log_filename)
        
        # 打开日志文件，使用追加模式
        self.log_file = open(log_path, 'a', encoding='utf-8')
        
        # 写入开始标记
        self.log_file.write(f"\n{'='*80}\n")
        self.log_file.write(f"日志开始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.log_file.write(f"玩家: {self.player_name}\n")
        self.log_file.write(f"{'='*80}\n\n")
        self.log_file.flush()
    
    def log(self, message: str, print_to_console: bool = True):
        """
        记录日志
        
        Args:
            message: 日志消息
            print_to_console: 是否同时输出到控制台
        """
        # 添加时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        # 输出到控制台（如果启用）
        if print_to_console:
            # 直接输出原始消息（保持原有的print格式，包括emoji和颜色）
            print(message, end='', flush=True)
        
        # 写入文件（去除ANSI颜色代码）
        if self.log_file:
            # 移除ANSI转义序列（颜色代码）
            clean_message = self._remove_ansi_codes(message)
            self.log_file.write(f"[{timestamp}] {clean_message}\n")
            self.log_file.flush()
    
    def log_line(self, message: str, print_to_console: bool = True):
        """
        记录单行日志（自动添加换行）
        
        Args:
            message: 日志消息
            print_to_console: 是否同时输出到控制台
        """
        self.log(message + "\n", print_to_console)
    
    def _remove_ansi_codes(self, text: str) -> str:
        """
        移除ANSI转义序列（颜色代码）
        
        Args:
            text: 包含ANSI代码的文本
            
        Returns:
            清理后的文本
        """
        import re
        # 移除所有ANSI转义序列
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def close(self):
        """关闭日志文件"""
        if self.log_file:
            self.log_file.write(f"\n{'='*80}\n")
            self.log_file.write(f"日志结束: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.log_file.write(f"{'='*80}\n\n")
            self.log_file.close()
            self.log_file = None
    
    @classmethod
    def get_logger(cls, player_name: str = "default", log_dir: str = ".\\log") -> 'LoggerUtil':
        """
        获取或创建日志实例（单例模式）
        
        Args:
            player_name: 玩家名称
            log_dir: 日志目录
            
        Returns:
            LoggerUtil实例
        """
        key = f"{player_name}_{log_dir}"
        if key not in cls._instances:
            cls._instances[key] = cls(player_name, log_dir)
        return cls._instances[key]
    
    @classmethod
    def close_all(cls):
        """关闭所有日志实例"""
        for logger in cls._instances.values():
            logger.close()
        cls._instances.clear()
    
    def __del__(self):
        """析构函数，确保文件关闭"""
        try:
            self.close()
        except:
            pass  # 忽略Python关闭时的异常


class TeeOutput:
    """同时输出到控制台和日志文件的输出类"""
    
    def __init__(self, logger: LoggerUtil, original_stdout):
        self.logger = logger
        self.original_stdout = original_stdout
    
    def write(self, text: str):
        """写入文本，同时输出到控制台和日志文件"""
        # 输出到原始stdout
        self.original_stdout.write(text)
        self.original_stdout.flush()
        
        # 写入日志文件（移除ANSI代码）
        if self.logger and self.logger.log_file:
            clean_text = self.logger._remove_ansi_codes(text)
            self.logger.log_file.write(clean_text)
            self.logger.log_file.flush()
    
    def flush(self):
        """刷新输出"""
        if self.original_stdout:
            self.original_stdout.flush()
        if self.logger and self.logger.log_file:
            self.logger.log_file.flush()

