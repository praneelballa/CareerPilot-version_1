import React from 'react';
import { Compass, Briefcase, User, LayoutDashboard, Settings, Map, FileCheck2, Menu } from 'lucide-react';

export const Layout = ({ activeView, setActiveView, children, candidateName }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  const navItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { id: 'jobs', icon: Briefcase, label: 'Job Feed' },
    { id: 'resume', icon: User, label: 'My Profile' },
    { id: 'applications', icon: FileCheck2, label: 'Applications' },
    { id: 'roadmap', icon: Map, label: 'Career Roadmap' },
    { id: 'settings', icon: Settings, label: 'Settings' },
  ];

  const handleNavClick = (id) => {
    setActiveView(id);
    setMobileMenuOpen(false);
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200 overflow-hidden font-sans">
      {/* Desktop Sidebar */}
      <aside className="hidden md:flex flex-col w-64 border-r border-slate-800/60 bg-slate-950 px-4 py-6 z-10">
        <div className="flex items-center gap-3 px-2 mb-10">
          <div className="p-2 bg-gradient-to-br from-sky-500 to-sky-600 rounded-xl shadow-lg shadow-sky-500/20">
            <Compass className="h-6 w-6 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight text-white">CareerPilot</span>
        </div>

        <nav className="flex-1 space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 text-sm font-medium ${
                  isActive
                    ? 'bg-slate-900 text-white font-semibold'
                    : 'text-slate-400 hover:bg-slate-900/50 hover:text-slate-200'
                }`}
              >
                <Icon className={`h-5 w-5 ${isActive ? 'text-sky-400' : 'text-slate-500'}`} />
                {item.label}
              </button>
            );
          })}
        </nav>

        <div className="mt-auto px-3 py-4 bg-slate-900/40 rounded-2xl border border-slate-800/50 flex items-center gap-3">
          <div className="h-9 w-9 rounded-full bg-sky-950 border border-sky-800 flex items-center justify-center text-sky-400 font-bold">
            {candidateName ? candidateName.charAt(0).toUpperCase() : '?'}
          </div>
          <div className="flex flex-col text-left overflow-hidden">
            <span className="text-sm font-semibold text-slate-200 truncate">{candidateName || 'Guest'}</span>
            <span className="text-[10px] text-emerald-400 font-mono">Engine Online</span>
          </div>
        </div>
      </aside>

      {/* Mobile Topbar */}
      <div className="md:hidden fixed top-0 left-0 right-0 h-16 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <Compass className="h-6 w-6 text-sky-500" />
          <span className="text-lg font-bold text-white">CareerPilot</span>
        </div>
        <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="p-2 text-slate-400">
          <Menu className="h-6 w-6" />
        </button>
      </div>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed inset-0 top-16 bg-slate-950 z-40 p-4 border-t border-slate-800">
          <nav className="flex flex-col space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  className="flex items-center gap-3 px-4 py-3 rounded-xl text-left bg-slate-900 text-slate-200"
                >
                  <Icon className="h-5 w-5 text-sky-400" />
                  {item.label}
                </button>
              );
            })}
          </nav>
        </div>
      )}

      {/* Main Content Area */}
      <main className="flex-1 relative overflow-y-auto pt-16 md:pt-0 bg-[#0B1120]">
        <div className="max-w-3xl mx-auto w-full min-h-full p-4 md:p-8 md:py-10">
          {children}
        </div>
      </main>
    </div>
  );
};