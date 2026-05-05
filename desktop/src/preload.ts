import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('api', {
  request: (method: string, url: string, data?: any) =>
    ipcRenderer.invoke('api:request', method, url, data),
})

declare global {
  interface Window {
    api: {
      request: (method: string, url: string, data?: any) => Promise<any>
    }
  }
}
