import React, { useState, useEffect } from 'react';
import { fetchSystemHealth } from './services/healthService';
import { HealthCard } from './components/HealthCard';
import { Compass } from 'lucide-react';

function App() {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const verifyBackend = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchSystemHealth();
      setHealthData(data);
    } catch (err) {
      setError(err.message || 'Unable to establish communication with backend API.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    verifyBackend();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-between p-6">
      <header className="max-w-6xl mx-auto w-full flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-sky-500/10 border border-sky-500/30 rounded-lg">
            <Compass className="h-6 w-6 text-sky-400 animate-pulse" />
          </div>
          <span className="text-xl font-bold tracking-tight text-white">
            CareerPilot<span className="text-sky-400">AI</span>
          </span>
        </div>
        <div className="text-xs font-mono text-slate-500">Phase 1: Project Foundation</div>
      </header>

      <main className="max-w-6xl mx-auto w-full flex flex-col items-center justify-center flex-1 my-12">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-slate-100 sm:text-4xl">
            System Initialization Check
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            Validating client-server pipeline, operational schemas, and async network layer.
          </p>
        </div>

        <HealthCard
          healthData={healthData}
          loading={loading}
          error={error}
          onRefresh={verifyBackend}
        />
      </main>

      <footer className="max-w-6xl mx-auto w-full text-center border-t border-slate-800 pt-4 text-xs text-slate-600">
        CareerPilotAI &copy; {new Date().getFullYear()} &mdash; Autonomous Career Intelligence Runtime
      </footer>
    </div>
  );
}

export default App;