const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');

function createWindow() {
	const win = new BrowserWindow({
		width: 800,
		height: 600,
		webPreferences: {
			nodeIntegration: true,
			contextIsolation: false,
		},
	});

	// In development you can set ELECTRON_START_URL to your dev server (e.g. http://localhost:3000)
	const startUrl = process.env.ELECTRON_START_URL;
	const prodIndex = path.join(__dirname, 'build', 'index.html');

	if (startUrl) {
		win.loadURL(startUrl);
	} else if (fs.existsSync(prodIndex)) {
		// Load the built React app copied into electron-app/build
		win.loadFile(prodIndex);
	} else {
		// Fallback: load index.html in electron-app (useful if you manually put files there)
		win.loadFile(path.join(__dirname, 'index.html'));
	}
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
	if (process.platform !== 'darwin') {
		app.quit();
	}
});

app.on('activate', () => {
	if (BrowserWindow.getAllWindows().length === 0) {
		createWindow();
	}
});