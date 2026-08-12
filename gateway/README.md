# Gateway

> 基于 go-zero 框架构建的统一流量入口，负责 HTTP 请求路由、JWT 鉴权及后端服务转发


## 📖 项目概述

**Gateway** 是**企业智能助手**的 **HTTP 网关层**，基于 [go-zero](https://go-zero.dev/) 的 `gateway` 组件构建。它接收前端 HTTP 请求，进行 JWT 鉴权后，将请求转发至后端各服务。

**核心职责**：

- **统一入口**：对外提供统一的 HTTP API 入口（默认端口 `8888`）
- **JWT 鉴权**：解析并校验 Token，提取用户身份并注入 `X-uid` Header
- **服务转发**：同时支持 gRPC 与 HTTP 两类上游，按路由规则转发至后端
- **SSE 流式透传**：对 `/chat` 等流式接口做逐块 Flush，实现 AI 回答的流式输出

**定位**：作为整体架构中的流量入口，专注路由转发与身份认证，不包含业务逻辑。


## ✨ 核心特性

| 特性 | 说明 |
| :--- | :--- |
| **🛡️ JWT 鉴权** | 基于 `handler.Authorize` 校验 Token，白名单路径（`/login`）跳过认证 |
| **🔌 MCP 协议感知** | 智能识别 MCP 请求体中的 `method`，非 `tools/call` 请求自动跳过认证（握手 / 初始化免鉴权） |
| **👤 身份透传** | 鉴权通过后从上下文提取 `uid`，写入 `X-uid` Header 传递给下游 |
| **🔀 多协议转发** | gRPC 上游（登录 RPC）+ HTTP 上游（MCP 服务 / Agent 服务）统一路由 |
| **📡 SSE 流式转发** | 逐块读取并 `Flush` 后端响应，支持 AI 对话的流式输出 |


## 🛠️ 技术栈

| 层级 | 技术选型 |
| :--- | :--- |
| **语言** | Go 1.25+ |
| **框架** | go-zero |
| **认证** | `handler.Authorize`（JWT HS256） |
| **HTTP 转发** | go-zero `httpc`（自动注入 traceparent） |
| **gRPC 转发** | protobuf 描述符 + `ProtoSets` 反序列化 |


## 📐 路由配置

网关通过 `etc/gateway-api.yaml` 配置上游与路由映射：

| 路由 | 上游类型 | 目标 | 说明 |
| :--- | :--- | :--- | :--- |
| `POST /login` | gRPC | `localhost:8081` | 登录认证（`main.rpc/Login`） |
| `POST /mcp` | HTTP | `localhost:8083` | MCP 数据服务 |
| `POST /upload_rag_file` | HTTP | `localhost:8084` | 知识库文件上传（Agent 服务） |
| `POST /chat` | HTTP (SSE) | `127.0.0.1:8084` | AI 对话（SSE 流式转发） |


## 🗂️ 目录结构

```
gateway/
├── gateway.go                   # 入口：网关启动、鉴权中间件、路由注册
├── etc/gateway-api.yaml         # 网关配置（端口 / 上游 / 路由 / Auth）
├── pb/                          # protobuf 生成代码（登录 RPC）
├── internal/
│   ├── config/                  # 配置结构体
│   ├── middlewares/             # JWT 鉴权（白名单 + MCP 感知）
│   ├── routes/                  # 路由注册（SSE / 超时）
│   ├── routes/agents/           # 后端转发 Handler（SSE 流式透传）
│   ├── svc/                     # 服务上下文
│   └── types/                   # 类型定义
└── airpc/                       # RPC 客户端封装
```


## 🚀 快速开始

```bash
# 1. 配置 etc/gateway-api.yaml（端口、上游地址、Auth 密钥等）

# 2. 启动网关（默认 :8888）
go run gateway.go -f etc/gateway-api.yaml
```


## 🔭 后续规划

- [ ] 限流 / 熔断策略接入
- [ ] 请求日志与链路追踪（traceparent 透传已就绪）
- [ ] 配置中心（Etcd）动态更新路由

---

## 📝 License

MIT © 2026 Mr.zhu
