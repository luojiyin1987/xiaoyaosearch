import { ElectronAPI } from '@electron-toolkit/preload'

declare global {
  interface Window {
    electron: ElectronAPI
    api: {
      openFile: (filePath: string) => Promise<{ success: boolean; error?: string }>
      selectFolder: () => Promise<{
        success: boolean;
        folderPath?: string;
        canceled?: boolean;
        error?: string
      }>
      openExternal: (url: string) => Promise<{ success: boolean; error?: string }>
    }
  }
}
