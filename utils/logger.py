"""日志系统配置模块"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器（终端输出）"""

    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'

    def format(self, record):
        """格式化日志记录"""
        # 添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{self.BOLD}{levelname}{self.RESET}"
            record.msg = f"{self.COLORS[levelname.split('[')[0]]}{record.msg}{self.RESET}"

        return super().format(record)


class ScraperLogger:
    """爬虫日志管理器"""

    def __init__(
        self,
        name: str = "scraper",
        log_dir: str = "logs",
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        enable_color: bool = True
    ):
        """
        初始化日志系统

        Args:
            name: 日志记录器名称
            log_dir: 日志文件目录
            console_level: 控制台日志级别
            file_level: 文件日志级别
            max_bytes: 单个日志文件最大字节数
            backup_count: 保留的日志文件数量
            enable_color: 是否启用控制台颜色
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 创建日志记录器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # 避免重复添加处理器
        if self.logger.handlers:
            return

        # 1. 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)

        if enable_color and sys.stdout.isatty():
            console_format = '%(levelname)s | %(message)s'
            console_handler.setFormatter(ColoredFormatter(console_format))
        else:
            console_format = '%(asctime)s | %(levelname)-8s | %(message)s'
            console_handler.setFormatter(logging.Formatter(
                console_format,
                datefmt='%H:%M:%S'
            ))

        self.logger.addHandler(console_handler)

        # 2. 文件处理器 - 详细日志
        log_file = self.log_dir / f"{name}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(file_level)
        file_format = '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s'
        file_handler.setFormatter(logging.Formatter(file_format))
        self.logger.addHandler(file_handler)

        # 3. 每日日志文件处理器
        daily_log_file = self.log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        daily_handler = logging.FileHandler(daily_log_file, encoding='utf-8')
        daily_handler.setLevel(logging.INFO)
        daily_handler.setFormatter(logging.Formatter(file_format))
        self.logger.addHandler(daily_handler)

        # 4. 错误日志单独文件
        error_log_file = self.log_dir / f"{name}_error.log"
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_format = '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(funcName)s\n%(message)s\n'
        error_handler.setFormatter(logging.Formatter(error_format))
        self.logger.addHandler(error_handler)

    def get_logger(self) -> logging.Logger:
        """获取日志记录器"""
        return self.logger

    def debug(self, message: str, *args, **kwargs):
        """记录调试信息"""
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """记录一般信息"""
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """记录警告信息"""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """记录错误信息"""
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """记录严重错误"""
        self.logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        """记录异常（包含堆栈跟踪）"""
        self.logger.exception(message, *args, **kwargs)


# 全局日志实例
_global_logger: Optional[ScraperLogger] = None


def setup_logger(
    name: str = "scraper",
    log_dir: str = "logs",
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    enable_color: bool = True
) -> ScraperLogger:
    """
    设置全局日志系统

    Args:
        name: 日志记录器名称
        log_dir: 日志文件目录
        console_level: 控制台日志级别
        file_level: 文件日志级别
        enable_color: 是否启用控制台颜色

    Returns:
        ScraperLogger: 日志管理器实例
    """
    global _global_logger
    _global_logger = ScraperLogger(
        name=name,
        log_dir=log_dir,
        console_level=console_level,
        file_level=file_level,
        enable_color=enable_color
    )
    return _global_logger


def get_logger() -> logging.Logger:
    """
    获取全局日志记录器

    Returns:
        logging.Logger: 日志记录器
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = setup_logger()
    return _global_logger.get_logger()


# 便捷的日志函数
def debug(message: str, *args, **kwargs):
    """记录调试信息"""
    get_logger().debug(message, *args, **kwargs)


def info(message: str, *args, **kwargs):
    """记录一般信息"""
    get_logger().info(message, *args, **kwargs)


def warning(message: str, *args, **kwargs):
    """记录警告信息"""
    get_logger().warning(message, *args, **kwargs)


def error(message: str, *args, **kwargs):
    """记录错误信息"""
    get_logger().error(message, *args, **kwargs)


def critical(message: str, *args, **kwargs):
    """记录严重错误"""
    get_logger().critical(message, *args, **kwargs)


def exception(message: str, *args, **kwargs):
    """记录异常（包含堆栈跟踪）"""
    get_logger().exception(message, *args, **kwargs)


# 使用示例
if __name__ == "__main__":
    # 设置日志
    logger = setup_logger("test", enable_color=True)

    # 测试不同级别的日志
    logger.info("这是一条普通信息")
    logger.debug("这是调试信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")

    try:
        1 / 0
    except Exception as e:
        logger.exception("捕获到异常")

    print(f"\n日志文件保存在: logs/")
