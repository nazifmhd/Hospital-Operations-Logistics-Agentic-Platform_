import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import ComprehensiveInventoryPage from './components/ComprehensiveInventoryPage';
import AlertsPanel from './components/AlertsPanel';
import Analytics from './components/Analytics';
import ProfessionalDashboard from './components/ProfessionalDashboard';
import BatchManagement from './components/BatchManagement';
import UserManagement from './components/UserManagement';
import AIMLDashboard from './components/AIMLDashboard';
import AutonomousWorkflow from './components/AutonomousWorkflow';
import TransferManagement from './components/TransferManagement';
import DepartmentInventory from './components/DepartmentInventory';
import Settings from './components/Settings';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import FloatingAIAssistant from './components/FloatingAIAssistant';
import { SupplyDataProvider } from './context/SupplyDataContext';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <SupplyDataProvider>
      <Router>
        <div className="flex h-screen bg-gray-100">
          {/* Sidebar */}
          <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
          
          {/* Main content */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Header */}
            <Header onMenuClick={() => setSidebarOpen(true)} />
            
            {/* Page content */}
            <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
              <Routes>
                <Route path="/" element={<Navigate to="/professional" replace />} />
                <Route path="/professional" element={<ProfessionalDashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/inventory" element={<ComprehensiveInventoryPage />} />
                <Route path="/departments" element={<DepartmentInventory />} />
                <Route path="/batch-management" element={<BatchManagement />} />
                <Route path="/user-management" element={<UserManagement />} />
                <Route path="/ai-ml" element={<AIMLDashboard />} />
                <Route path="/workflow" element={<AutonomousWorkflow />} />
                <Route path="/transfers" element={<TransferManagement />} />
                <Route path="/alerts" element={<AlertsPanel />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </main>
          </div>
          
          {/* Global Floating AI Assistant */}
          <FloatingAIAssistant />
        </div>
      </Router>
    </SupplyDataProvider>
  );
}

export default App;
