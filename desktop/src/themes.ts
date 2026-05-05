export const themes = {
  dark: {
    bg: 'bg-gray-900',
    sidebg: 'bg-gray-800',
    border: 'border-gray-700',
    text: 'text-gray-100',
    secondary: 'text-gray-400',
    hover: 'hover:bg-gray-700',
  },
  light: {
    bg: 'bg-white',
    sidebg: 'bg-gray-100',
    border: 'border-gray-300',
    text: 'text-gray-900',
    secondary: 'text-gray-600',
    hover: 'hover:bg-gray-200',
  },
  nord: {
    bg: 'bg-nord0',
    sidebg: 'bg-nord1',
    border: 'border-nord2',
    text: 'text-nord4',
    secondary: 'text-nord3',
    hover: 'hover:bg-nord2',
  },
  dracula: {
    bg: 'bg-dracula-bg',
    sidebg: 'bg-dracula-bgalt',
    border: 'border-dracula-comment',
    text: 'text-dracula-fg',
    secondary: 'text-dracula-comment',
    hover: 'hover:bg-dracula-selection',
  },
}

export const styleMap = {
  dark: `
    :root {
      --bg-primary: #0f172a;
      --bg-secondary: #1e293b;
      --text-primary: #f1f5f9;
      --text-secondary: #94a3b8;
      --border-color: #334155;
    }
  `,
  light: `
    :root {
      --bg-primary: #ffffff;
      --bg-secondary: #f3f4f6;
      --text-primary: #111827;
      --text-secondary: #6b7280;
      --border-color: #d1d5db;
    }
  `,
  nord: `
    :root {
      --bg-primary: #2e3440;
      --bg-secondary: #3b4252;
      --text-primary: #eceff4;
      --text-secondary: #d8dee9;
      --border-color: #4c566a;
    }
  `,
  dracula: `
    :root {
      --bg-primary: #282a36;
      --bg-secondary: #21222c;
      --text-primary: #f8f8f2;
      --text-secondary: #6272a4;
      --border-color: #44475a;
    }
  `,
}

export type ThemeName = keyof typeof themes
