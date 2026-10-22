const puppeteer = require('puppeteer');
const path = require('path');
const FILE = 'file://' + encodeURI(path.join(__dirname, 'index.html'));
const OUT = path.join(__dirname, '..', 'screenshots', 'demo');
const fs = require('fs');
fs.mkdirSync(OUT, { recursive: true });
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: 'new', args: ['--no-sandbox', '--font-render-hinting=none'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 430, height: 932, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const errs = [];
  page.on('pageerror', e => errs.push('PAGEERROR: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errs.push('CONSOLE: ' + m.text()); });

  await page.goto(FILE, { waitUntil: 'networkidle2', timeout: 30000 });
  await sleep(700);
  await page.screenshot({ path: path.join(OUT, '01-hero.png') });

  const profile = await page.evaluate(() => ({
    bmr: document.getElementById('bmrV').textContent,
    tdee: document.getElementById('tdeeV').textContent,
    target: document.getElementById('targetV').textContent,
  }));

  // 逐个吃法采集指标
  const readings = [];
  for (let i = 0; i < 5; i++) {
    await page.evaluate(n => document.querySelectorAll('#plans .plan')[n].click(), i);
    await sleep(280);
    readings.push(await page.evaluate(() => ({
      plan: document.querySelector('#plans .plan.on .tt').textContent,
      kcal: document.getElementById('mKcal').textContent,
      pro: document.getElementById('mPro').textContent,
      gap: document.getElementById('mGap').textContent,
      unit: document.getElementById('unitBig').textContent,
      verdict: document.querySelector('#verdict .t').textContent,
      cls: document.getElementById('verdict').className,
    })));
  }

  // 回到「照抄窦月法」截图（最有戏剧性）
  await page.evaluate(() => document.querySelectorAll('#plans .plan')[0].click());
  await sleep(300);
  await page.evaluate(() => document.getElementById('s2').scrollIntoView({ block: 'center' }));
  await sleep(450);
  await page.screenshot({ path: path.join(OUT, '02-plans.png') });

  await page.evaluate(() => document.getElementById('s3').scrollIntoView({ block: 'center' }));
  await sleep(450);
  await page.screenshot({ path: path.join(OUT, '03-verdict-risk.png') });

  // 点「套用医生改良版」
  await page.evaluate(() => document.getElementById('fixBtn').click());
  await sleep(700);
  await page.evaluate(() => document.getElementById('s3').scrollIntoView({ block: 'center' }));
  await sleep(450);
  const afterFix = await page.evaluate(() => ({
    plan: document.querySelector('#plans .plan.on .tt').textContent,
    kcal: document.getElementById('mKcal').textContent,
    pro: document.getElementById('mPro').textContent,
    verdict: document.querySelector('#verdict .t').textContent,
  }));
  await page.screenshot({ path: path.join(OUT, '04-verdict-good.png') });

  // 改体重看联动
  await page.evaluate(() => {
    const w = document.getElementById('wgt'); w.value = '75';
    w.dispatchEvent(new Event('input'));
  });
  await sleep(350);
  const afterWeight = await page.evaluate(() => ({
    bmr: document.getElementById('bmrV').textContent,
    verdict: document.querySelector('#verdict .t').textContent,
  }));

  // 日历打卡
  await page.evaluate(() => {
    const b = document.querySelectorAll('#cal button');
    for (let i = 0; i < 6; i++) if (b[i]) b[i].click();
  });
  await sleep(500);
  await page.evaluate(() => document.getElementById('s4').scrollIntoView({ block: 'center' }));
  await sleep(450);
  const stats = await page.evaluate(() => ['st1', 'st2', 'st3'].map(i => document.getElementById(i).textContent));
  await page.screenshot({ path: path.join(OUT, '05-calendar.png') });

  await page.evaluate(() => document.getElementById('s5').scrollIntoView({ block: 'start' }));
  await sleep(450);
  await page.screenshot({ path: path.join(OUT, '06-data.png') });

  // 桌面
  const p2 = await browser.newPage();
  await p2.setViewport({ width: 1280, height: 900 });
  await p2.goto(FILE, { waitUntil: 'networkidle2' });
  await sleep(700);
  await p2.screenshot({ path: path.join(OUT, '07-desktop.png') });

  console.log(JSON.stringify({ profile, readings, afterFix, afterWeight, stats, errors: errs }, null, 1));
  await browser.close();
})();
