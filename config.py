"""项目配置管理"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# ==================== 图床配置 ====================
IMAGE_API_URL = os.getenv('IMAGE_API_URL', 'http://81.68.170.234/api/index.php')
IMAGE_API_TOKEN = os.getenv('IMAGE_API_TOKEN', '1c17b11693cb5ec63859b091c5b9c1b2')
IMAGE_TARGET_WIDTH = int(os.getenv('IMAGE_TARGET_WIDTH', '800'))
IMAGE_TARGET_HEIGHT = int(os.getenv('IMAGE_TARGET_HEIGHT', '400'))

# ==================== OpenAI 配置 ====================
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')

# ==================== 目录配置 ====================
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_DIR = DATA_DIR / 'output'
INPUT_DIR = DATA_DIR / 'input'
LOGS_DIR = PROJECT_ROOT / 'logs'

# 确保目录存在
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
INPUT_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ==================== 爬虫URL配置 ====================
# 默认爬取的分类URL
DEFAULT_CATEGORY_URL = os.getenv(
    'SCRAPER_CATEGORY_URL',
    'https://www.hollandandbarrett.com/shop/vitamins-supplements/condition/hair-skin-nails/'
)

# ==================== 输出文件配置 ====================
# 基本信息输出文件
OUTPUT_BASIC_CSV = OUTPUT_DIR / os.getenv('OUTPUT_BASIC_FILE', 'products_basic.csv')
# 完整信息输出文件
OUTPUT_COMPLETE_CSV = OUTPUT_DIR / os.getenv('OUTPUT_COMPLETE_FILE', 'products_complete.csv')
# 失败产品记录文件
OUTPUT_FAILED_JSON = OUTPUT_DIR / os.getenv('OUTPUT_FAILED_FILE', 'failed_products.json')
# 多页爬取输出文件模板（会根据产品类型动态生成）
OUTPUT_MULTIPAGE_TEMPLATE = 'products_multi_page_{product_type}.csv'

# CSV字段名配置
CSV_FIELDNAMES_BASIC = ['brand', 'name', 'price', 'image', 'url']
CSV_FIELDNAMES_COMPLETE = [
    '产品名称', '产品亮点', '产品价格', '产品品牌',
    '产品图', '产品描述', '产品类型', '作用部位',
    '用法说明', '营养成分', '配料表', 'URL'
]

# ==================== Chrome浏览器配置 ====================
# User-Agent
CHROME_USER_AGENT = os.getenv(
    'CHROME_USER_AGENT',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)

# 是否启用headless模式
CHROME_HEADLESS = os.getenv('CHROME_HEADLESS', 'true').lower() == 'true'

# 页面加载策略: normal, eager, none
CHROME_PAGE_LOAD_STRATEGY = os.getenv('CHROME_PAGE_LOAD_STRATEGY', 'eager')

# Chrome选项列表
CHROME_OPTIONS = [
    '--disable-blink-features=AutomationControlled',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-extensions',
    '--disable-software-rasterizer',
    '--disable-features=VizDisplayCompositor',
    '--log-level=3',
]

# 如果启用headless，添加headless选项
if CHROME_HEADLESS:
    CHROME_OPTIONS.insert(0, '--headless=new')

# ==================== 爬虫行为配置 ====================
# 页面加载超时（秒）
PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '60'))
# 脚本执行超时（秒）
SCRIPT_TIMEOUT = int(os.getenv('SCRIPT_TIMEOUT', '60'))
# 页面等待时间（秒）
PAGE_WAIT_TIME = int(os.getenv('PAGE_WAIT_TIME', '3'))
# Cookie处理超时（秒）
COOKIE_TIMEOUT = int(os.getenv('COOKIE_TIMEOUT', '5'))

# Cookie弹窗选择器
COOKIE_SELECTORS = [
    "//button[contains(text(), 'Yes I Accept')]",
    "//button[contains(text(), 'Accept')]",
    "//button[@id='onetrust-accept-btn-handler']",
]

# ==================== 并行爬取配置 ====================
# 默认并发线程数
DEFAULT_MAX_WORKERS = int(os.getenv('PARALLEL_MAX_WORKERS', '3'))
# 最大并发线程数限制
MAX_WORKERS_LIMIT = int(os.getenv('MAX_WORKERS_LIMIT', '10'))
# 重试次数
RETRY_TIMES = int(os.getenv('RETRY_TIMES', '3'))
# 请求延迟范围（秒）
REQUEST_DELAY_MIN = int(os.getenv('REQUEST_DELAY_MIN', '2'))
REQUEST_DELAY_MAX = int(os.getenv('REQUEST_DELAY_MAX', '4'))
# 批次写入大小
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '100'))

# ==================== 多页爬取配置 ====================
# 默认最大爬取页数（None表示不限制）
DEFAULT_MAX_PAGES = None
# 是否启用断点续传
ENABLE_RESUME = os.getenv('ENABLE_RESUME', 'true').lower() == 'true'
# 断点续传时是否自动继续（仅在非交互式模式下生效）
AUTO_RESUME = os.getenv('AUTO_RESUME', 'true').lower() == 'true'

# ==================== 交互式选项配置（支持非交互式运行） ====================
# 是否启用交互式模式（false时使用下面的默认配置）
INTERACTIVE_MODE = os.getenv('INTERACTIVE_MODE', 'true').lower() == 'true'

# 爬取模式配置
# 1 = 单页模式, 2 = 多页模式, 3 = 限制页数模式
SCRAPE_MODE = int(os.getenv('SCRAPE_MODE', '1'))
# 限制页数（当SCRAPE_MODE=3时使用）
MAX_PAGES_LIMIT = int(os.getenv('MAX_PAGES_LIMIT', '5'))

# 是否爬取详情页
SCRAPE_DETAILS = os.getenv('SCRAPE_DETAILS', 'false').lower() == 'true'
# 爬取详情页的最大产品数量（None表示全部）
MAX_PRODUCTS_TO_SCRAPE = os.getenv('MAX_PRODUCTS_TO_SCRAPE', None)
if MAX_PRODUCTS_TO_SCRAPE is not None and MAX_PRODUCTS_TO_SCRAPE.strip():
    MAX_PRODUCTS_TO_SCRAPE = int(MAX_PRODUCTS_TO_SCRAPE)
else:
    MAX_PRODUCTS_TO_SCRAPE = None

# 详情页爬取模式
# 1 = 顺序模式, 2 = 并行模式
DETAIL_SCRAPE_MODE = int(os.getenv('DETAIL_SCRAPE_MODE', '2'))

# 是否运行翻译
RUN_TRANSLATION = os.getenv('RUN_TRANSLATION', 'true').lower() == 'true'
# 是否运行图片处理
RUN_IMAGE_PROCESSING = os.getenv('RUN_IMAGE_PROCESSING', 'true').lower() == 'true'

# ==================== 产品选择器配置 ====================
# 产品卡片选择器
PRODUCT_CARD_SELECTOR = '[data-test="product-card"]'
# 产品卡片选择器（备用）
PRODUCT_CARD_SELECTOR_ALT = '[data-testid="product-card"]'
# 品牌选择器
BRAND_SELECTOR = '[data-test="product-card-brand-name"]'
BRAND_SELECTOR_ALT = '.ProductCard-module_productBrand__-rFtT'
# 标题选择器
TITLE_SELECTOR = '[data-test="product-card-title"]'
TITLE_SELECTOR_ALT = '.ProductCard-module_title__ytKYE'
# 价格选择器
PRICE_SELECTOR = '[data-test="product-card-price"]'
PRICE_SELECTOR_ALT = '.MppProductCardPrice-module_price__bold__BpYBE'
# 图片选择器
IMAGE_SELECTOR = '[data-test="product-image"]'
IMAGE_SELECTOR_ALT = '.ProductCard-module_productImage__9bfwO'


def get_chrome_options():
    """获取配置好的Chrome选项"""
    from selenium import webdriver

    options = webdriver.ChromeOptions()

    # 添加实验性选项
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # 添加所有配置的选项
    for option in CHROME_OPTIONS:
        options.add_argument(option)

    # 设置User-Agent
    options.add_argument(f'user-agent={CHROME_USER_AGENT}')

    # 设置页面加载策略
    options.page_load_strategy = CHROME_PAGE_LOAD_STRATEGY

    return options


def get_output_path(product_type: str = None, output_type: str = 'basic') -> Path:
    """
    获取输出文件路径

    Args:
        product_type: 产品类型
        output_type: 输出类型 ('basic', 'complete', 'failed', 'multipage')

    Returns:
        输出文件路径
    """
    if output_type == 'basic':
        return OUTPUT_BASIC_CSV
    elif output_type == 'complete':
        return OUTPUT_COMPLETE_CSV
    elif output_type == 'failed':
        return OUTPUT_FAILED_JSON
    elif output_type == 'multipage' and product_type:
        filename = OUTPUT_MULTIPAGE_TEMPLATE.format(product_type=product_type)
        return OUTPUT_DIR / filename
    else:
        raise ValueError(f"未知的输出类型: {output_type}")


def get_product_type_from_url(url: str) -> str:
    """从URL提取产品类型"""
    try:
        return url.split("/shop/")[1].split("/")[0]
    except (IndexError, AttributeError):
        return "unknown"
