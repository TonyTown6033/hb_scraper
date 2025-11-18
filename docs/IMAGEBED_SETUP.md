# 图床配置指南 🖼️

## 问题诊断

### 当前状态 ⚠️

经检查，当前配置的图床API返回 **502 Bad Gateway** 错误：

```
API URL: http://81.68.170.234/api/index.php
状态: 502 Bad Gateway (服务不可用)
```

**可能原因**:
- 图床服务已关闭或迁移
- 服务器配置错误
- 网络连接问题

### 快速检查

运行诊断脚本：

```bash
uv run python scripts/check_imagebed.py
```

这会检查：
- API连接性
- 上传功能
- 并提供替代方案

## 解决方案

### 方案1: 使用其他图床服务（推荐）

以下是一些可靠的图床服务：

#### ImgBB
```
网站: https://imgbb.com
优点: 免费、稳定、有API
限制: 需要注册获取API key
```

#### SM.MS
```
网站: https://sm.ms
优点: 免费、中文、有API
限制: 需要注册获取API token
```

#### 路过图床
```
网站: https://imgse.com
优点: 国内访问快
限制: 可能有上传限制
```

### 方案2: 自建图床（最佳长期方案）

#### EasyImage 2.0（推荐）

**优点**:
- 开源免费
- 安装简单
- 支持多种存储
- 当前代码已适配此API

**安装步骤**:

1. **环境要求**:
   - PHP 7.4+
   - MySQL 5.6+
   - Web服务器 (Nginx/Apache)

2. **下载安装**:
```bash
git clone https://github.com/icret/EasyImages2.0.git
cd EasyImages2.0
```

3. **配置**:
   - 访问 `http://your-domain.com/install.php`
   - 按照向导完成安装
   - 在后台获取API Token

4. **配置爬虫**:
```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env
nano .env
```

修改为:
```env
IMAGE_API_URL=http://your-domain.com/api/index.php
IMAGE_API_TOKEN=your_token_here
```

#### Lsky Pro

```
项目: https://github.com/lsky-org/lsky-pro
特点: 功能强大、界面美观
```

#### Chevereto

```
项目: https://chevereto.com
特点: 专业级、功能全面
注意: 收费版功能更多
```

### 方案3: 使用云存储服务

#### 阿里云OSS

**步骤**:
1. 开通OSS服务
2. 创建Bucket
3. 获取AccessKey
4. 修改代码使用OSS SDK

**示例代码**:
```python
import oss2

auth = oss2.Auth('your-access-key-id', 'your-access-key-secret')
bucket = oss2.Bucket(auth, 'your-endpoint', 'your-bucket')

# 上传图片
bucket.put_object('image.png', image_data)
url = f"https://your-bucket.oss-cn-hangzhou.aliyuncs.com/image.png"
```

#### 七牛云

```
文档: https://developer.qiniu.com
SDK: pip install qiniu
```

### 方案4: 保留原始URL（临时方案）

如果暂时不需要处理图片，可以保留原始URL：

修改 `main.py`:
```python
# 注释掉图片处理
# translate_main()
# image_post_precessor()  # 暂时不处理图片
```

## 配置步骤

### 1. 创建配置文件

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置
nano .env
```

### 2. 修改配置

```env
# 图床API地址 - 修改为你的API地址
IMAGE_API_URL=http://your-image-host.com/api/index.php

# 图床API Token - 修改为你的Token
IMAGE_API_TOKEN=your_token_here

# 图片尺寸（可选，默认800x400）
IMAGE_TARGET_WIDTH=800
IMAGE_TARGET_HEIGHT=400
```

### 3. 测试配置

```bash
# 运行诊断脚本
uv run python scripts/check_imagebed.py
```

应该看到：
```
============================================================
✓ 图床服务正常，可以使用！
============================================================
```

### 4. 开始使用

```bash
# 处理CSV中的图片
uv run python scripts/process_csv_images.py

# 或在main.py中自动调用
uv run python main.py
```

## 代码适配指南

### 如果需要适配其他图床API

当前代码使用的是EasyImage API格式，如果你的图床API不同，需要修改 `utils/image_processor.py`:

```python
def upload_to_imagebed(self, image_data: bytes, filename: str = "product.png"):
    """上传图片到图床"""
    try:
        # 原始代码（EasyImage格式）
        files = {"image": (filename, image_data, "image/png")}
        data = {"token": self.token}
        response = self.client.post(self.api_url, files=files, data=data)

        # 根据你的图床API修改这里
        if response.status_code == 200:
            result = response.json()
            if result.get("result") == "success":
                return result.get("url")

        return None
    except Exception as e:
        print(f"上传出错: {e}")
        return None
```

### ImgBB API示例

```python
def upload_to_imgbb(self, image_data: bytes):
    """上传到ImgBB"""
    import base64

    image_base64 = base64.b64encode(image_data).decode()

    data = {
        'key': self.token,  # ImgBB使用key而不是token
        'image': image_base64
    }

    response = self.client.post(
        'https://api.imgbb.com/1/upload',
        data=data
    )

    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            return result['data']['url']

    return None
```

### SM.MS API示例

```python
def upload_to_smms(self, image_data: bytes, filename: str):
    """上传到SM.MS"""
    files = {'smfile': (filename, image_data, 'image/png')}
    headers = {'Authorization': self.token}

    response = self.client.post(
        'https://sm.ms/api/v2/upload',
        files=files,
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            return result['data']['url']

    return None
```

## 常见问题

### Q: 如何知道我的图床API格式？

A: 查看图床的API文档或后台说明。通常包含：
- API地址
- 认证方式（token/key）
- 请求格式（form-data/json）
- 响应格式

### Q: 可以不上传图床，只处理图片吗？

A: 可以，修改 `utils/image_processor.py`:

```python
def process_and_save_local(self, image_url: str, save_path: str):
    """下载并处理图片，保存到本地"""
    image_data = self.download_image(image_url)
    if not image_data:
        return None

    processed_data = self.process_image(image_data)
    if not processed_data:
        return None

    # 保存到本地
    with open(save_path, 'wb') as f:
        f.write(processed_data)

    return save_path
```

### Q: 图片处理失败率很高怎么办？

A: 检查以下几点：
1. 网络连接是否稳定
2. API配额是否用完
3. 图片URL是否有效
4. 图床服务是否限流

### Q: 能否批量重新处理失败的图片？

A: 可以，创建一个脚本读取CSV，找出图片URL未更新的行，重新处理：

```python
import csv

# 读取CSV
with open('products_complete.csv', 'r') as f:
    rows = list(csv.DictReader(f))

# 找出未处理的
failed_rows = [
    row for row in rows
    if 'hollandandbarrett' in row.get('产品图', '')
]

print(f"找到 {len(failed_rows)} 个未处理的图片")

# 重新处理
for row in failed_rows:
    # 处理逻辑...
    pass
```

## 推荐方案总结

| 方案 | 成本 | 难度 | 稳定性 | 推荐度 |
|------|------|------|--------|--------|
| 自建EasyImage | 服务器成本 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 免费图床(ImgBB) | 免费 | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 云存储(OSS) | 按量计费 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 保留原URL | 免费 | ⭐ | ⭐⭐⭐ | ⭐⭐ |

**最佳选择**: 如果有服务器，建议自建EasyImage；如果只是个人使用，ImgBB等免费图床足够。

## 获取帮助

如果遇到问题，可以：
1. 运行诊断脚本查看详细错误
2. 查看图床服务商的文档
3. 检查网络连接和防火墙
4. 查看项目Issues寻找类似问题

---

**更新时间**: 2024-11-18
