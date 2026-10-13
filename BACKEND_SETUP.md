# ResearchSpace 完整后端配置与验证

最后验证：2026-10-12。项目：D:\projects\ResearchSpace，分支 Xiao1009。

## 你现在只需要做什么

环境、数据库、基础向量模型、所有主要接口和后台文档处理代码已准备。你无需再次安装依赖。

在 PowerShell 中执行：

```powershell
cd D:\projects\ResearchSpace
powershell -ExecutionPolicy Bypass -File .\configure_api.ps1
# 在隐藏输入提示中粘贴你的 DeepSeek API Key，按回车。
powershell -ExecutionPolicy Bypass -File .\start_all.ps1
```

或者直接编辑 `PaperQuery_Backend/.env`，只填入：

```dotenv
DEEPSEEK_API_KEY=你的真实密钥
```

其他参数已配置：

```dotenv
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-flash
DEEPSEEK_THINKING=disabled
TRANSLATION_PROVIDER=deepseek
```

`deepseek-chat` 已过期：官方公告说明该名称在 2026-07-24 后退役。当前配置使用官方文档的 `deepseek-flash`，并通过 `extra_body` 显式设置非思考模式，兼容当前内容流和 JSON 解析。可按实际需要将模型名改为官方支持的其他模型。

官方资料：https://api-docs.deepseek.com/ 、https://api-docs.deepseek.com/guides/thinking_mode/ 、https://api-docs.deepseek.com/news/news260424/

网页：http://127.0.0.1:8080/login
API 文档：http://127.0.0.1:8001/docs
管理员账号及密码沿用聊天中已提供的本地账号，数据库和 JWT 签名密钥已保留。

## 填 Key 后如何验收

以下命令会向你配置的 DeepSeek 接口发起一次少量 token 的真实请求，用于验证 Key、Base URL 和模型名；按服务商规则可能产生少量费用：

```powershell
cd D:\projects\ResearchSpace\PaperQuery_Backend
.\.venv\Scripts\python.exe -m scripts.check_backend --check-api
```

成功时 `live_api_verified` 为 true。没有 `--check-api` 时只检查本地环境，不发送付费请求。检查不会打印 Key，也不会把 Key 保存到检查报告。

然后在页面进行：新建论文库 → 上传有文本层的 PDF → 等待索引完成 → 打开原文 → 提问并检查引用跳页 → 新建研究项目并关联论文 → 比较/图谱/深度研究/成果工作室。图谱和比较需要已索引的论文，比较至少需要两篇；证据和引用来源必须来自该项目真实资料。

## 已实际完成的配置

- 独立 Python 3.12.14 `.venv`，依赖已安装并通过 `pip check`。
- 完整依赖清单：`requirements-win-full.txt` 与 `requirements-win-full.lock.txt`；不再使用不适合 Windows 的旧大而杂依赖文件来初始化。
- SQLite 数据库四个 Alembic 迁移已完成，本地管理员和默认团队已保留。
- ONNX MiniLM 基础向量模型已下载到项目 `res` 目录，真实 CPU 推理产生 384 维向量。
- tiktoken 分词器已缓存到项目目录，首次填写 Key 后不再依赖临时目录中的缓存。
- API 和 Worker 共用配置与向量模型实现，数据路径根据后端目录解析，可从任意工作目录启动。
- 翻译和旧版流式问答改为使用同一份 DeepSeek Key，中英互译不需要腾讯密钥或 Argos 安装包。
- 默认启用 ONNX 语义检索 + BM25 关键词检索 + RRF 融合，使用真实可追溯的索引记录 ID。
- 向量索引使用确定性 ID，Worker 重试不会反复添加相同文本块。
- Worker 更新按论文、知识库和工作空间限定范围，并在事务中重算该库索引统计；同一 PDF 放到两个库不会错误地同步处理状态。
- 修复无效模型 JSON 引发的无限重试，设置模型超时与有限重试。
- 上传前验证 PDF 格式、大小、密码保护和文本层；无文本扫描件明确提示先 OCR，避免进入永不完成的索引队列。
- 未填 Key 时完整 API 仍能登录和管理数据；调用 AI 返回清晰的 503 配置提示。填入 Key 后重启，启动脚本会启动文档 Worker。
- 启动脚本识别并替换本项目旧的账户专用服务，不会把任意占用端口的其他服务当成本项目。
- 后端和前端仅监听本机 127.0.0.1。

