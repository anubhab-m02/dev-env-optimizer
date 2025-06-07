// electron/main.js
const { app, BrowserWindow, ipcMain, Notification } = require('electron');
const path = require('path');
const fs = require('fs').promises;
const os = require('os');
const si = require('systeminformation');
const { GoogleGenerativeAI } = require('@google/generative-ai');

// --- Global variables ---
let mainWindow;
let dataInterval;
let isDev;

// --- Main Window Creation ---
async function createWindow() {
    isDev = (await import('electron-is-dev')).default;

    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false,
        },
    });

    const startUrl = isDev
        ? 'http://localhost:3000'
        : `file://${path.join(__dirname, '../build/index.html')}`;
    mainWindow.loadURL(startUrl);

    if (isDev) {
        mainWindow.webContents.openDevTools();
    }

    mainWindow.webContents.on('did-finish-load', startSystemMonitoring);
    mainWindow.on('closed', () => {
        stopSystemMonitoring();
        mainWindow = null;
    });
}

// --- System Monitoring & Notification Logic ---
let highCpuCount = 0;
const CPU_THRESHOLD = 90;
const NOTIFICATION_TRIGGER_COUNT = 3;

const startSystemMonitoring = () => {
    if (dataInterval) clearInterval(dataInterval);

    dataInterval = setInterval(async () => {
        try {
            const [cpu, mem, fs, graphics, osInfo, processes] = await Promise.all([
                si.currentLoad(), si.mem(), si.fsSize(), si.graphics(), si.osInfo(), si.processes()
            ]);

            if (cpu.currentLoad > CPU_THRESHOLD) {
                highCpuCount++;
            } else {
                highCpuCount = 0;
            }

            if (highCpuCount === NOTIFICATION_TRIGGER_COUNT) {
                new Notification({
                    title: "High CPU Usage Alert",
                    body: `CPU load has been over ${CPU_THRESHOLD}% for several seconds.`
                }).show();
                highCpuCount = 0;
            }

            const liveData = {
                cpuLoad: cpu.currentLoad,
                memory: { total: mem.total, used: mem.used, percent: (mem.used / mem.total) * 100 },
                disk: { total: fs[0].size, used: fs[0].used, percent: fs[0].use },
                gpu: graphics.controllers.length > 0 ? { name: graphics.controllers[0].model, memoryTotal: graphics.controllers[0].vram } : null,
                os: `${osInfo.distro} ${osInfo.release}`,
                cpu: { manufacturer: (await si.cpu()).manufacturer, brand: (await si.cpu()).brand },
                topProcesses: processes.list.sort((a, b) => b.mem - a.mem).slice(0, 10).map(p => ({ pid: p.pid, name: p.name, cpu_percent: p.cpu, memory_percent: p.mem }))
            };

            if (mainWindow) mainWindow.webContents.send('system-data', liveData);

        } catch (e) {
            console.error('Error fetching system data:', e);
            if (mainWindow) mainWindow.webContents.send('system-data-error', 'Failed to fetch system data.');
        }
    }, 2000);
};

const stopSystemMonitoring = () => {
    clearInterval(dataInterval);
    dataInterval = null;
};

// --- IPC Handlers ---
function getVscodeSettingsPath() {
    const homeDir = os.homedir();
    switch (process.platform) {
        case 'win32': return path.join(homeDir, 'AppData', 'Roaming', 'Code', 'User', 'settings.json');
        case 'darwin': return path.join(homeDir, 'Library', 'Application Support', 'Code', 'User', 'settings.json');
        case 'linux': return path.join(homeDir, '.config', 'Code', 'User', 'settings.json');
        default: return null;
    }
}

ipcMain.handle('get-vscode-settings', async () => {
    const settingsPath = getVscodeSettingsPath();
    if (!settingsPath) {
        return { error: "Operating system not supported for VS Code settings." };
    }
    try {
        const fileContent = await fs.readFile(settingsPath, 'utf8');
        const jsonContent = fileContent.replace(/\\"|"(?:\\"|[^"])*"|(\/\/.*|\/\*[\s\S]*?\*\/)/g, (m, g) => g ? "" : m);
        return { settings: JSON.parse(jsonContent) };
    } catch (error) {
        if (error.code === 'ENOENT') return { error: "VS Code settings.json file not found." };
        console.error("Error reading VSCode settings:", error);
        return { error: "Failed to read or parse VS Code settings.json." };
    }
});

ipcMain.handle('get-recommendations', async (event, { systemInfo, processes }) => {
    require('dotenv').config({ path: path.join(app.getAppPath(), '.env') });
    if (!process.env.GEMINI_API_KEY) {
        console.error("FATAL ERROR: GEMINI_API_KEY is not set in the .env file.");
        return { error: "Gemini API Key is not configured on the backend." };
    }
    // Updated Gemini Model
    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
    const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash-preview-05-20" });

    if (!systemInfo) {
        return { error: "System information is missing." };
    }
    const prompt = `
        You are an expert system optimization AI. Analyze the following developer environment data and provide a concise, actionable list of recommendations to improve performance, security, and productivity. Focus on high-impact changes.
        System Information:
        - OS: ${systemInfo.os}
        - CPU: ${systemInfo.cpu.manufacturer} ${systemInfo.cpu.brand}
        - CPU Load: ${systemInfo.cpuLoad.toFixed(2)}%
        - Memory Usage: ${(systemInfo.memory.percent).toFixed(2)}%
        - Top 5 Memory-Intensive Processes:
          ${processes.slice(0, 5).map(p => `  - ${p.name}: ${p.memory_percent.toFixed(2)}%`).join('\n')}
        Question: Based on this data, what are the top 5 most critical optimizations? Format the answer as a Markdown list.
    `;
    try {
        const result = await model.generateContent(prompt);
        const response = await result.response;
        return { recommendations: response.text() };
    } catch (e) {
        console.error("Error with Gemini AI:", e);
        return { error: `Error communicating with Gemini AI: ${e.message}` };
    }
});

// --- App Lifecycle ---
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
