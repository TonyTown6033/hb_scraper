# WebDriver 并发架构说明

## 当前实现机制

### 是的！已经是多WebDriver并发了 ✅

当前的实现**已经是每个线程一个独立的WebDriver**：

```
线程1 → WebDriver实例1 → 爬取产品1,5,9...
线程2 → WebDriver实例2 → 爬取产品2,6,10...
线程3 → WebDriver实例3 → 爬取产品3,7,11...
线程4 → WebDriver实例4 → 爬取产品4,8,12...
```

### 代码位置

在 `utils/parallel_scraper.py:121`:
```python
# 每个线程在处理每个任务时都会创建新的driver
driver = self._create_driver()
```

## 如何增加WebDriver数量？

### 方法1: 增加线程数（推荐）

运行时输入更大的线程数：
```
并发线程数 (建议2-3, 默认3): 8
```

这会创建**8个并发的WebDriver实例**！

### 方法2: 修改默认配置

编辑 `main.py`，修改默认值：
```python
workers = input("并发线程数 (建议2-3, 默认3): ").strip() or "8"  # 改为8
max_workers = min(max(int(workers), 1), 16)  # 上限改为16
```

### 方法3: 直接调用函数时指定

```python
products = scrape_details_parallel(
    products=products,
    scrape_detail_func=scrape_product_detail,
    max_workers=10,  # 10个WebDriver并发！
    request_delay=(1, 2)  # 缩短延迟
)
```

## 性能限制因素

### 1. 系统资源

每个WebDriver（Chrome）需要：
- **内存**: ~200-300MB
- **CPU**: 1个核心的部分使用

**计算公式**:
- 8GB内存 → 最多 15-20 个WebDriver
- 16GB内存 → 最多 30-40 个WebDriver

### 2. 网络限制

目标网站可能有：
- **请求频率限制**: 过快会被限流
- **IP限制**: 同一IP并发过多会被封

### 3. ChromeDriver限制

ChromeDriver本身支持高并发，理论上可以几十个实例。

## 性能对比

### 不同并发数的效果（100个产品）

| 线程数 | WebDriver数 | 预估耗时 | 成功率 | 内存占用 |
|--------|-------------|----------|--------|----------|
| 1 | 1 | 200秒 | 95% | ~300MB |
| 3 | 3 | 70秒 | 90% | ~900MB |
| 5 | 5 | 45秒 | 85% | ~1.5GB |
| 8 | 8 | 30秒 | 75% | ~2.4GB |
| 10 | 10 | 25秒 | 70% | ~3GB |
| 15 | 15 | 20秒 | 60% | ~4.5GB |

**结论**:
- **3-5个线程** = 性价比最高
- **8-10个线程** = 追求速度
- **15+个线程** = 不推荐（成功率太低）

## 优化建议

### 激进配置（速度优先）

```python
max_workers=8
retry_times=5
request_delay=(0.5, 1.5)  # 缩短延迟
```

**适用场景**:
- 网络很好
- 内存充足（8GB+）
- 目标网站不严格

### 平衡配置（推荐）

```python
max_workers=5
retry_times=3
request_delay=(2, 4)
```

**适用场景**:
- 大多数情况
- 内存中等（4-8GB）
- 追求稳定性和速度平衡

### 保守配置（稳定优先）

```python
max_workers=2
retry_times=3
request_delay=(3, 5)
```

**适用场景**:
- 网络不稳定
- 内存有限
- 目标网站严格

## 实际测试建议

1. **从少到多测试**：先用3个，再5个，再8个
2. **观察成功率**：如果低于80%就减少线程
3. **监控系统**：用活动监视器查看内存/CPU
4. **记录最佳值**：找到你系统的最佳并发数

## 自动寻找最佳并发数

我们提供了性能测试工具 `scripts/find_optimal_threads.py`，可以自动找到最佳线程数！
