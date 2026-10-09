# ResearchSpace 视觉决策

日期：2026-10-08。模式：由设计者选择；用户确认《星际穿越》的时间与探索意象，允许原创生成图片结合程序动效。领域：科研工作台；范围：所有当前可路由页面及其可见、可点击组件。用户已明确授权写规范后直接升级整站，沿用这项授权继续各阶段。

## 研究与转译
导演：Christopher Nolan；影片：Interstellar。电影只是研究输入，产品布局由真实科研任务决定。时间积累对应每日阅读沙瓶；大尺度与小尺度对照对应登录的宇宙视野和可操作的登录面板；空间深度对应固定导航、文档工作区和临时详情浮层。

研究来源：
- https://www.dneg.com/news/gravitational-lensing-by-spinning-black-holes ：黑洞光线弯曲的视觉结构；抽取不对称光环、深空间与细边缘光，不复刻影片画面。
- https://www.paramountpictures.com/movies/interstellar ：影片及导演的官方来源。
- https://linear.app/docs/projects ：研究工作区的信息秩序，项目、文档与有明确结果的任务。
- https://support.anthropic.com/en/articles/11088861-using-research-on-claude ：研究过程与来源呈现。
- 本地 awesome-design-md 的 Linear、Claude、Notion、Miro 文档：分别抽取秩序、阅读、文档层级、画布表达。
- emil-design-eng：即时反馈、频率预算、可中断与减少动态效果。

## 既有界面审计
现有登录：左文案右白色圆角卡片、紫色渐变、三张功能卡；内页：整屏背景图、多个主色变量、不同边框与圆角。保留研境品牌与业务，不复用原首页壳。
禁止：紫色光球堆叠、三张同构功能卡、大面积透明阅读面板、鼠标跟随光标、阻塞操作的进场、伪数据、工作界面反复电影化转场。
主构图：全出血宇宙观测场，非卡片网格；内页采用观测台、档案架、双页阅读台、证据画布、纵向任务轨道等不同工作构图。

## 可行性边界
Vue 3 + Vite + Radix Vue + Element Plus；保留现有 API、权限、流式协议和阅读计时。新动效优先 CSS/SVG；仅登录一处较强环境视觉，首页一处沙瓶。无需 Three.js 或 WebGL；移动端和 reduced-motion 使用静态构图。后台与账密无变更；不发送付费模型请求作为视觉测试。