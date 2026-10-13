> **最新状态：完整后端已配置并启动。请阅读 BACKEND_SETUP.md，只需填 DeepSeek Key 后运行 start_all.ps1。以下账户专用模式与初次拉取说明为历史记录，以 BACKEND_SETUP.md 为准。**

> **本地登录修复（2026-10-12）**：已建立 Python 3.12 独立 `.venv`、创建 `.env`（随机 JWT 签名密钥）、完成四个 Alembic 迁移，并创建本地管理员 `admin` 和默认团队。当前使用 `PaperQuery_Backend/local_main.py` 的账户/基础工作空间模式，复用原项目数据库、注册登录、密码哈希、JWT 和基础业务路由。原完整 AI 入口 `main.py` 未修改。
>
> 已验证管理员登录 HTTP 200、身份和 admin 角色、错误密码 HTTP 401、未登录鉴权 HTTP 401、注册 HTTP 201、新用户登录 HTTP 200、重复注册 HTTP 409。临时测试账号已清理。浏览器实际登录并到达 `/home/dashboard`，首页真实数据请求成功。刷新后仍可保持登录。
>
> 下次启动请执行 `powershell -ExecutionPolicy Bypass -File D:\projects\ResearchSpace\start_local_accounts.ps1`。原 `start_all.ps1` 仍用于完整 AI 后端，不适用于当前最小账户环境。当前 API 仅监听 `127.0.0.1:8001`。AI/向量化接口未启用，`/health/ready` 返回 503 是真实的模型未就绪状态；这不影响注册登录。完整模式需要另行补齐 AI 依赖和有效模型密钥。
>
> 以下初次克隆记录中的“后端未启动、没有虚拟环境/数据库”等内容是修复前状态，以此更新为准。密码已在聊天中提供，未写入源码或文档。
# ResearchSpace 本地项目梳理

检查日期：2026-10-12

## 1. 已拉取的版本

- 仓库：https://github.com/Xiao666690/ResearchSpace
- 分支：Xiao1009（跟踪 origin/Xiao1009）
- 提交：4e9cf7f — feat: redesign ResearchSpace workspace, branding and interactions
- 本地位置：D:\projects\ResearchSpace
- 本次按指定分支执行完整克隆，保留该分支 Git 历史。

## 2. 本地运行状态

前端依赖已安装；`npm run build:dev` 中的 vue-tsc 类型检查和 Vite 构建均通过。本地前端已启动，登录页地址为 http://127.0.0.1:8080/login，HTTP 检查返回 200。

已执行 VS Code 打开整个项目的命令。前端运行不等于完整系统可用：本次没有启动后端，因此登录、注册、上传、问答和研究任务暂不可用。

前端本地配置位于 `PaperQuery_Frontend/config/.env.dev`，API 地址已设为 `http://127.0.0.1:8001`。示例原本使用 `/api`，但 Vite 当前没有启用 API 代理；直接使用本地后端地址可避免开发环境请求落到前端服务。

首次 `npm ci` 在 Husky prepare 阶段失败，因为前端子目录没有 `.git`。重新安装时仅在当前进程设置 `HUSKY=0`，安装成功，没有修改 package.json 或 lockfile。

构建存在组件自动导入名称冲突、Browserslist 数据过期和大 chunk 等警告，未导致类型检查或构建失败。尚未验收真实 PDF、模型输出和账号业务流程。

## 3. 项目定位与主要功能

这是一个以研究项目为中心的 AI 科研工作台，中文品牌为“研境 ResearchSpace”。

| 模块 | 主要用途 | 前端位置 |
| --- | --- | --- |
| 控制台 | 工作空间概览和活动 | src/views/dashboard |
| 论文库 | 知识库管理、论文上传与索引 | src/views/library |
| 论文阅读 | PDF 阅读、笔记、翻译与问答 | src/views/pdf、note、translate |
| 智能问答 | 基于论文上下文的问答与引用 | src/views/chat |
| 深度研究 | 输入研究目标，执行任务并查看成果、轨迹 | src/views/research |
| 研究项目 | 项目创建、概览与论文关联 | src/views/projects |
| 时间线 | 查看研究活动与事件 | src/views/timeline |
| 比较实验室 | 多篇论文按维度比较 | src/views/compare |
| 证据看板 | 观点、支持证据与反证 | src/views/evidence |
| 研究图谱 | 实体和关系可视化 | src/views/research-map |
| 成果工作室 | 文稿编辑与引用核验 | src/views/studio |
| 协作、团队 | 项目成员、评论、任务分配和团队管理 | src/views/collaboration、team |

论坛代码仍存在，但前端路由已注释，当前不会作为正常页面开放。量子工具适配器仅为接口骨架，源码明93确说明尚未接入真实工具。

## 4. 目录与技术栈

