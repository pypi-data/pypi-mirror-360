# channel-exporter

[![Release](https://img.shields.io/github/release/channel07/channel-exporter.svg?style=flat-square")](https://github.com/channel07/channel-exporter/releases/latest)
[![Python Version](https://img.shields.io/badge/python-2.7+/3.6+-blue.svg)](https://github.com/channel07/channel-exporter)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/channel-exporter)](https://pepy.tech/project/channel-exporter)

用于 Python 应用的 Prometheus 指标监控库，支持 Flask、Requests 和消息队列消费者的监控指标自动收集。

## 功能特性

- ✅ 内置三大监控维度
    - Web 服务内部指标（Flask）
    - 合作商 HTTP 调用指标（Requests）
    - 消息队列消费指标（Consumer）
- ✅ Prometheus 原生集成
- ✅ 灵活的指标桶配置
- ✅ 自动化的指标收集
- ✅ 合作商接口预配置

## 安装使用

```bash
pip install channel_exporter
```

### 环境要求

- Python 2.7+
- 可选依赖（安装即监控）：
    - Flask (Web 服务监控)
    - requests (HTTP 调用监控)
    - ctec_consumer (消费者监控)

### 快速开始（Web 服务指标）

```python
# coding:utf-8
import channel_exporter
from flask import Flask

app = Flask(__name__)


@app.get("/")
def hello():
    return "Hello World!"


if __name__ == "__main__":
    # 初始化监控配置
    channel_exporter.__init__("<your_syscode>")

    # 启动后访问 /metrics 获取指标
    app.run()
```

## 配置说明

### 初始化参数

| 参数名                            | 类型    | 必填 | 默认值  | 说明                   |
|--------------------------------|-------|----|------|----------------------|
| `syscode`                      | str   | 是  | 无    | 10位服务编码，格式：大写字母+9位数字 |
| `inner_metrics_buckets`        | tuple | 否  | 默认桶  | Web 服务耗时分布桶          |
| `partner_http_metrics_buckets` | tuple | 否  | 默认桶  | HTTP 调用耗时分布桶         |
| `consumer_metrics_buckets`     | tuple | 否  | 默认桶  | 消费者耗时分布桶             |
| `default_metrics_port`         | int   | 否  | 9166 | 指标默认暴露端口             |

## 指标说明

### Web 服务指标

指标名称：`[syscode]_inner_metrics`

标签说明：

- `appid`: 应用ID（syscode前4位）
- `application`: 系统编码
- `f_code`: 请求方系统编码（取自 headers["User-Agent"]）
- `path`: 请求路径
- `http_status`: HTTP 状态码
- `code`: 业务响应码
- `method_code`: 接口编号

### HTTP 调用指标

指标名称：`partner_http_metrics`

标签说明：

- `appid`: 应用ID（syscode前4位）
- `application`: 系统编码
- `partner`: 合作商（域名）编号
- `action_code`: 动作（路径）编号
- `http_status`: HTTP 状态码
- `code`: 业务响应码（由业务方定义，-1表示未找到业务响应码）

### 消费者指标

指标名称：`[syscode]_consumer_metrics`

标签说明：

- `appid`: 应用ID（syscode前4位）
- `application`: 完整syscode
- `f_code`: 空值
- `topic`: 消息主题
- `code`: 处理结果（0成功/1失败）
