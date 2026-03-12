import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from "react-router-dom"
import DashboardLayout from "./layouts/DashboardLayout"
import Dashboard from "./pages/Dashboard"
import Assessments from "./pages/Assessments"
import Assessment from "./pages/Assessment"
import Intelligence from "./pages/Intelligence"
import Settings from "./pages/Settings"
import Login from "./pages/Login"
import { useAuth } from "./contexts/AuthContext"

const ProtectedRoute = () => {
  const { session, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-brand-500 border-t-transparent"></div>
      </div>
    );
  }

  if (!session) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        {/* Protected Routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<DashboardLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="assessments">
              <Route index element={<Assessments />} />
              <Route path="new" element={<Assessment />} />
            </Route>
            <Route path="intelligence" element={<Intelligence />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App
