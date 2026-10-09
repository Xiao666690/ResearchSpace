const {chromium}=require('C:/Users/xiaoweiqi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');const out='D:/ResearchSpace/docs/design/qa/';
const project={project_id:'preview',name:'探索生成模型的研究边界',description:'从论文到证据，建立清晰、可追溯的研究脉络。',research_goal:'如何让生成模型更准确地理解研究证据？',status:'active',created_by:'界面验收'};
const library={knowledgeID:'preview',knowledgeName:'生成模型与研究方法',knowledgeDescription:'界面验收模拟资料',documentNum:2,vectorNum:28,createTime:'2026-10-08'};
let minutes=37;const requests=[];const errors=[];
function fixture(path){
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
(async()=>{const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});const context=await browser.newContext({viewport:{width:1440,height:1000}});await context.route(/https?:\/\/(?:127\.0\.0\.1|localhost):8001\/.*/,async r=>{const data=fixture(new URL(r.request().url()).pathname);await r.fulfill({status:data===null?503:200,contentType:'application/json',body:JSON.stringify(data||{detail:'模拟PDF不可用'})})});await context.addInitScript(()=>{localStorage.setItem('token','isolated-browser-fixture');localStorage.setItem('username','界面验收');localStorage.setItem('role','admin')});const page=await context.newPage();await page.goto('http://127.0.0.1:8080/home/dashboard',{waitUntil:'networkidle'});console.log(await page.evaluate(()=>({bodyFont:getComputedStyle(document.body).fontFamily,mainFont:getComputedStyle(document.querySelector('.vessel-copy')).fontFamily,scaleFont:getComputedStyle(document.querySelector('.bottle text')).fontSize})));await page.keyboard.press('Control+k');await page.locator('#workspace-search').fill('论文');await page.waitForTimeout(200);console.log({results:await page.locator('.command-result').count()});await page.keyboard.press('ArrowDown');console.log(await page.evaluate(()=>({focused:document.activeElement.outerHTML})));await browser.close()})().catch(e=>{console.error(e);process.exit(1)});