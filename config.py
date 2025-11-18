"""项目配置管理"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# 图床配置
IMAGE_API_URL = os.getenv('IMAGE_API_URL', 'http://81.68.170.234/api/index.php')
IMAGE_API_TOKEN = os.getenv('IMAGE_API_TOKEN', '1c17b11693cb5ec63859b091c5b9c1b2')
IMAGE_TARGET_WIDTH = int(os.getenv('IMAGE_TARGET_WIDTH', '800'))
IMAGE_TARGET_HEIGHT = int(os.getenv('IMAGE_TARGET_HEIGHT', '400'))

# OpenAI 配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')

# 数据目录
DATA_DIR = Path(__file__).parent / 'data'
OUTPUT_DIR = DATA_DIR / 'output'

# 确保目录存在
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
