const {chromium}=require('C:/Users/xiaoweiqi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');const out='D:/ResearchSpace/docs/design/qa/';
const project={project_id:'preview',name:'探索生成模型的研究边界',description:'从论文到证据，建立清晰、可追溯的研究脉络。',research_goal:'如何让生成模型更准确地理解研究证据？',status:'active',created_by:'界面验收'};
const library={knowledgeID:'preview',knowledgeName:'生成模型与研究方法',knowledgeDescription:'界面验收模拟资料',documentNum:2,vectorNum:28,createTime:'2026-10-08'};
let minutes=37;const requests=[];const errors=[];
function baseFixture(path){
 if(path.endsWith('/health/ready'))return {status:'ready'};
 if(path.endsWith('/dashboard/overview'))return {data:{date:'2026-10-08',stats:{libraries:1,documents:2,vectors:28,askCount:4,researchCount:1,uploadCount:2,readingMinutes:minutes},researchGoals:[],myPosts:[],newPosts:[],uploadedPapers:[],readings:[]}};
 if(path.endsWith('/projects'))return {data:[project]};
 if(path.endsWith('/projects/preview'))return {data:project};
 if(path.endsWith('/overview'))return {data:{project,document_count:2,task_count:0,artifact_count:0,event_count:0}};
 if(path.endsWith('/graph'))return {data:{run:null,nodes:[],edges:[]}};
 if(path.endsWith('/getKnowledgeList')||path.endsWith('/getLibraryInfo'))return {status_code:200,data:{knowledgeList:[library],documentNum:2,vectorNum:28,knowledgeNum:1}};
 if(path.endsWith('/team/info'))return {data:{team_name:'研究同行',owner_username:'界面验收',members:[]}};
 if(path.endsWith('/document/getFile'))return null;
 if(path.endsWith('/document/Info'))return {data:{documentID:'preview',documentName:'研究资料',documentStatus:2,documentTags:[],vectorNum:28}};
 if(path.endsWith('/note/getNote'))return {data:{content:''}};
 return {status_code:200,data:[]};
}

