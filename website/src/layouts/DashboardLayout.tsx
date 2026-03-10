import { Outlet, Link, useLocation } from "react-router-dom"
import { Activity, LayoutDashboard, FileText, Settings, LogOut, Search } from "lucide-react"

export default function DashboardLayout() {
  const location = useLocation()

  const navItems = [
    { name: "Dashboard", path: "/", icon: LayoutDashboard },
    { name: "Assessments", path: "/assessments", icon: FileText },
    { name: "Intelligence", path: "/intelligence", icon: Activity },
    { name: "Settings", path: "/settings", icon: Settings },
  ]

  return (
    <div className="flex h-screen w-full bg-slate-50 text-slate-900">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 bg-slate-900 text-white flex flex-col border-r border-slate-800/80 relative z-20 shadow-[4px_0_24px_rgba(0,0,0,0.1)]">
        <div className="h-16 flex items-center px-6 border-b border-white/5">
          <Activity className="h-6 w-6 text-brand-400 mr-2" />
          <span className="font-extrabold text-lg hidden sm:block tracking-tight text-white">Intelli-Credit</span>
        </div>

        <nav className="flex-1 overflow-y-auto py-4">
          <ul className="space-y-1 px-3">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path
              return (
                <li key={item.name}>
                  <Link
                    to={item.path}
                    className={`flex items-center px-4 py-3 rounded-xl transition-all duration-200 group ${isActive
                      ? "bg-brand-500/20 text-brand-300 shadow-sm border border-brand-500/30"
                      : "text-slate-400 hover:bg-white/5 hover:text-white"
                      }`}
                  >
                    <item.icon className={`h-5 w-5 mr-3 transition-colors ${isActive ? "text-brand-400" : "group-hover:text-white text-slate-400"}`} />
                    <span className="text-[14px] font-semibold tracking-wide">{item.name}</span>
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>

        <div className="p-4 border-t border-white/5">
          <button className="flex w-full items-center px-4 py-3 text-sm font-semibold text-slate-400 rounded-xl hover:bg-white/5 hover:text-white transition-all duration-200 tracking-wide">
            <LogOut className="h-5 w-5 mr-3" />
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden bg-slate-50/50">
        {/* Top Header */}
        <header className="h-16 flex-shrink-0 bg-white/70 backdrop-blur-xl border-b border-slate-200/60 flex items-center justify-between px-8 z-10 sticky top-0 shadow-sm">
          <div className="flex flex-1 items-center">
            <div className="relative w-full max-w-md">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-4 w-4 text-slate-400" />
              </div>
              <input
                type="text"
                className="block w-full pl-10 pr-3 py-2 border border-slate-200 rounded-xl leading-5 bg-white shadow-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 sm:text-sm transition duration-200 ease-in-out"
                placeholder="Search borrower, GSTin, PAN..."
              />
            </div>
          </div>
          <div className="ml-4 flex items-center md:ml-6">
            <button className="bg-white p-1 rounded-full text-slate-400 hover:text-slate-500 focus:outline-none">
              <span className="sr-only">View notifications</span>
              <div className="h-8 w-8 rounded-full bg-slate-200 border-2 border-white overflow-hidden">
                <img src="https://ui-avatars.com/api/?name=Credit+Officer&background=0D8ABC&color=fff" alt="User Avatar" />
              </div>
            </button>
          </div>
        </header>

        {/* Dynamic Page Content */}
        <main className="flex-1 relative z-0 overflow-y-auto focus:outline-none">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
