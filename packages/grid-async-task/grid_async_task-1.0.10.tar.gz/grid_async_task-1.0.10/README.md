# grid 异步任务处理插件

一个通用的异步任务处理插件，支持RabbitMQ队列监听、任务重试、进度通知、回调等功能。专为Kubernetes + KEDA自动扩缩容环境设计。

## 功能特性

- 🚀 **RabbitMQ队列监听**: 支持从RabbitMQ队列获取任务，每次处理一个任务
- 🔄 **智能重试机制**: 支持任务执行失败时的重试，可配置重试次数和策略
- 📊 **进度通知**: 支持任务执行过程中的进度通知
- 📞 **多种回调方式**: 支持HTTP和RabbitMQ两种回调通知方式
- 💾 **任务持久化**: 基于MySQL的任务状态持久化存储
- 📝 **详细日志**: 完整的任务执行日志记录
- 🔔 **飞书通知**: 任务失败时的飞书webhook通知
- 🏗️ **高可用设计**: 支持网络中断重连、数据库连接池等
- ⏰ **空闲超时**: 支持空闲超时自动退出，优化资源使用
- ⚙️ **环境配置**: 通过环境变量或.env文件进行配置

## 安装

```bash
pip install grid-async-task
```

## 快速开始

### 1. 配置环境变量

创建 `.env` 文件或设置环境变量：

```env
# ====================================
# Grid异步任务处理插件配置 (必填)
# ====================================

# RabbitMQ AMQP连接URL
GRID_ASYNC_TASK_AMQP_URL=amqp://guest:guest@localhost:5672/

# 任务队列名称
GRID_ASYNC_TASK_QUEUE=task_queue

# MySQL连接URL 
GRID_ASYNC_TASK_MYSQL_URL=mysql+pymysql://root:password@localhost:3306/task_db?charset=utf8mb4

# ====================================
# 可选配置项
# ====================================

# 数据库表配置（避免表名冲突）
GRID_ASYNC_TASK_TABLE_PREFIX=grid_async_task_
GRID_ASYNC_TASK_TABLE_NAME=tasks

# 任务重试配置
GRID_ASYNC_TASK_MAX_RETRY_COUNT=3
GRID_ASYNC_TASK_RETRY_DELAY=60

# 空闲超时配置（秒），0表示永不退出
GRID_ASYNC_TASK_IDLE_TIMEOUT=0

# 日志配置
GRID_ASYNC_TASK_LOG_LEVEL=INFO
GRID_ASYNC_TASK_LOG_DIR=logs

# 飞书通知（可选，任务失败时发送通知）
GRID_ASYNC_TASK_FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
```

**配置说明**：
- 📋 参考项目目录下的 `env_example.txt` 文件查看完整配置示例
- 🔒 敏感信息（密码、密钥等）请妥善保管，不要提交到代码仓库

### 2. 创建任务处理器

```python
from grid_async_task import TaskHandler, TaskProcessor

class MyTaskHandler(TaskHandler):
    def execute(self, task_data):
        """执行具体的任务逻辑"""
        # 报告进度
        self.report_progress(20, "开始处理...")
        
        # 执行任务逻辑
        result = self.process_data(task_data)
        
        # 报告进度
        self.report_progress(100, "处理完成")
        
        return result
    
    def process_data(self, data):
        # 你的具体业务逻辑
        return {"status": "success", "result": data}

# 启动任务处理器
processor = TaskProcessor(handler=MyTaskHandler())
processor.start()
```

### 3. 任务生产者示例

```python
from grid_async_task import TaskProducer

# 基本使用 - 使用配置文件中的默认队列
producer = TaskProducer()
producer.send_task({
    "task_id": "unique_task_id",
    "task_type": "data_processing",
    "data": {"input": "test_data"},
    "callback_url": "http://your-api.com/callback",
    "retry_count": 3
})
```

### 4. 动态队列功能（NEW！）

**TaskProducer** 现在支持动态传入队列名称，让您可以将不同类型的任务发送到不同的队列中，实现更灵活的任务调度。