```text
ResearchSpace/
├─ PaperQuery_Frontend/       Vue 3 + TypeScript + Vite
│  ├─ src/router/             页面路由和登录/角色守卫
│  ├─ src/views/              各功能页面
│  ├─ src/api/                后端请求封装
│  ├─ src/stores/             Pinia 状态管理
│  ├─ src/components/         共享组件
│  ├─ config/                 Vite 环境配置
│  └─ public/                 品牌图形、图片等静态资源
├─ PaperQuery_Backend/        Python + FastAPI
│  ├─ main.py                 API 入口，默认端口 8001
│  ├─ vector.py               论文处理/向量化轮询 Worker
│  ├─ core/backend/           路由、数据库模型、CRUD 和服务
│  ├─ core/llm/               DeepSeek/Kimi/智谱/OpenAI 模型适配
│  ├─ core/agent/             聊天和论文处理 Agent
│  ├─ core/vectordb/          Chroma 向量库
│  ├─ core/retrieval/         检索、融合和重排
│  ├─ core/research/          Planner → Executor → Verifier 编排
│  ├─ core/skills/            检索、搜索、阅读、提取、比较、报告、引用核验
│  ├─ core/evidence/          证据组织与格式化
│  ├─ core/artifact/          研究成果构建
│  ├─ migrations/            Alembic 数据库迁移
│  ├─ scripts/               管理员创建、离线翻译安装
│  └─ tests/                 后端测试
├─ docs/design/              设计规格、实施记录、截图与 QA 脚本
├─ DESIGN.md / MOTION.md     视觉和动效规范
├─ start_all.ps1             仓库原有前端/API/Worker 启动脚本
└─ start_frontend_local.ps1  本次添加的前端单独启动入口
```

前端使用 Vue Router、Pinia、Element Plus、Radix Vue、Tailwind/UnoCSS、PDF 和 Markdown 组件，以及 Cytoscape 图谱。后端使用 SQLAlchemy + SQLite 保存用户、论文、研究项目、任务、观点证据、图谱、文稿和协作记录；Chroma 保存向量数据，LangChain 组织模型调用。

## 5. 两条核心业务流程

论文处理：前端上传 → 后端保存论文及元数据 → vector.py 轮询待处理记录 → 解析/切分/模型处理/向量化 → Chroma 和 SQLite 更新 → 前端展示索引状态 → 阅读、问答和引用。

深度研究：用户提交研究目标 → Planner 规划 → Executor 执行注册的 Skills → Verifier 检查 → 保存研究任务、步骤和成果 → 前端展示执行轨迹与成果。

默认向量检索使用 ONNX MiniLM。存在本地 BGE-M3 和 reranker 模型时，可启用 BM25、BGE-M3 与重排增强；缺失时继续使用原有 ONNX 路径。首次向量化仍可能需要下载基础模型，不代表完全离线可用。

## 6. 完整后端还缺什么

1. 独立的 Python 虚拟环境。当前命令行 Python 为 3.14.7；依赖文件锁定了大量 2024 年版本，本次未验证其在 Python 3.14 下的兼容性。可优先用独立 Python 3.11 环境尝试，仍需实际安装验证。
2. 安装 Windows 依赖。`req_win.txt` 去掉了 Linux 专用的 uvloop，但没有列出原启动脚本必需的 Alembic。不要直接把 `requirement.txt` 当成经过验证的 Windows 安装清单。
3. 从 `.env.example` 创建后端 `.env`，填入有效 `DEEPSEEK_API_KEY`，更换 `SECRET_KEY`，确认数据目录配置。`core/llm/LLM.py` 会在 DeepSeek Key 缺失时抛出错误；仅填 OpenAI/Kimi/智谱 Key 也无法绕过当前启动要求。
4. 执行数据库迁移 `python -m alembic upgrade head`。
5. 按需执行 `python -m scripts.create_admin` 创建管理员，密码由交互输入。不提供或假设默认管理员密码。
6. 启动 API 与向量化 Worker，必要时安装离线翻译和增强检索模型。

以下是后续配置完成后的操作顺序，本次没有执行后端安装和启动：

```powershell
cd D:\projects\ResearchSpace\PaperQuery_Backend
# 用已安装的兼容 Python 创建 .venv，例如 py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r req_win.txt
.\.venv\Scripts\python.exe -m pip install alembic
Copy-Item .env.example .env
# 编辑 .env，设置有效的 DeepSeek Key、SECRET_KEY 和数据目录
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m scripts.create_admin
cd ..
.\start_all.ps1
```

以上为启动准备说明，依赖安装仍可能需要处理旧版本兼容性。完整系统就绪后应检查 http://127.0.0.1:8001/health/ready 和 http://127.0.0.1:8001/docs，并使用真实账号和论文验收。

## 7. 日常本地操作

单独启动前端：在项目根目录执行 `powershell -ExecutionPolicy Bypass -File .\start_frontend_local.ps1`，或在前端目录执行 `npm.cmd run dev -- --host 127.0.0.1`。

查看服务日志：`PaperQuery_Frontend/vite-local.log` 与 `vite-local-error.log`。本次后台前端进程 PID 为 4104；停止前请核实 PID 仍属于该项目的 Vite 进程。关掉浏览器不会自动停止后台服务。

更新此分支：`git -C D:\projects\ResearchSpace pull --ff-only`。拉取前先检查并保存自己的本地修改。

建议阅读顺序：前端路由 → views/projects → src/api → 后端 main.py → core/backend/router 与 db/models.py → vector.py 与 core/agent → core/research、skills、retrieval → docs/design。
