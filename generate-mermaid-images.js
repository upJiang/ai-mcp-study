#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// 读取 Markdown 文件
const mdPath = '/Users/mac/Desktop/studyProject/ai-mcp-study/MCP开发入门与实战-钉钉版.md';
const mdContent = fs.readFileSync(mdPath, 'utf-8');

// 提取所有 Mermaid 代码块
const mermaidRegex = /```mermaid\n([\s\S]*?)```/g;
const mermaidBlocks = [];
let match;

while ((match = mermaidRegex.exec(mdContent)) !== null) {
  mermaidBlocks.push(match[1].trim());
}

console.log(`找到 ${mermaidBlocks.length} 个 Mermaid 图表`);

// 为每个 Mermaid 图表创建 HTML 文件
const outputDir = '/Users/mac/Desktop/studyProject/ai-mcp-study/演示图片';

mermaidBlocks.forEach((mermaidCode, index) => {
  const htmlContent = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mermaid 图表 ${index + 1}</title>
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    mermaid.initialize({
      startOnLoad: true,
      theme: 'default',
      themeVariables: {
        fontSize: '20px',
        fontFamily: 'Arial, sans-serif'
      },
      flowchart: {
        useMaxWidth: false,
        htmlLabels: true,
        curve: 'basis'
      },
      sequence: {
        useMaxWidth: false,
        diagramMarginX: 50,
        diagramMarginY: 10,
        actorMargin: 50,
        width: 150,
        height: 65,
        boxMargin: 10,
        boxTextMargin: 5,
        noteMargin: 10,
        messageMargin: 35
      }
    });
  </script>
  <style>
    * {
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }
    body {
      margin: 0;
      padding: 60px;
      background: white;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
    }
    .mermaid {
      background: white;
      transform: scale(1);
    }
    .mermaid svg {
      max-width: 100%;
      height: auto;
    }
  </style>
</head>
<body>
  <div class="mermaid">
${mermaidCode}
  </div>
</body>
</html>`;

  const htmlPath = path.join(outputDir, `mermaid-${index + 1}.html`);
  fs.writeFileSync(htmlPath, htmlContent);
  console.log(`生成 HTML: mermaid-${index + 1}.html`);
});

// 生成图表名称映射
const chartNames = [
  '01-M×N问题对比',
  '02-M+N问题解决方案',
  '03-Function-Call工作流程',
  '04-MCP架构图',
  '05-STDIO通信原理',
  '06-SSE通信原理',
  '07-HTTP通信原理',
  '08-Figma使用案例',
  '09-Playwright测试流程',
  '10-多MCP协同工作',
  '11-MCP数据流程',
  '12-MCP发展时间线',
  '13-npm发布流程'
];

// 生成截图脚本
const screenshotScript = `#!/usr/bin/env node

const { chromium } = require('playwright');
const path = require('path');

const chartNames = ${JSON.stringify(chartNames, null, 2)};

async function captureScreenshots() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: 1200, height: 800 }
  });

  for (let i = 0; i < ${mermaidBlocks.length}; i++) {
    const htmlPath = path.join(__dirname, '演示图片', \`mermaid-\${i + 1}.html\`);
    const pngPath = path.join(__dirname, '演示图片', \`\${chartNames[i] || ('图表-' + (i + 1))}.png\`);

    console.log(\`截图: \${chartNames[i] || ('图表-' + (i + 1))}\`);

    await page.goto('file://' + htmlPath);
    await page.waitForTimeout(2000); // 等待 Mermaid 渲染

    const mermaidElement = await page.$('.mermaid svg');
    if (mermaidElement) {
      await mermaidElement.screenshot({ path: pngPath });
      console.log(\`✅ 保存: \${pngPath}\`);
    }
  }

  await browser.close();
  console.log('\\n所有图表截图完成！');
}

captureScreenshots().catch(console.error);
`;

fs.writeFileSync(
  path.join('/Users/mac/Desktop/studyProject/ai-mcp-study', 'capture-screenshots.js'),
  screenshotScript
);

console.log('\n✅ HTML 文件生成完成');
console.log('📝 下一步：运行 node capture-screenshots.js 生成图片');