#### 基本用法

```python
from grid_async_task import TaskProducer

# 方式1：指定默认队列
producer = TaskProducer(default_queue="my_custom_queue")
task_id = producer.send_task(task_data)  # 发送到 my_custom_queue

# 方式2：动态指定队列
producer = TaskProducer()
task_id = producer.send_task(task_data, queue_name="high_priority_queue")

# 方式3：使用便捷方法
task_id = producer.send_task_to_queue(task_data, "gpu_queue")
```

#### 批量发送任务

```python
# 批量发送到指定队列
batch_tasks = [
    {"task_data": {"task_type": "validation", "data": {"file": f"file_{i}"}}
     for i in range(10)
]
task_ids = producer.batch_send_tasks(batch_tasks, queue_name="validation_queue")

# 批量发送到默认队列
task_ids = producer.batch_send_tasks(batch_tasks)
```

#### 队列管理

```python
# 检查队列是否已声明
if not producer.is_queue_declared("new_queue"):
    producer.send_task(task_data, queue_name="new_queue")  # 自动声明队列

# 查看已声明的队列
declared_queues = producer.get_declared_queues()
print(f"已声明的队列: {declared_queues}")
```

#### 实际应用场景

```python
# 按优先级分发任务
high_priority_task = {
    "task_type": "urgent_analysis", 
    "data": {"priority": "high"}
}
producer.send_task(high_priority_task, queue_name="high_priority_queue")

low_priority_task = {
    "task_type": "batch_processing", 
    "data": {"priority": "low"}
}
producer.send_task(low_priority_task, queue_name="low_priority_queue")

# 按资源类型分发任务
gpu_task = {"task_type": "ml_training", "data": {"model": "cnn"}}
producer.send_task(gpu_task, queue_name="gpu_queue")

cpu_task = {"task_type": "data_processing", "data": {"format": "csv"}}
producer.send_task(cpu_task, queue_name="cpu_queue")
```

## 协议说明

### 任务消息协议

#### RabbitMQ 消息格式

发送到队列的消息必须是 JSON 格式，包含以下字段：

```json
{
    "task_id": "string",              // 必需：任务唯一标识符
    "task_type": "string",            // 可选：任务类型，默认 "default"
    "data": {},                       // 可选：任务具体数据，任意 JSON 对象
    "max_retry_count": 3,             // 可选：最大重试次数，默认 0
    "callback_url": "string",         // 可选：HTTP 回调地址
    "callback_type": "http|rabbitmq", // 可选：回调类型，默认 "http"
    "callback_data": {}               // 可选：回调附加数据
}
```

#### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|-----|------|------|------|
| `task_id` | string | ✓ | 任务唯一标识符，建议使用UUID |
| `task_type` | string | ✗ | 任务类型标识，用于业务分类 |
| `data` | object | ✗ | 任务执行所需的具体数据 |
| `max_retry_count` | int | ✗ | 最大重试次数，0表示不重试 |
| `callback_url` | string | ✗ | 任务完成后的HTTP回调地址 |
| `callback_type` | string | ✗ | 回调方式：`http` 或 `rabbitmq` |
| `callback_data` | object | ✗ | 回调时携带的额外数据 |

### 任务状态定义

| 状态 | 说明 |
|------|------|
| `pending` | 等待处理 |
| `running` | 执行中 |
| `success` | 执行成功 |
| `failed` | 执行失败 |
| `retrying` | 重试中 |

### 回调协议

#### HTTP 回调

当任务完成时，系统会向 `callback_url` 发送 POST 请求：

```json
{
    "task_id": "string",        // 任务ID
    "status": "success|failed", // 任务状态
    "result": {},               // 任务结果数据
    "timestamp": "string",      // 完成时间 (ISO 8601)
    "callback_data": {}         // 任务提交时的回调数据
}
```

