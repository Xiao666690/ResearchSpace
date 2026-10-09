# ResearchSpace 编译规范

来源：decisions.md → storyboard.md → 本文。实施文件和下列规范共同构成可追溯定义。细节以根目录 DESIGN.md / MOTION.md 为准。

## 设计库选择
登录：compositions #23 Viewport fill / #16 Weighted right anchor（身份面板），background A2 Directional Light、C8 Vignette，typography 1.1 Full-Width Display 的克制中文变体。Camera 为远景建立空间；Custom 原创宇宙图配静态轨道与轻微环境移动，装饰不接受输入也不改变导航。
首页：Custom 真实阅读沙瓶；图像不够表达动态真实时间，故使用 SVG 裁切填充，主数字始终是准确分钟，60分钟仅为视觉参考刻度，非目标或上限，超额保留准确文字。
浮层：Emil button press / popover origin / modal / drawer recipes。图谱与拖动保持现有实现，不加磁吸光标。

## External Library Decision
不新增运行时动画库。Vue Transition、CSS transitions 与现有 Radix Vue/Element Plus 足够完成本次交互。SVG沙瓶不依赖GPU重型场景。原创位图是渐进增强；加载失败时CSS场景仍成立。WebGL、Three.js、React/Sonner不引入Vue工程。

## 精确约束
工作区 canvas #F7F7F4、surface #FFFFFF、ink #202124、muted #687078、line #E5E7EB、primary #6858D6、gold #B58C53；登录 canvas #080D18、ink #F5F3ED。控件8px，面板12–16px，浮层16px。4px间距基线。桌面导航232px、收起76px；移动端抽屉并遮罩，禁止同时固定展开挤占正文。
按钮反馈 120ms scale(.98)，只对指针按下；浮层180–240ms，退出120–160ms；ease cubic-bezier(.23,1,.32,1)。transform与opacity优先，不使用transition:all。键盘导航即时。

## CSS 实施基线
```css
:root { --rs-canvas:#F7F7F4; --rs-surface:#fff; --rs-ink:#202124; --rs-muted:#687078; --rs-line:#E5E7EB; --rs-primary:#6858D6; --rs-ease:cubic-bezier(.23,1,.32,1); }
.rs-control { transition:transform 120ms var(--rs-ease), background-color 140ms ease, box-shadow 140ms ease; }
.rs-control:active:not(:disabled) { transform:scale(.98); }
.rs-control:focus-visible { outline:2px solid var(--rs-primary); outline-offset:3px; }
@media(prefers-reduced-motion:reduce) { .rs-control { transform:none!important; transition-duration:0ms!important; } }
```
沙瓶SVG与登录环境逻辑的完整实现位于对应组件；两者须记录数据驱动方式、暂停条件、资源回收。登录环境无需JS-required library效果；如新增程序循环必须包含取消帧、可见性和减少动态效果处理。共享进场不包裹整个router-view，避免聊天/PDF持续重挂载。

## 整站适配策略
全局tokens连接旧Less、Tailwind/Radix和Element Plus；共享按钮、输入、下拉、弹窗、Toast先统一；页面自己的布局样式继续拥有几何结构。页面逐个审计，禁止依靠一个高优先级万能选择器假装整站重做。不得覆盖PDF canvas/SVG图谱的内部颜色和尺寸。背景装饰只留登录，阅读与输入表面不透明。

## 检查矩阵
每一类页面：可操作、加载、空状态、失败、禁用、长标题、键盘、手机、reduce-motion。浏览器使用真实API或明确标记的验证数据，不将演示数据放入生产状态。构建必须vue-tsc和Vite通过。图谱、PDF和流式接口受限于真实资料/API时记录验证边界。