const fs = require('fs-extra');
const path = require('path');

// Paths
const frontendDist = path.join(__dirname, 'frontend', 'dist'); // Vite default output
const destBuild = path.join(__dirname, 'electron-app', 'build');

async function copyBuild() {
  try {
    if (!(await fs.pathExists(frontendDist))) {
      console.error(`Frontend build not found at ${frontendDist}.`);
      console.error('Run `npm --prefix frontend run build` first (or `npm run build-frontend` from the repo root).');
      process.exitCode = 2;
      return;
    }

    // Ensure destination exists
    await fs.ensureDir(destBuild);

    // Remove existing contents to avoid stale files
    await fs.remove(destBuild);
    await fs.copy(frontendDist, destBuild);

    console.log(`Copied frontend build from ${frontendDist} -> ${destBuild}`);
  } catch (err) {
    console.error('Error copying build files:', err);
    process.exitCode = 1;
  }
}

if (require.main === module) {
  copyBuild();
}

module.exports = copyBuild;