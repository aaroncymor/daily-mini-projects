import { createContext, useContext, useState } from 'react';

const ThemeContext = createContext()

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('dark');

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light': 'dark'));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <div className={theme === 'dark' ? 'bg-slate-900 text-white min-h-screen' : 'bg-white text-slate-900 min-h-screen'}>
        {children}
      </div>
    </ThemeContext.Provider>
  );
}

// Custom hook to consume context safely
export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}
