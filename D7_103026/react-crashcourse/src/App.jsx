import { useState } from 'react';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import { TaskManager } from './components/TaskManager';
import { TaskTimer } from './components/TaskTimer';

function Dashboard() {
  const { theme, toggleTheme } = useTheme();
  const [isTracking, setIsTracking] = useState(false);

  return (
    <div className="max-w-xl mx-auto p-6 space-y-6">
      <header className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">React Interview Dashboard</h1>
        <button onClick={toggleTheme} className="px-3 py-1 border rounded">
          Toggle {theme === 'dark' ? 'Light': 'Dark' } Mode
        </button>
      </header>

      <div className="space-y-2">
        <button
          onClick={() => setIsTracking(!isTracking)}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          {isTracking ? "Pause Session" : "Start Session"}
        </button>
        <TaskTimer isTracking={isTracking} />
      </div>

      <TaskManager />
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <Dashboard />
    </ThemeProvider>
  );
}
