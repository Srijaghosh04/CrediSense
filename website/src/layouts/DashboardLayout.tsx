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
      <aside className="w-64 flex-shrink-0 bg-slate-900 text-white flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-slate-800">
          <Activity className="h-6 w-6 text-blue-500 mr-2" />
          <span className="font-bold text-lg hidden sm:block">Intelli-Credit</span>
        </div>
        
        <nav className="flex-1 overflow-y-auto py-4">
          <ul className="space-y-1 px-3">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path
              return (
                <li key={item.name}>
                  <Link
                    to={item.path}
                    className={`flex items-center px-3 py-2 rounded-md transition-colors ${
                      isActive 
                        ? "bg-blue-600/10 text-blue-400" 
                        : "text-slate-400 hover:bg-slate-800 hover:text-white"
                    }`}
                  >
                    <item.icon className="h-5 w-5 mr-3" />
                    <span className="text-sm font-medium">{item.name}</span>
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>
        
        <div className="p-4 border-t border-slate-800">
          <button className="flex w-full items-center px-3 py-2 text-sm font-medium text-slate-400 rounded-md hover:bg-slate-800 hover:text-white transition-colors">
            <LogOut className="h-5 w-5 mr-3" />
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <header className="h-16 flex-shrink-0 bg-white border-b border-slate-200 flex items-center justify-between px-6 z-10">
          <div className="flex flex-1 items-center">
            <div className="relative w-full max-w-md">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-4 w-4 text-slate-400" />
              </div>
              <input
                type="text"
                className="block w-full pl-10 pr-3 py-2 border border-slate-200 rounded-md leading-5 bg-slate-50 placeholder-slate-400 focus:outline-none focus:bg-white focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition duration-150 ease-in-out"
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
