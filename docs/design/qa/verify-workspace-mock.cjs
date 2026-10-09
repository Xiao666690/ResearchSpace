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
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const context=await browser.newContext({viewport:{width:1440,height:1000}});
 // Every API request is fulfilled locally. No browser verification request reaches the backend.
 await context.route(/https?:\/\/(?:127\.0\.0\.1|localhost):8001\/.*/,async r=>{const u=new URL(r.request().url());requests.push({path:u.pathname,method:r.request().method()});const data=fixture(u.pathname);await r.fulfill({status:data===null?503:200,contentType:'application/json',body:JSON.stringify(data===null?{detail:'模拟 PDF 不可用'}:data)});});
 await context.addInitScript(()=>{localStorage.setItem('token','isolated-browser-fixture');localStorage.setItem('username','界面验收');localStorage.setItem('role','admin');});
 const page=await context.newPage();page.on('pageerror',e=>errors.push({url:page.url(),message:e.message}));
 const pages=['dashboard','projects','library','library/notes','knowledge/preview','Chat','research','team','projects/preview/overview','projects/preview/library','projects/preview/chat','projects/preview/research','projects/preview/timeline','projects/preview/compare','projects/preview/evidence','projects/preview/studio','projects/preview/map','projects/preview/collaboration','pdfInfo/preview/preview','note/fullscreen/preview/preview'];
 const results=[];
 for(const width of [1440,390]){
 await page.setViewportSize({width,height:width===390?844:1000});
 for(const path of pages){console.log(width+' '+path);await page.goto('http://127.0.0.1:8080/home/'+path,{waitUntil:'networkidle'});await page.waitForTimeout(600);const result=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,width:document.documentElement.scrollWidth,textLength:document.body.innerText.length}));results.push({path,viewport:width,...result});if(['dashboard','library','projects/preview/overview','projects/preview/evidence','projects/preview/map','pdfInfo/preview/preview'].includes(path))await page.screenshot({path:out+path.replaceAll('/','-')+'-'+width+'.png',fullPage:true});}
 }
 await page.setViewportSize({width:1440,height:1000});await page.goto('http://127.0.0.1:8080/home/dashboard',{waitUntil:'networkidle'});
 await page.keyboard.press('Control+k');await page.locator('#workspace-search').fill('论文');await page.keyboard.press('ArrowDown');const keyboardFocused=await page.evaluate(()=>document.activeElement.classList.contains('command-result'));await page.keyboard.press('Escape');
 const reading=[];for(const m of [0,60,85]){minutes=m;await page.reload({waitUntil:'networkidle'});reading.push({minutes:m,text:await page.locator('.reading-vessel').innerText().catch(()=>page.locator('body').innerText())});}
 await page.setViewportSize({width:390,height:844});await page.getByRole('button',{name:'打开导航',exact:true}).click();const drawer=await page.getByRole('dialog').count();await page.keyboard.press('Escape');
 await page.getByRole('button',{name:'账户菜单'}).click();await page.getByText('退出登录',{exact:true}).click();await page.waitForURL('**/login');const logout=await page.evaluate(()=>!localStorage.getItem('token')&&!localStorage.getItem('username'));
 fs.writeFileSync(out+'workspace-results.json',JSON.stringify({mode:'isolated browser fixtures; no backend requests',results,errors,keyboardFocused,drawer,logout,reading,requests},null,2));
 console.log(JSON.stringify({pages:results.length,errors,overflow:results.filter(x=>x.overflow),keyboardFocused,drawer,logout}));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
