import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import InventoryTable from './components/InventoryTable';
import AlertsPanel from './components/AlertsPanel';
import Analytics from './components/Analytics';
import ProfessionalDashboard from './components/ProfessionalDashboard';
import MultiLocationInventory from './components/MultiLocationInventory';
import BatchManagement from './components/BatchManagement';
import UserManagement from './components/UserManagement';
import AIMLDashboard from './components/AIMLDashboard';
import Settings from './components/Settings';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
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
                <Route path="/inventory" element={<InventoryTable />} />
                <Route path="/multi-location" element={<MultiLocationInventory />} />
                <Route path="/batch-management" element={<BatchManagement />} />
                <Route path="/user-management" element={<UserManagement />} />
                <Route path="/ai-ml" element={<AIMLDashboard />} />
                <Route path="/alerts" element={<AlertsPanel />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </main>
          </div>
        </div>
      </Router>
    </SupplyDataProvider>
  );
}

export default App;
