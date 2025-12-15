#!/usr/bin/env node

/**
 * 批量发布所有版本变化的包到 npm
 * 1. 检测版本变化
 * 2. 构建每个包
 * 3. 发布到 npm
 */

import fs from 'fs';
import { execSync } from 'child_process';
import { detectChangedPackages } from './detect-changes.js';

async function buildPackage(pkgPath) {
  console.log(`🔨 构建项目...`);

  try {
    // 检查是否有 build 脚本
    const packageJson = JSON.parse(fs.readFileSync(`${pkgPath}/package.json`, 'utf8'));
    const hasBuildScript = packageJson.scripts && packageJson.scripts.build;

    if (hasBuildScript) {
      execSync('npm run build', {
        cwd: pkgPath,
        stdio: 'inherit'
      });
      console.log(`✅ 构建成功`);
      return true;
    } else {
      console.log(`⚠️  没有 build 脚本，跳过构建`);
      return true;
    }
  } catch (error) {
    console.error(`❌ 构建失败:`, error.message);
    return false;
  }
}

async function publishPackage(pkg) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`🚀 发布 ${pkg.name}`);
  console.log(`📌 版本: ${pkg.npmVersion} → ${pkg.localVersion}`);
  console.log(`📁 路径: ${pkg.path}`);
  console.log('='.repeat(60));

  const originalDir = process.cwd();

  try {
    // 切换到包目录
    process.chdir(pkg.path);

    // 安装依赖（如果需要）
    console.log(`📦 安装依赖...`);
    execSync('npm install', { stdio: 'inherit' });

    // 构建
    const buildSuccess = await buildPackage(pkg.path);
    if (!buildSuccess) {
      throw new Error('构建失败');
    }

    // 发布
    console.log(`\n📤 发布到 npm...`);
    execSync('npm publish --access public', { stdio: 'inherit' });

    console.log(`\n✅ ${pkg.name} v${pkg.localVersion} 发布成功！`);
    console.log(`🔗 https://www.npmjs.com/package/${pkg.name}`);

    return { success: true, pkg };
  } catch (error) {
    console.error(`\n❌ ${pkg.name} 发布失败:`, error.message);
    return { success: false, pkg, error: error.message };
  } finally {
    // 恢复原始目录
    process.chdir(originalDir);
  }
}

async function main() {
  console.log('🚀 MCP 自动发布工具\n');

  // 检测版本变化
  console.log('🔍 检测包版本变化...\n');
  const changed = await detectChangedPackages();

  if (changed.length === 0) {
    console.log('\n✅ 没有包需要发布');
    return;
  }

  console.log(`\n📦 发现 ${changed.length} 个包需要发布\n`);

  // 发布每个包
  const results = [];
  for (const pkg of changed) {
    const result = await publishPackage(pkg);
    results.push(result);
  }

  // 输出总结
  console.log('\n' + '='.repeat(60));
  console.log('📊 发布总结');
  console.log('='.repeat(60));

  const successful = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);

  console.log(`✅ 成功: ${successful.length}`);
  if (successful.length > 0) {
    successful.forEach(r => {
      console.log(`   - ${r.pkg.name} v${r.pkg.localVersion}`);
    });
  }

  if (failed.length > 0) {
    console.log(`\n❌ 失败: ${failed.length}`);
    failed.forEach(r => {
      console.log(`   - ${r.pkg.name}: ${r.error}`);
    });
  }

  console.log('='.repeat(60));

  if (failed.length > 0) {
    console.log('\n⚠️  部分包发布失败，但已成功发布其他包');
    console.log('建议检查失败的包并手动修复\n');
    process.exit(0); // 不阻塞其他包的发布
  }
}

main().catch(error => {
  console.error('❌ 发生错误:', error);
  process.exit(1);
});
