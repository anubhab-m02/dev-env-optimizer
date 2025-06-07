// electron/preload.js
const { contextBridge, ipcRenderer } = require('electron');

// Expose a controlled API to the renderer process (your React app).
contextBridge.exposeInMainWorld('api', {
  /**
   * Set up a listener for receiving system data.
   * @param {function} callback - The function to call with the new data.
   * @returns {function} - A function to call to remove the listener.
   */
  onSystemData: (callback) => {
    const listener = (event, data) => callback(data);
    ipcRenderer.on('system-data', listener);
    
    // Return a cleanup function
    return () => {
      ipcRenderer.removeListener('system-data', listener);
    };
  },

  /**
   * Set up a listener for errors.
   * @param {function} callback - The function to call with the error message.
   * @returns {function} - A function to call to remove the listener.
   */
  onError: (callback) => {
    const listener = (event, message) => callback(message);
    ipcRenderer.on('system-data-error', listener);

    return () => {
      ipcRenderer.removeListener('system-data-error', listener);
    }
  },

  /**
   * Request VS Code settings from the main process.
   * @returns {Promise<object>} - A promise that resolves with the settings or an error.
   */
  getVscodeSettings: () => ipcRenderer.invoke('get-vscode-settings'),

  /**
   * Request AI recommendations from the main process.
   * @param {object} data - Contains systemInfo and processes.
   * @returns {Promise<object>} - A promise that resolves with the recommendations.
   */
  getRecommendations: (data) => ipcRenderer.invoke('get-recommendations', data),
});
