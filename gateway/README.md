# Gateway

> 基于 go-zero 框架构建的统一流量入口，负责 HTTP 请求路由、JWT 鉴权及 gRPC 服务转发


## 📖 项目概述

**Gateway** 是**企业智能助手**的 **HTTP 网关层**，基于 **go-zero** 框架构建。它负责接收前端 HTTP 请求，进行 JWT 鉴权后，通过 gRPC 将请求转发至后端服务。

**核心职责**：
- **HTTP 网关**：接收前端请求，提供统一的 API 入口
- **JWT 鉴权**：解析并校验 Token，提取用户身份
- **服务转发**：通过 gRPC 将请求转发至认证服务（Service-MCP）和对话服务（Python Agent）
- **协议适配**：支持 HTTP 和 SSE（Server-Sent Events）两种响应模式

**定位**：作为整体架构中的流量入口，专注路由转发与身份认证，不包含业务逻辑。


