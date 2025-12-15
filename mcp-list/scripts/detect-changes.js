#!/usr/bin/env node

/**
 * 检测哪些包的版本发生了变化
 * 比较本地 package.json 的版本和 npm registry 上的版本
 */

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function detectChangedPackages() {
  const rootDir = path.resolve(__dirname, '..');
  const packagesDir = path.join(rootDir, 'packages');

  if (!fs.existsSync(packagesDir)) {
    console.log('📦 packages/ 目录不存在，创建中...');
    fs.mkdirSync(packagesDir, { recursive: true });
    return [];
  }

  const packages = fs.readdirSync(packagesDir).filter(pkg => {
    const pkgPath = path.join(packagesDir, pkg);
    return fs.statSync(pkgPath).isDirectory();
  });

  if (packages.length === 0) {
    console.log('📦 packages/ 目录中没有找到任何包');
    return [];
  }

  const changed = [];

  for (const pkg of packages) {
    const pkgPath = path.join(packagesDir, pkg);
    const pkgJsonPath = path.join(pkgPath, 'package.json');

    if (!fs.existsSync(pkgJsonPath)) {
      console.log(`⚠️  跳过 ${pkg}（没有 package.json）`);
      continue;
    }

    try {
      const pkgJson = JSON.parse(fs.readFileSync(pkgJsonPath, 'utf8'));
      const { name, version } = pkgJson;

      if (!name || !version) {
        console.log(`⚠️  跳过 ${pkg}（package.json 缺少 name 或 version）`);
        continue;
      }

      // 检查 npm 上的版本
      let npmVersion = null;
      try {
        npmVersion = execSync(`npm view ${name} version 2>/dev/null`, { encoding: 'utf8' }).trim();
      } catch (error) {
        // 包不存在于 npm，这是新包
        npmVersion = null;
      }

      if (npmVersion === null) {
        // 新包
        changed.push({
          name,
          path: pkgPath,
          localVersion: version,
          npmVersion: 'not published',
          isNew: true
        });
        console.log(`🆕 ${name}: 新包，版本 ${version}`);
      } else if (version !== npmVersion) {
        // 版本变化
        changed.push({
          name,
          path: pkgPath,
          localVersion: version,
          npmVersion: npmVersion,
          isNew: false
        });
        console.log(`📦 ${name}: ${npmVersion} → ${version}`);
      } else {
        console.log(`✅ ${name}: 版本 ${version}（无变化）`);
      }
    } catch (error) {
      console.error(`❌ 处理 ${pkg} 时出错:`, error.message);
    }
  }

  return changed;
}

// 如果直接运行此脚本
if (import.meta.url === `file://${process.argv[1]}`) {
  console.log('🔍 检测包版本变化...\n');

  detectChangedPackages()
    .then(changed => {
      console.log('\n' + '='.repeat(50));
      if (changed.length === 0) {
        console.log('✅ 没有包需要发布');
      } else {
        console.log(`📦 发现 ${changed.length} 个包需要发布：`);
        changed.forEach(pkg => {
          const badge = pkg.isNew ? '🆕' : '📦';
          console.log(`   ${badge} ${pkg.name}: ${pkg.npmVersion} → ${pkg.localVersion}`);
        });
      }
      console.log('='.repeat(50));
    })
    .catch(error => {
      console.error('❌ 错误:', error);
      process.exit(1);
    });
}
