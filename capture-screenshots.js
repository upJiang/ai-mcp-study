#!/usr/bin/env node

const { chromium } = require('playwright');
const path = require('path');

const chartNames = [
  "01-M×N问题对比",
  "02-M+N问题解决方案",
  "03-Function-Call工作流程",
  "04-MCP架构图",
  "05-STDIO通信原理",
  "06-SSE通信原理",
  "07-HTTP通信原理",
  "08-Figma使用案例",
  "09-Playwright测试流程",
  "10-多MCP协同工作",
  "11-MCP数据流程",
  "12-MCP发展时间线",
  "13-npm发布流程"
];

async function captureScreenshots() {
  // 启动浏览器,设置高DPI
  const browser = await chromium.launch({
    headless: true,
    args: ['--force-device-scale-factor=2']
  });

  // 创建页面,使用更大的视口和2倍像素密度
  const page = await browser.newPage({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 2  // 2倍像素密度,生成Retina级别图片
  });

  for (let i = 0; i < 13; i++) {
    const htmlPath = path.join(__dirname, '演示图片', `mermaid-${i + 1}.html`);
    const pngPath = path.join(__dirname, '演示图片', `${chartNames[i] || ('图表-' + (i + 1))}.png`);

    console.log(`截图: ${chartNames[i] || ('图表-' + (i + 1))}`);

    await page.goto('file://' + htmlPath);
    await page.waitForTimeout(3000); // 等待 Mermaid 完全渲染

    const mermaidElement = await page.$('.mermaid svg');
    if (mermaidElement) {
      await mermaidElement.screenshot({
        path: pngPath,
        type: 'png',
        omitBackground: false
      });
      console.log(`✅ 保存: ${pngPath}`);
    }
  }

  await browser.close();
  console.log('\n所有图表截图完成！');
}

captureScreenshots().catch(console.error);