const citation={knowledge_id:'preview',document_id:'paperA',page:2,chunk_id:'chunkA'};
function fixture(p){
 if(p.endsWith('/documents'))return {data:[{...citation,document_name:'生成模型的证据边界',document_status:2},{knowledge_id:'preview',document_id:'paperB',document_name:'研究方法与评价',document_status:2}]};
 if(p.endsWith('/evidence'))return {data:[{claim_id:'claimA',title:'准确引用改善研究结论',content:'将输出与原始论文连接，能够提高结论的可核查性。',status:'open',evidence:[{evidence_id:'evA',...citation,page_number:2,text:'Evidence-linked generation improves verifiability. 这里是用于界面验收的长段落，实际产品展示来自真实论文的文本。',stance:'SUPPORT',source_status:'available'}]}]};
 if(p.endsWith('/graph'))return {data:{run:{run_id:'runA',status:'completed'},nodes:[{id:'nodeA',type:'concept',name:'可核查性',confidence:'high',citation,source_status:'available'},{id:'nodeB',type:'method',name:'检索增强生成',confidence:'high',citation,source_status:'available'}],edges:[{id:'edgeA',source:'nodeB',target:'nodeA',type:'SUPPORT',confidence:'high',citation,source_status:'available'}]}};
 if(p.endsWith('/compare'))return {data:[{session_id:'compareA',title:'方法与证据比较',question:'方法如何提高可靠性？',columns:['方法'],rows:[{document_id:'paperA',paper:'生成模型的证据边界',cells:{方法:{value:'检索增强生成',verified:true,citation,source_status:'available'}}}]}]};
 if(p.endsWith('/studio'))return {data:[{studio_id:'studioA',title:'研究综述草稿',document_type:'report',content_markdown:'# 研究结论\n\n这里是可编辑的研究文稿。',created_by:'界面验收',updated_at:'2026-10-08',citations:[]}]};
 return baseFixture(p);
}
(async()=>{const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});const context=await browser.newContext({viewport:{width:1440,height:1000}});let apiCalls=0;
await context.route(/https?:\/\/(?:127\.0\.0\.1|localhost):8001\/.*/,async r=>{apiCalls++;const path=new URL(r.request().url()).pathname;const failed=path.includes('createKnowledge')||path.endsWith('/login');const d=fixture(path);await r.fulfill({status:failed?503:d===null?503:200,contentType:'application/json',body:JSON.stringify(failed?{msg:'模拟网络失败，请重试',detail:'模拟网络失败，请重试'}:d||{detail:'模拟PDF不可用'})})});const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));const checks={};
await page.goto('http://127.0.0.1:8080/login',{waitUntil:'networkidle'});await page.getByPlaceholder('用户名',{exact:true}).fill('browser-preview');await page.getByPlaceholder('密码',{exact:true}).fill('preview-password');await page.getByRole('button',{name:'进入研究空间',exact:true}).click();await page.locator('.rs-auth-message').waitFor();checks.loginError=await page.locator('.rs-auth-message').innerText();checks.loginRetained=await page.getByPlaceholder('用户名',{exact:true}).inputValue();await page.getByRole('button',{name:'显示密码'}).click();checks.reveal=await page.getByPlaceholder('密码',{exact:true}).getAttribute('type');await page.getByRole('button',{name:'立即注册'}).click();await page.getByPlaceholder('确认密码',{exact:true}).fill('different-password');const before=apiCalls;await page.getByRole('button',{name:'创建研究账户',exact:true}).click();checks.mismatchNoRequest=before===apiCalls;checks.mismatch=await page.locator('.rs-auth-message').innerText();
await page.evaluate(()=>{localStorage.setItem('token','isolated-browser-fixture');localStorage.setItem('username','界面验收');localStorage.setItem('role','admin')});await page.goto('http://127.0.0.1:8080/home/library',{waitUntil:'networkidle'});await page.getByRole('button',{name:'＋ 创建知识库',exact:true}).click();await page.locator('#libName').fill('保留失败后的输入');await page.getByRole('dialog').getByRole('button',{name:'创建知识库',exact:true}).click();await page.waitForTimeout(300);checks.failedDraft=await page.locator('#libName').inputValue();checks.failedDialog=await page.getByRole('dialog').count();await page.keyboard.press('Escape');
await page.goto('http://127.0.0.1:8080/home/projects/preview/evidence',{waitUntil:'networkidle'});await page.locator('.evidence-detail').click();checks.evidenceDialog=await page.locator('.evidence-inspector').count().catch(()=>0);await page.screenshot({path:out+'evidence-detail.png',fullPage:true});await page.keyboard.press('Escape');
await page.goto('http://127.0.0.1:8080/home/projects/preview/compare',{waitUntil:'networkidle'});await page.screenshot({path:out+'compare-populated.png',fullPage:true});
await page.goto('http://127.0.0.1:8080/home/projects/preview/map',{waitUntil:'networkidle'});await page.getByRole('button',{name:'放大图谱',exact:true}).click();await page.getByRole('button',{name:'适应画布',exact:true}).click();checks.graphCanvas=await page.locator('.canvas canvas').count();await page.screenshot({path:out+'map-populated.png',fullPage:true});
await page.goto('http://127.0.0.1:8080/home/projects/preview/studio',{waitUntil:'networkidle'});await page.screenshot({path:out+'studio-populated.png',fullPage:true});
await page.setViewportSize({width:390,height:844});await page.goto('http://127.0.0.1:8080/home/pdfInfo/preview/preview',{waitUntil:'networkidle'});checks.paperWidth=await page.locator('.paper-panel').first().evaluate(e=>e.getBoundingClientRect().width);await page.getByRole('button',{name:'翻译、笔记与问答',exact:true}).click();checks.toolsWidth=await page.locator('.tools-panel').evaluate(e=>e.getBoundingClientRect().width);await page.screenshot({path:out+'reader-tools-mobile.png',fullPage:true});
await page.goto('http://127.0.0.1:8080/home/dashboard',{waitUntil:'networkidle'});await page.keyboard.press('Control+k');await page.locator('#workspace-search').fill('论文');await page.keyboard.press('ArrowDown');checks.searchKeyboard=await page.locator('.command-result').evaluate(e=>e===document.activeElement);await page.keyboard.press('Enter');await page.waitForURL('**/home/library');checks.searchNavigation=true;
console.log(JSON.stringify({mode:'browser fixtures only',checks,errors}));fs.writeFileSync(out+'interaction-results.json',JSON.stringify({mode:'browser fixtures only',checks,errors},null,2));await browser.close()})().catch(e=>{console.error(e);process.exit(1)});