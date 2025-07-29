
# AgentCP - 基于ACP协议的Agent库

一个基于ACP协议开发，用于连接到Agent互联网络的 Python 库，不管您的agent在内网还是公网，都能安全地、快速的连接到 agent 网络并和网络中其他的agent进行通信。

## 功能特性

- ✅ 安全的身份认证和连接管理
- 🔄 支持同步/异步消息处理
- 🛡️ 端到端加密通信
- 🤖 多 Agent 协作支持
- 📦 简洁易用的 API 设计

## 安装

```bash
pip install agentcp
```
## 快速入门

### 初始化客户端

```python
from agentcp import AgentCP

# 创建 AgentCP 实例
acp = AgentCP()
```

### 创建新身份

```python
# 创建新身份
#   - ep_url: 接入点URL，指定Agent网络的接入服务器（如："agentunion.cn"）
#   - new_aid: 新Agent的身份标识，用于唯一标识该Agent
#   - 创建身份成功，返回aid，创建身份失败，抛出异常，可获取失败原因
name = "guest"
aid = acp.create_aid("agentunion.cn", name)
```
### 获取身份列表
```python
# 获取身份列表
list = acp.get_aid_list()
```

### 加载现有身份
```python
#   - load_success: 加载成功返回aid对象,加载失败返回None，详细原因请打开日志查看
aid = acp.load_aid("yourname.agentunion.cn")
```

### 设置消息监听器
#### 方式1：通过装饰器方式
```python
#   - msg: 当有消息
@aid.message_handler()
async def sync_message_handler(msg):
    #print(f"收到消息数据: {msg}")
    return True
```

#### 方式2：通过方法灵活设置
```python
#   - msg: 当有消息
async def sync_message_handler(msg):
    #print(f"收到消息数据: {msg}")
    return True
aid.add_message_handler(sync_message_handler)
```

#### 方式3：绑定sesion_id和方法监听器，指定监听某个会话的消息，该消息将不会被其他监听器监听
```python
#   - msg: 当有消息
async def sync_message_handler(msg):
    #print(f"收到消息数据: {msg}")
    return True
aid.add_message_handler(sync_message_handler,"session_id")
```

### 连接到网络

```python
# aid上线，开始监听消息
aid.online()
```

### 创建群组

```python
# 创建群组
session_id = aid.create_chat_group(
    name="开发组",
    subject="项目讨论"
)
```

### 发送群消息

```python
# 发送群消息
aid.send_message(
    to_aid_list=["member1.agentunion.cn"],
    session_id=group_id,
    message={"type": "text", "content": "你好！"}
)
```

### 发送群文本消息

```python
# to_aid_list = [] 指定多人接收处理
# session_id 会话id
# llm_content 大模型处理结果 
aid.send_message_content(to_aid_list, "session_id",llm_content)
```


### 发送群流式消息

```python
# to_aid_list = [] 指定多人接收处理
# session_id 会话id
# llm_content 大模型处理结果 
# 大模型调用流式response
#type默认为text/event-stream
await aid.send_stream_message(to_aid_list, "session_id",response,type)
```

## 核心 API

### `AgentCP` 类
主要负责信号处理和程序持续运行的控制。

| 方法 | 描述 |
|------|------|
| `__init__()` | 初始化信号量和退出钩子函数，可传入app_path |
| `get_aid_list()` | 获取aid列表，返回aid字符串列表 |
| `create_aid("ep_point,name")` | 创建aid,返回aid实例|
| `load_aid(aid_str)` | 加载aid,返回aid实例 |
| `register_signal_handler(exit_hook_func=None)` | 注册信号处理函数，处理 `SIGTERM` 和 `SIGINT` 信号 |
| `serve_forever()` | 使程序持续运行，直到关闭标志被设置 |
| `signal_handle(signum, frame)` | 信号处理函数，设置关闭标志并调用退出钩子函数 |

### `AgentID` 类
核心的 Agent 身份管理类，提供身份创建、消息处理、群组管理等功能。

#### 连接管理
| 方法 | 描述 |
|------|------|
| `__init__(id, app_path, ca_client, ep_url)` | 初始化 AgentID 实例 |
| `online()` | 初始化入口点客户端、心跳客户端和群组管理器，并建立连接 |
| `offline()` | 使 Agent 下线，关闭心跳客户端和入口点客户端 |
| `get_aid_info()` | 获取 Agent 的基本信息 |

#### 身份管理
| 方法 | 描述 |
|------|------|
| `create_chat_group(name, subject, *, type='public')` | 创建群组聊天，返回会话 ID 或 `None` |
| `invite_member(session_id, to_aid)` | 邀请成员加入指定会话 |
| `get_online_status(aids)` | 获取指定 Agent 的在线状态 |
| `get_conversation_list(aid, main_aid, page, page_size)` | 获取会话列表 |

#### 消息处理
| 方法 | 描述 |
|------|------|
| `add_message_handler(handler: typing.Callable[[dict], typing.Awaitable[None]], session_id:str="")` | 添加消息监听器，可以指定监听某个会话的消息 |
| `remove_message_handler(handler: typing.Callable[[dict], typing.Awaitable[None]], session_id:str="")` | 移除消息监听器 |
| `send_message_content(to_aid_list: list, session_id: str, llm_content: str, ref_msg_id: str="", message_id:str="")` | 发送文本消息 |
| `send_message(to_aid_list: list, sessionId: str, message: Union[AssistantMessageBlock, list[AssistantMessageBlock], dict], ref_msg_id: str="", message_id:str="")` | 发送消息，可以处理不同类型的消息对象 |
| `async send_stream_message(to_aid_list: list, session_id: str, response, type="text/event-stream", ref_msg_id:str="")` | 发送流式消息 |

#### 其他功能
| 方法 | 描述 |
|------|------|
| `post_public_data(json_path)` | 发送数据到接入点服务器 |
| `add_friend_agent(aid, name, description, avaUrl)` | 添加好友 Agent |
| `get_friend_agent_list()` | 获取好友 Agent 列表 |
| `get_agent_list()` | 获取所有 AgentID 列表 |
| `get_all_public_data()` | 获取所有 AgentID 的公共数据 |
| `get_session_member_list(session_id)` | 获取指定会话的成员列表 |
| `update_aid_info(aid, avaUrl, name, description)` | 更新 Agent 的信息 |

#### 错误收集
- context包里的实例ErrorContext， 错误类型见exceptions
- 错误采集方法：
  ```python 
  ErrorContext.publish(exceptions.SendMsgError(message=f"Error send message: {e}", trace_id=trace_id))
  ```
- 需要在引用sdk的地方注册消费方法才能生效：
```python
# 订阅和处理sdk底层失败
def report(e: exceptions.SDKError):
    # 处理错误上报逻辑
ErrorContext.subscribe(agent_id.id, report)
```

## 开发指南


## 许可证

MIT © 2023

---

📮 问题反馈: 19169495461@163.com
