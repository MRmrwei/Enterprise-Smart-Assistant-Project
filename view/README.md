# View

> 企业智能助手前端界面，基于 Vue 3 + Element Plus + Vite 构建


## 📖 项目概述

**View** 是**企业智能助手**的 **Web 前端**，基于 [Vue 3](https://vuejs.org/) + [Element Plus](https://element-plus.org/) + [Vite](https://vitejs.dev/) 构建。提供登录、AI 对话、知识库文档导入三个核心页面，通过 SSE 流式协议与后端 Agent 服务交互。

**定位**：作为整体架构中的用户交互层，专注界面展示与前后端通信，不包含业务逻辑。


## ✨ 核心特性

| 特性 | 说明 |
| :--- | :--- |
| **🔐 登录鉴权** | 账号密码登录，JWT Token 存储于 `localStorage`，请求统一携带 `Authorization` Bearer 头 |
| **💬 AI 对话（SSE 流式）** | 基于 `fetch` 读取 `text/event-stream` 流，实时渲染 AI 思考过程与最终答案 |
| **⌨️ 打字机效果** | 前端自建字符队列，逐字渲染回答，支持 HTML 标签与转义实体的正确分片 |
| **🧠 推理过程展示** | 将后端推送的 `reasoning` 与 `answer` 分块展示，推理阶段与答案阶段分离 |
| **📥 知识库导入** | 支持 `.txt` 文档批量上传（最多 10 个），可选父子块 / 通用切块策略，实时上传进度 |
| **🛡️ 鉴权兜底** | 响应 `401/403` 自动清除 Token 并跳转登录，登录过期友好提示 |
| **📐 路由守卫** | 基于 `vue-router` 的全局前置守卫，未登录访问受保护页面自动重定向登录 |


## 🛠️ 技术栈

| 层级 | 技术选型 |
| :--- | :--- |
| **框架** | Vue 3（Composition API + `<script setup>`） |
| **UI 组件** | Element Plus |
| **构建工具** | Vite |
| **路由** | Vue Router |
| **状态管理** | 组合式函数（`composables/`） |


## 📐 页面与路由

| 路由 | 页面 | 说明 |
| :--- | :--- | :--- |
| `/login` | 登录 | 账号密码登录，获取 JWT |
| `/home` | 功能导航 | 功能入口卡片（对话 / 文档导入） |
| `/chat` | AI 对话 | SSE 流式对话，推理过程 + 最终答案 |
| `/rag` | 文档导入 | TXT 上传向量化，切块策略选择 |

> 除 `/login` 外，其余路由均在 `MainLayout` 布局下，且需登录访问。


## 🔌 接口对接

| 接口 | 方法 | 说明 |
| :--- | :--- | :--- |
| `/login` | POST | 登录，返回 Token |
| `/chat` | POST | AI 对话（SSE 流式） |
| `/upload_rag_file` | POST | 知识库文件上传（FormData） |
| `/logout` | POST | 退出登录 |

开发环境通过 Vite `proxy` 将上述接口代理到后端网关（默认 `http://127.0.0.1:8888`），配置见 `vite.config.js` 与 `.env`。


## 🗂️ 目录结构

```
view/
├── index.html                  # 入口 HTML
├── vite.config.js              # Vite 配置（端口 / 代理）
├── src/
│   ├── main.js                 # 应用入口（挂载 Element Plus + Router）
│   ├── App.vue                 # 根组件（router-view）
│   ├── router/                 # 路由配置与守卫
│   ├── layouts/                # 全局布局（顶栏 + 内容区）
│   ├── views/                  # 页面（Login / Nav / Chat / Rag）
│   ├── composables/            # 组合式函数（useChat / useLogin / useRag）
│   ├── utils/                  # 请求封装、Token 管理
│   └── styles/                 # 页面样式
└── package.json                # 依赖与脚本
```


## 🚀 快速开始

```bash
# 1. 安装依赖
npm install

# 2. 配置后端地址（可选，默认 http://127.0.0.1:8888）
cp .env.example .env
# 编辑 .env 中的 VITE_BACKEND_URL

# 3. 启动开发服务器（默认 :5173）
npm run dev

# 4. 生产构建
npm run build
```

> 前端依赖后端网关、Agent、Service-MCP 服务已就绪，参见项目根 [README](../README.md)。

---

## 📝 License

MIT © 2026 Mr.zhu
