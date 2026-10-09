# 登录实施规范与原创资源

依据 compiled-spec.md：compositions #23 Viewport fill / #16 Weighted right anchor，background A2 Directional Light / C8 Vignette，typography 1.1 Full-Width Display 的中文变体。Custom 原创宇宙图与 CSS 轨道为唯一强环境效果。构图为左侧光环远景、右侧身份控制台、底部连续功能注释。

login.vue 保留真实 login/register API、busy 防重复、密码确认及团队申请。补充可见字段标签、行内 aria-live 成败状态、忙碌时禁止模式切换。异步成功由实际接口触发。

LoginCosmosVisual.vue 使用 CSS 环境动画，无 requestAnimationFrame。暂停按钮、页面不可见、系统 reduce-motion 均暂停；卸载移除 media/visibility 监听。标题裁切700ms，面板侧移12px/440ms。常规按钮按压120ms。820px以下单列，480px以下输入16px、功能注释纵排；位图失败保留深蓝背景及轨道。

资源：`PaperQuery_Frontend/public/visuals/research-eclipse.png`。2026-10-08 使用内置 image_gen 生成（非CLI），原创视觉，并非电影剧照。无需外部字体或重型动画库。

最终提示词：Use case: stylized-concept. Asset type: cinematic ResearchSpace login backdrop. Original widescreen 16:9 astrophysical fine-art image, dark blue-black deep space with a monumental black eclipse at 42% horizontal position, a thin brilliant warm ivory and muted gold accretion ring bending light around it, atmospheric dust and restrained realistic distant stars. A sense of immense time, silence and scientific exploration, physically inspired gravitational lensing, refined film photography lighting. Composition: big luminous ring in upper-left-center, lower-left dark negative space for headline, right third extremely dark and low-detail for login form; keep the whole image sophisticated and not busy. No spacecraft, people, text, logos, labels, film characters, movie still imitation or watermark. Wide panoramic framing, deep navy #080D18, warm ivory, restrained gold #B58C53. High-quality original environmental asset.

验证：vue-tsc --noEmit 通过；视觉浏览器和真实API检查由整站验证完成。