**HTTP 回调要求：**
- 请求方法：`POST`
- Content-Type：`application/json`
- 超时时间：30秒
- 重试次数：3次
- 成功判断：返回状态码 `200`

#### RabbitMQ 回调

当 `callback_type` 为 `rabbitmq` 时，回调消息会发送到指定队列：

```json
{
    "task_id": "string",
    "status": "success|failed",
    "result": {},
    "timestamp": "string",
    "callback_data": {
        "queue_name": "callback_queue"  // 可选：指定队列名，默认 "callback_queue"
    }
}
```

### 进度通知协议

任务执行过程中的进度会更新到数据库，可通过查询API获取：

```json
{
    "task_id": "string",
    "progress": 75,                    // 进度百分比 (0-100)
    "progress_message": "处理中...",   // 进度描述
    "status": "running",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### 多语言接入示例

#### Python

```python
import json
import pika
import uuid

# 连接RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# 发送任务
task = {
    "task_id": str(uuid.uuid4()),
    "task_type": "data_processing",
    "data": {"input": "test_data"},
    "callback_url": "http://your-api.com/callback",
    "max_retry_count": 3
}

channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=json.dumps(task),
    properties=pika.BasicProperties(delivery_mode=2)
)
```

#### Node.js

```javascript
const amqp = require('amqplib');
const { v4: uuidv4 } = require('uuid');

async function sendTask() {
    const connection = await amqp.connect('amqp://localhost');
    const channel = await connection.createChannel();
    
    const task = {
        task_id: uuidv4(),
        task_type: 'data_processing',
        data: { input: 'test_data' },
        callback_url: 'http://your-api.com/callback',
        max_retry_count: 3
    };
    
    await channel.sendToQueue(
        'task_queue', 
        Buffer.from(JSON.stringify(task)),
        { persistent: true }
    );
}
```

#### Java (Spring Boot)

```java
@Service
public class TaskProducer {
    
    @Autowired
    private RabbitTemplate rabbitTemplate;
    
    public String sendTask(String taskType, Object data, String callbackUrl) {
        String taskId = UUID.randomUUID().toString();
        
        Map<String, Object> task = new HashMap<>();
        task.put("task_id", taskId);
        task.put("task_type", taskType);
        task.put("data", data);
        task.put("callback_url", callbackUrl);
        task.put("max_retry_count", 3);
        
        rabbitTemplate.convertAndSend("task_queue", task);
        return taskId;
    }
}
```

#### Go

```go
package main

import (
    "encoding/json"
    "github.com/google/uuid"
    "github.com/streadway/amqp"
)

type Task struct {
    TaskID         string      `json:"task_id"`
    TaskType       string      `json:"task_type"`
    Data           interface{} `json:"data"`
    CallbackURL    string      `json:"callback_url"`
    MaxRetryCount  int         `json:"max_retry_count"`
}

func sendTask() error {
    conn, err := amqp.Dial("amqp://localhost")
    if err != nil {
        return err
    }
    defer conn.Close()
    
    ch, err := conn.Channel()
    if err != nil {
        return err
    }
    defer ch.Close()
    
    task := Task{
        TaskID:        uuid.New().String(),
        TaskType:      "data_processing",
        Data:          map[string]string{"input": "test_data"},
        CallbackURL:   "http://your-api.com/callback",
        MaxRetryCount: 3,
    }
    
    body, _ := json.Marshal(task)
    
    return ch.Publish(
        "",           // exchange
        "task_queue", // routing key
        false,        // mandatory
        false,        // immediate
        amqp.Publishing{
            DeliveryMode: amqp.Persistent,
            ContentType:  "application/json",
            Body:         body,
        })
}
```

#### PHP

```php
<?php
require_once __DIR__ . '/vendor/autoload.php';
use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

