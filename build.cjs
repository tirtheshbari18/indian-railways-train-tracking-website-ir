const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('--- RailTrack India Vercel Build Script ---');
console.log('Working directory:', process.cwd());

// Detect if we are in the repository root or inside the frontend directory
const inRoot = fs.existsSync(path.join(process.cwd(), 'frontend')) && fs.existsSync(path.join(process.cwd(), 'backend'));
const frontendDir = inRoot ? path.join(process.cwd(), 'frontend') : process.cwd();
const rootDir = inRoot ? process.cwd() : path.join(process.cwd(), '..');

console.log('Frontend directory:', frontendDir);
console.log('Root directory:', rootDir);

// 1. Ensure frontend dependencies are installed
const nodeModulesPath = path.join(frontendDir, 'node_modules');
if (!fs.existsSync(nodeModulesPath)) {
  console.log('Installing frontend dependencies via npm install...');
  execSync('npm install', { cwd: frontendDir, stdio: 'inherit' });
} else {
  console.log('Dependencies already installed in frontend.');
}

// 2. Build the frontend with Vite
console.log('Building frontend production bundle...');
execSync('npm run build', { cwd: frontendDir, stdio: 'inherit' });

// 3. Synchronize output dist folder so it exists in both root/dist and frontend/dist
const frontendDist = path.join(frontendDir, 'dist');
const rootDist = path.join(rootDir, 'dist');

function copyDirRecursive(source, target) {
  if (!fs.existsSync(source)) return;
  if (!fs.existsSync(target)) fs.mkdirSync(target, { recursive: true });
  const entries = fs.readdirSync(source, { withFileTypes: true });
  for (const entry of entries) {
    const srcPath = path.join(source, entry.name);
    const tgtPath = path.join(target, entry.name);
    if (entry.isDirectory()) {
      copyDirRecursive(srcPath, tgtPath);
    } else {
      fs.copyFileSync(srcPath, tgtPath);
    }
  }
}

// Sync to root dist if built in frontend/dist
if (fs.existsSync(frontendDist) && frontendDist !== rootDist) {
  console.log(`Syncing dist from ${frontendDist} to ${rootDist}...`);
  copyDirRecursive(frontendDist, rootDist);
}

// Sync to frontend/dist if built in root dist
if (fs.existsSync(rootDist) && rootDist !== frontendDist) {
  console.log(`Syncing dist from ${rootDist} to ${frontendDist}...`);
  copyDirRecursive(rootDist, frontendDist);
}

console.log('--- Build completed successfully! ---');
