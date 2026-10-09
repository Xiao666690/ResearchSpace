# 按钮与弹窗精修

日期：2026-10-09。基于用户提供的历史会话、研究任务、问答输入与思考状态截图。实现位于PaperQuery_Frontend/src/styles/control-polish.css，统一接入主入口。

| Before | After | Why |
|---|---|---|
| 描边按钮缺少表面层次 | 细边缘、内侧高光、两层轻阴影 | 建立可按下的材质与层级 |
| 主次操作外观接近 | 蓝紫渐变主操作、白色次操作、轻量ghost与危险色 | 明确操作优先级与风险 |
| 历史记录为连续通用卡片 | 纸面表层、选中侧线、键盘焦点与工具按钮 | 支持快速定位与操作 |
| 输入区紫色圈偏重 | 单一材料、柔和聚焦光环、上传/发送区分 | 把注意力留给输入内容 |
| 问答等待为小白框 | 稳定宽度、细紫色侧线、真实思考时间 | 让请求状态更明确，正文保持稳定 |
| Radix与Element弹窗不统一 | 统一纸面、标题/页脚边界、关闭按钮及背景遮罩 | 全站浮层具有一致的材料 |
| 手机历史栏挤窄对话 | 独立历史抽屉 | 防止按钮、标题和内容被压缩 |

动效目的为点击反馈与空间说明：指针按压120ms，translateY(1px)/scale(.98)，松开可连续中断；浮层进入220ms/退出160ms，opacity及轻微transform。悬停仅启用于fine pointer/hover设备。键盘开启即时呈现；prefers-reduced-motion禁用位移和过渡。未新增动效库。

## 验证

- vue-tsc与Vite完整构建通过；保留原有大包与自动组件解析警告。
- verify-controls.cjs：隔离浏览器历史数据、Element上传对话框、重命名确认框、手机对话框、按钮按压与减弱动效。
- 上传对话框桌面680px；手机390px视口左右各16px；未溢出。
- 手机历史抽屉358px，焦点位于抽屉内；Escape可关闭，操作按钮保持可见。
- 实际按钮按压matrix(.98,0,0,.98,0,1)，reduced motion过渡0s；无pageerror。
- verify-interactions.cjs：登录校验、失败保留输入、证据详情、图谱、移动阅读与搜索导航回归通过。
- verify-workspace-mock.cjs：整站20页面×2视口布局回归；结果见qa/workspace-results.json。
- 所有功能接口均在独立测试浏览器拦截；不更改真实会话、论文、项目或用户数据。真实模型调用和触屏硬件未在本轮验证。

截图：qa/controls-chat-desktop.png、controls-upload-dialog.png、controls-confirm-dialog.png、controls-dialog-mobile.png。
