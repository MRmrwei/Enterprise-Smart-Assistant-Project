# 企业智能助手

> 基于 LangGraph + go-zero + Vue 3 构建的 AI Agent 系统


## 📖 项目概述

本项目是一个**企业员工自助服务 AI 助手**，采用微服务架构设计，由四个核心组件构成：

| 组件 | 技术栈 | 职责 |
| :--- | :--- | :--- |
| **[View](./view/README.md)** | Vue 3 + Element Plus + Vite | 前端界面：登录、AI 对话、知识库上传 |
| **[Gateway](./gateway/README.md)** | go-zero | 流量入口：HTTP 网关、JWT 鉴权、请求路由 |
| **[Service-MCP](./service-mcp/README.md)** | go-zero + gRPC + MCP | 业务服务层：认证 RPC、MCP 数据服务 |
| **[Agent](./enterprise_emart_assistant/README.md)** | LangGraph + FastAPI | AI 编排层：意图识别、多智能体协作、RAG 问答 |

**系统定位**：为企业员工提供智能化的自助服务，涵盖制度问答、请假报销申请、个人数据查询等场景。


## 🏗️ 整体架构

```mermaid
graph TB
    subgraph 前端层
        A[View<br/>Vue 3 + Vite]
    end

    subgraph 网关层
        B[Gateway<br/>go-zero :8888]
    end

    subgraph 服务层
        C[Service-MCP<br/>RPC :8081 / MCP :8083]
        D[Python Agent<br/>LangGraph :8084]
    end

    subgraph 存储层
        E[(MySQL)]
        F[(Chroma)]
        G[(Redis)]
    end

    A -->|HTTP/SSE| B
    B -->|gRPC /login| C
    B -->|HTTP /mcp| C
    B -->|HTTP /upload_rag_file| D
    B -->|HTTP SSE /chat| D
    C -->|SQL| E
    C -->|Redis| G
    D -->|HTTP/SSE| C
    D -->|Chroma| F
```

**请求链路**：前端通过 Vite 代理将请求发往网关，网关完成 JWT 鉴权后，按路由规则将 `/login`（gRPC）、`/mcp`（HTTP）转发至 Service-MCP，将 `/chat`（SSE）、`/upload_rag_file`（HTTP）转发至 Python Agent 服务。


## 🚀 快速开始

### 1. 启动基础设施

```bash
# 启动 MySQL、Redis
```

### 2. 初始化数据库

```bash
# 创建数据库
mysql -u root -p < deploy/initsql/init.sql

# 迁移表结构（golang-migrate）
migrate -path deploy/migrations -database "mysql://root:root@tcp(127.0.0.1:3306)/ai" up
```

### 3. 启动 Service-MCP

```bash
cd service-mcp
go mod tidy
go run main.go            # RPC :8081 / MCP :8083
```

### 4. 启动 Agent

```bash
cd enterprise_emart_assistant
uv sync
uv run main.py            # FastAPI :8084
```

### 5. 启动 Gateway

```bash
cd gateway
go mod tidy
go run gateway.go         # HTTP 网关 :8888
```

### 6. 启动前端

```bash
cd view
npm install
npm run dev               # Vite 开发服务器 :5173
```

访问 `http://localhost:5173`，默认账号 `admin` / 密码 `admin`。


## 📂 项目目录结构

```
.
├── view/                        # 前端（Vue 3 + Element Plus + Vite）
│   ├── src/views/               # 登录 / 对话 / 知识库页面
│   ├── src/composables/         # 组合式函数（SSE 对话、登录、RAG）
│   └── vite.config.js           # 开发代理配置
│
├── gateway/                     # 网关服务（go-zero）
│   ├── internal/                # 鉴权中间件、路由、转发
│   └── etc/                     # 网关配置（端口 / 上游 / 路由）
│
├── service-mcp/                 # 业务服务层（go-zero）
│   ├── internal/                # RPC 逻辑、MCP 工具、数据访问
│   ├── pb/                      # protobuf 生成代码
│   └── etc/                     # 服务配置
│
├── enterprise_emart_assistant/  # Python Agent 服务（LangGraph）
│   ├── agents/                  # 子智能体
│   ├── graphs/                  # 主图与状态管理
│   ├── nodes/                   # 图节点实现
│   ├── tools/                   # 工具与 Skill
│   ├── skills/                  # SKILL 定义
│   ├── llms/                    # LLM 工厂
│   ├── db/                      # 向量数据库 / 缓存 / 重排
│   └── services/                # 对话流式、知识入库、RAG 检索
│
├── protos/                      # Protocol Buffers 定义
├── deploy/                      # 数据库脚本与迁移
└── README.md                    # 项目根文档
```


## 🔭 后续优化规划

- [ ] 增加 Docker 部署方案（含 docker-compose 编排）
- [ ] 检查点存储迁移至 PostgreSQL / Redis，支持持久化与分布式部署
