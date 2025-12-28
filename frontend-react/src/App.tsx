/**
 * FitTrack Pro - Main App Component
 */

import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useAuthStore, useIsAdmin } from './store/authStore';
import { ThemeProvider } from './context/ThemeContext';
import { DataProvider } from './context/DataContext';

// Pages
// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Water from './pages/Water';
import Nutrition from './pages/Nutrition';
import Workouts from './pages/Workouts';
import Sleep from './pages/Sleep';
import Goals from './pages/Goals';
import Progress from './pages/Progress';
import AdminHome from './pages/admin/Home';
import AdminOverview from './pages/admin/Overview';
import AdminUsers from './pages/admin/Users';
import AdminActivity from './pages/admin/Activity';
import UserActivity from './pages/admin/UserActivity';
import AdminAPIDocs from './pages/admin/APIDocs';
import PlaceholderPage from './pages/PlaceholderPage';

// Protected Route Component
function ProtectedRoute({ children, adminOnly = false }: { children: React.ReactNode; adminOnly?: boolean }) {
  const { isAuthenticated, user } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (adminOnly && user?.role !== 'admin') {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}

// Admin Route - Only accessible by admins
function AdminRoute({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute adminOnly>
      {children}
    </ProtectedRoute>
  );
}

function App() {
  const { checkAuth } = useAuthStore();

  // Check auth on app load
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <ThemeProvider>
      <DataProvider>
        <Router>
          <Toaster
            position="top-right"
            toastOptions={{
              // Custom dark glass styling - matches the overall theme better
              style: {
                background: 'rgba(30, 41, 59, 0.9)',
                color: '#fff',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
              },
            }}
          />

          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected User Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/workouts"
              element={
                <ProtectedRoute>
                  <Workouts />
                </ProtectedRoute>
              }
            />
            <Route
              path="/nutrition"
              element={
                <ProtectedRoute>
                  <Nutrition />
                </ProtectedRoute>
              }
            />
            <Route
              path="/sleep"
              element={
                <ProtectedRoute>
                  <Sleep />
                </ProtectedRoute>
              }
            />
            <Route
              path="/water"
              element={
                <ProtectedRoute>
                  <Water />
                </ProtectedRoute>
              }
            />
            <Route
              path="/goals"
              element={
                <ProtectedRoute>
                  <Goals />
                </ProtectedRoute>
              }
            />
            <Route
              path="/progress"
              element={
                <ProtectedRoute>
                  <Progress />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <PlaceholderPage title="User Profile" emoji="👤" />
                </ProtectedRoute>
              }
            />
            <Route
              path="/notifications"
              element={
                <ProtectedRoute>
                  <PlaceholderPage title="Notifications" emoji="🔔" />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <PlaceholderPage title="Settings" emoji="⚙️" />
                </ProtectedRoute>
              }
            />

            {/* Protected Admin Routes */}
            <Route
              path="/admin"
              element={
                <AdminRoute>
                  <AdminHome />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/overview"
              element={
                <AdminRoute>
                  <AdminOverview />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/users"
              element={
                <AdminRoute>
                  <AdminUsers />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/users/:id/activity"
              element={
                <AdminRoute>
                  <UserActivity />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/activity"
              element={
                <AdminRoute>
                  <AdminActivity />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/api"
              element={
                <AdminRoute>
                  <AdminAPIDocs />
                </AdminRoute>
              }
            />

            {/* Default Redirect */}
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </Router>
      </DataProvider>
    </ThemeProvider>
  );
}

export default App;
