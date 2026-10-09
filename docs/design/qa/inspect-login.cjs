const { chromium } = require('C:/Users/xiaoweiqi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[]; page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8080/login',{waitUntil:'networkidle'});
 await page.screenshot({path:'D:/ResearchSpace/docs/design/qa/login-desktop.png',fullPage:true});
 console.log(JSON.stringify({title:await page.title(),errors,overflow:await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)}));
 await page.setViewportSize({width:390,height:844});
 await page.screenshot({path:'D:/ResearchSpace/docs/design/qa/login-mobile.png',fullPage:true});
 console.log(JSON.stringify({mobileOverflow:await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),inputs:await page.locator('input').count()}));
 await browser.close();
})().catch(e=>{console.error(e.message);process.exit(1)});