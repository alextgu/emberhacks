const { app, BrowserWindow, session } = require("electron");
const path = require("path");
const fs = require("fs");

app.commandLine.appendSwitch("enable-media-stream");

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    backgroundColor: "#0a0a0f",
    autoHideMenuBar: true,
    titleBarStyle: "hiddenInset",
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: false,
    },
  });

  const isDev = process.env.NODE_ENV === "development";
  const devURL = "http://localhost:5173";
  const prodPath = path.join(__dirname, "build", "index.html");

  if (isDev) {
    win.loadURL(devURL);
    win.webContents.openDevTools();
  } else if (fs.existsSync(prodPath)) {
    win.loadFile(prodPath);
  } else {
    console.error("❌ Build not found. Run `npm run build` first.");
  }
}

app.whenReady().then(() => {
  session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
    if (permission === "media" || permission === "microphone") {
      callback(true);
    } else {
      callback(false);
    }
  });

  createWindow();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
