import { Outlet, Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, FolderOpen, Database } from 'lucide-react'

const NAV = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/projects',  icon: FolderOpen,      label: 'Projects'  },
]

const Layout = () => {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex">

      {/* ── Sidebar ── */}
      <aside className="fixed left-0 top-0 h-full w-60 bg-[#0F172A] flex flex-col z-30">
        {/* Logo */}
        <div className="px-6 py-5 border-b border-white/[0.06]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center">
              <Database size={16} className="text-white" />
            </div>
            <span className="text-white font-semibold text-[15px] tracking-tight">DataSense AI</span>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-0.5">
          {NAV.map(({ to, icon: Icon, label }) => {
            const active = location.pathname.startsWith(to)
            return (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  active
                    ? 'bg-indigo-500/20 text-indigo-300'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.05]'
                }`}
              >
                <Icon size={18} className={active ? 'text-indigo-400' : ''} />
                {label}
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="px-4 py-4 border-t border-white/[0.06]">
          <p className="text-xs text-slate-600 font-medium">v1.0.0</p>
        </div>
      </aside>

      {/* ── Main area ── */}
      <div className="flex-1 ml-60 flex flex-col min-h-screen">

        {/* ── Page Content ── */}
        <main className="flex-1 px-8 py-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Layout