## 验证结果与范围

| 验证项 | 本次结果 |
| --- | --- |
| 完整 API 启动、65 组路径注册 | 已验证 |
| 管理员登录、身份、首页、项目和论文库请求 | 真实本地服务返回 200 |
| 注册、新用户登录、错误密码拒绝 | 已验证，测试账号已清理 |
| CPU 向量模型下载与推理 | 真实模型通过 |
| PDF 上传、Worker 索引、PDF 下载、重复索引去重、跨知识库状态 | 隔离数据库 + 真实 PDF + 真实 Chroma/ONNX 模型通过 |
| 中英互译、普通/流式模型 SDK 协议 | 测试替身/MockTransport 通过，没有调用真实模型服务 |
| 比较、证据引用、图谱、成果编辑、协作、时间线、删除来源后的引用状态 | 自动测试通过，模型生成使用测试替身 |
| 联网论文搜索 | 真实 arXiv 搜索成功，取得论文结果 |
| 后端回归测试 | 15 项全部通过 |
| DeepSeek 真实 Key、余额、服务可达性、实际生成质量 | 当前未填 Key，尚未验收 |

`/health/ready` 检查组件是否初始化，不能证明 Key 或余额有效。未填 Key 时它会返回 503；填 Key 并正常启动后，仍需要上面的 `--check-api` 命令与真实资料验收。

## 日常管理

```powershell
# 启动/重启完整前后端，填 Key 后用这条重新加载配置
powershell -ExecutionPolicy Bypass -File D:\projects\ResearchSpace\start_all.ps1

# 停止由本项目管理的服务
powershell -ExecutionPolicy Bypass -File D:\projects\ResearchSpace\stop_all.ps1

# 本地检查（不调用模型 API）
cd D:\projects\ResearchSpace\PaperQuery_Backend
.\.venv\Scripts\python.exe -m scripts.check_backend
.\.venv\Scripts\python.exe -m scripts.manage_local status
.\.venv\Scripts\python.exe -m pytest tests -q
```

日志：`PaperQuery_Backend/full-api.log`、`full-api-error.log`、`vector-worker.log`、`vector-worker-error.log`；前端日志在 `PaperQuery_Frontend/vite-local.log` 和 `vite-local-error.log`。

`setup_backend.ps1` 用于未来重建环境，本次无需运行。它使用锁定的依赖并保留已有 `.env`。在其他机器上可通过 `-PythonPath` 指定 Python 3.12。

## 仍然存在的明确功能边界

- 扫描 PDF 需要先 OCR；项目没有自带完整 OCR 管线，仅填 LLM Key 无法解决文档没有文本层的问题。
- 默认混合检索已可用。可选 BGE-M3 + 大型 reranker 未下载或启用；它们属于额外本地模型增强，不是默认功能的启动条件。
- Argos 离线英中翻译保留为可选模式（`TRANSLATION_PROVIDER=offline`），需要另行安装其依赖和语言包；当前单 Key 模式使用 DeepSeek。
- Kimi、智谱等独立模型仍需各自 Key，未配置的模型不会假装可用。
- 论文搜索、外部 PDF 导入依赖网络和来源服务；直接导入目前限 arXiv PDF，其他来源请下载后上传。
- 量子工具适配器是仓库原有接口骨架，没有真实外部工具实现；这项不能靠填写 DeepSeek Key 自动补齐。

这些边界不会被测试替身或健康状态伪装成已实现。当前界面主要功能的本地运行条件已补齐，真实模型能力需要有效密钥与真实资料才能最终验收。