function sendTask() {
    $connection = new AMQPStreamConnection('localhost', 5672, 'guest', 'guest');
    $channel = $connection->channel();
    
    $task = [
        'task_id' => uniqid(),
        'task_type' => 'data_processing',
        'data' => ['input' => 'test_data'],
        'callback_url' => 'http://your-api.com/callback',
        'max_retry_count' => 3
    ];
    
    $msg = new AMQPMessage(
        json_encode($task),
        ['delivery_mode' => AMQPMessage::DELIVERY_MODE_PERSISTENT]
    );
    
    $channel->basic_publish($msg, '', 'task_queue');
    
    $channel->close();
    $connection->close();
}
?>
```

### 错误处理

#### 常见错误码

| 错误类型 | 说明 | 处理建议 |
|---------|------|----------|
| `ValidationError` | 任务数据验证失败 | 检查数据格式和必需字段 |
| `ConnectionError` | 数据库连接失败 | 检查数据库配置和网络 |
| `TimeoutError` | 任务执行超时 | 增加超时时间或优化任务逻辑 |
| `RetryExhausted` | 重试次数耗尽 | 检查任务逻辑或增加重试次数 |

#### 错误回调格式

```json
{
    "task_id": "string",
    "status": "failed",
    "result": {
        "error": "错误描述",
        "error_type": "ValidationError"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "callback_data": {}
}
```

**注意：** 为了安全考虑，详细的错误堆栈信息（traceback）不会在回调通知中返回，只会在飞书webhook通知中包含，便于开发人员调试。

## 详细配置

### 环境变量配置

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `RABBITMQ_HOST` | RabbitMQ主机 | localhost |
| `RABBITMQ_PORT` | RabbitMQ端口 | 5672 |
| `RABBITMQ_USERNAME` | RabbitMQ用户名 | guest |
| `RABBITMQ_PASSWORD` | RabbitMQ密码 | guest |
| `RABBITMQ_VHOST` | RabbitMQ虚拟主机 | / |
| `RABBITMQ_QUEUE` | 任务队列名称 | task_queue |
| `MYSQL_HOST` | MySQL主机 | localhost |
| `MYSQL_PORT` | MySQL端口 | 3306 |
| `MYSQL_DATABASE` | 数据库名 | task_db |
| `MYSQL_USERNAME` | 数据库用户名 | root |
| `MYSQL_PASSWORD` | 数据库密码 | password |
| `FEISHU_WEBHOOK_URL` | 飞书webhook地址 | - |
| `LOG_LEVEL` | 日志级别 | INFO |
| `LOG_DIR` | 日志目录 | logs |

### 任务表结构

插件会自动创建以下任务表：

```sql
CREATE TABLE IF NOT EXISTS async_tasks (
    id VARCHAR(255) PRIMARY KEY,
    task_type VARCHAR(100) NOT NULL,
    status ENUM('pending', 'running', 'success', 'failed', 'retrying') DEFAULT 'pending',
    data JSON,
    result JSON,
    error_message TEXT,
    progress INT DEFAULT 0,
    retry_count INT DEFAULT 0,
    max_retry_count INT DEFAULT 0,
    callback_url VARCHAR(500),
    callback_type ENUM('http', 'rabbitmq') DEFAULT 'http',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL
);
```

## API参考

### TaskProducer

任务生产者用于发送任务到RabbitMQ队列：

```python
class TaskProducer:
    def __init__(self, default_queue: Optional[str] = None):
        """
        初始化任务生产者
        
        Args:
            default_queue: 默认队列名称，如果不提供则使用配置文件中的队列名称
        """
    
    def send_task(self, task_data: Dict[str, Any], task_id: Optional[str] = None, 
                  queue_name: Optional[str] = None) -> str:
        """
        发送任务到指定队列
        
        Args:
            task_data: 任务数据
            task_id: 任务ID，如果不提供则自动生成
            queue_name: 队列名称，如果不提供则使用默认队列
            
        Returns:
            任务ID
        """
    
    def send_task_to_queue(self, task_data: Dict[str, Any], queue_name: str, 
                          task_id: Optional[str] = None) -> str:
        """发送任务到指定队列的便捷方法"""
    
    def batch_send_tasks(self, tasks: List[Dict[str, Any]], 
                        queue_name: Optional[str] = None) -> List[str]:
        """批量发送任务到指定队列"""
    
    def get_declared_queues(self) -> set:
        """获取已声明的队列列表"""
    
    def is_queue_declared(self, queue_name: str) -> bool:
        """检查队列是否已声明"""
    
    def close(self):
        """关闭连接"""
```

### TaskHandler

自定义任务处理器需要继承 `TaskHandler` 类：

```python
class TaskHandler:
    def execute(self, task_data):
        """执行任务的核心方法，子类必须实现"""
        raise NotImplementedError
    
    def report_progress(self, progress, message=""):
        """报告任务进度"""
        pass
    
    def get_task_id(self):
        """获取当前任务ID"""
        return self.task_id
```

### TaskProcessor

任务处理器的主要配置选项：

```python
processor = TaskProcessor(
    handler=MyTaskHandler(),
    max_retry_count=3,           # 最大重试次数
    retry_delay=60,              # 重试延迟（秒）
    progress_interval=10,        # 进度报告间隔（秒）
    enable_auto_ack=True,        # 自动确认消息
    prefetch_count=1             # 预取消息数量
)
```

## Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "grid_async_task.cli"]
```

## Kubernetes + KEDA配置

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: task-processor-scaler
spec:
  scaleTargetRef:
    name: task-processor
  minReplicaCount: 0
  maxReplicaCount: 10
  triggers:
  - type: rabbitmq
    metadata:
      host: amqp://user:password@rabbitmq:5672/
      queueName: task_queue
      queueLength: "1"
```

## 开发

### 本地开发环境

```bash
# 克隆项目
git clone https://github.com/grid/grid-async-task-plugin.git
cd grid-async-task-plugin

# 安装依赖
pip install -r requirements.txt

# 运行测试
python -m pytest tests/

# 构建包
python setup.py sdist bdist_wheel
```

## 🔧 故障排除

### 配置错误问题

如果看到以下错误信息：

```
Grid异步任务插件配置错误：缺少必需的环境变量配置
缺少的配置项：amqp_url, rabbitmq_queue, mysql_url
```

**解决方法**：
1. 检查环境变量是否正确设置（注意 `GRID_ASYNC_TASK_` 前缀）
2. 参考项目目录下的 `env_example.txt` 文件配置示例
3. 确认配置文件路径和格式正确

### 常见配置示例

```bash
# 设置环境变量方式1：导出环境变量
export GRID_ASYNC_TASK_AMQP_URL="amqp://guest:guest@localhost:5672/"
export GRID_ASYNC_TASK_QUEUE="task_queue"
export GRID_ASYNC_TASK_MYSQL_URL="mysql+pymysql://root:password@localhost:3306/task_db?charset=utf8mb4"

# 设置环境变量方式2：.env文件
echo 'GRID_ASYNC_TASK_AMQP_URL=amqp://guest:guest@localhost:5672/' > .env
echo 'GRID_ASYNC_TASK_QUEUE=task_queue' >> .env
echo 'GRID_ASYNC_TASK_MYSQL_URL=mysql+pymysql://root:password@localhost:3306/task_db?charset=utf8mb4' >> .env
```

### 连接问题排查

1. **RabbitMQ连接失败**
   - 检查 AMQP URL 格式是否正确
   - 确认 RabbitMQ 服务运行状态
   - 验证用户名密码和虚拟主机配置

2. **MySQL连接失败**
   - 检查 MySQL URL 格式和连接参数
   - 确认数据库服务运行状态
   - 验证数据库用户权限

3. **日志查看**
   - 默认日志保存在 `logs/` 目录
   - 调整 `GRID_ASYNC_TASK_LOG_LEVEL=DEBUG` 获取详细日志

### 技术支持

- 📖 查看项目 Wiki 获取更多帮助
- 🐛 遇到 Bug？请在 GitHub Issues 中报告
- 💬 讨论和建议请使用 GitHub Discussions

## 许可证

MIT License 