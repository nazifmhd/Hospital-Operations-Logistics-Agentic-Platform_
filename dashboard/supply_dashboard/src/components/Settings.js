import React, { useState } from 'react';
import { 
  Settings as SettingsIcon, 
  Bell, 
  Shield, 
  Database, 
  Users, 
  Globe,
  Save,
  RefreshCw
} from 'lucide-react';

const Settings = () => {
  const [settings, setSettings] = useState({
    notifications: {
      lowStock: true,
      criticalAlerts: true,
      userActivity: false,
      systemUpdates: true
    },
    inventory: {
      autoReorder: true,
      reorderThreshold: 10,
      defaultLocation: 'WAREHOUSE',
      batchTracking: true
    },
    security: {
      sessionTimeout: 30,
      passwordExpiry: 90,
      twoFactorAuth: false,
      auditLogging: true
    },
    system: {
      dataRetention: 365,
      backupFrequency: 'daily',
      maintenanceWindow: '02:00',
      timezone: 'UTC-5'
    }
  });

  const handleSave = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v2/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          settings: settings,
          updated_by: 'admin',
          timestamp: new Date().toISOString()
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`✅ Settings saved successfully!\n\nSettings Version: ${result.version}\nLast Updated: ${new Date().toLocaleString()}\n\n${result.changes_count} changes applied.`);
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('❌ Failed to save settings. Please try again.');
    }
  };

  const handleReset = async () => {
    if (window.confirm('Are you sure you want to reset all settings to default?')) {
      try {
        const response = await fetch('http://localhost:8000/api/v2/settings/reset', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            reset_type: 'factory_defaults',
            confirm: true
          })
        });

        if (response.ok) {
          // Reset to default values
          setSettings({
            notifications: {
              lowStock: true,
              criticalAlerts: true,
              userActivity: false,
              systemUpdates: true
            },
            inventory: {
              autoReorder: true,
              reorderThreshold: 10,
              defaultLocation: 'WAREHOUSE',
              batchTracking: true
            },
            security: {
              sessionTimeout: 30,
              passwordExpiry: 90,
              twoFactorAuth: false,
              auditLogging: true
            },
            system: {
              dataRetention: 365,
              backupFrequency: 'daily',
              maintenanceWindow: '02:00',
              timezone: 'UTC-5'
            }
          });
          alert('✅ Settings reset to factory defaults!');
        } else {
          throw new Error('Failed to reset settings');
        }
      } catch (error) {
        console.error('Error resetting settings:', error);
        alert('❌ Failed to reset settings. Please try again.');
      }
    }
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <SettingsIcon className="h-6 w-6 mr-2" />
              System Settings
            </h1>
            <p className="mt-2 text-gray-600">
              Configure system preferences and operational parameters
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleReset}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 flex items-center"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Reset
            </button>
            <button
              onClick={handleSave}
              className="btn btn-primary flex items-center"
            >
              <Save className="h-4 w-4 mr-2" />
              Save Changes
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Notifications Settings */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Bell className="h-5 w-5 mr-2" />
            Notifications
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">Low Stock Alerts</label>
              <input
                type="checkbox"
                checked={settings.notifications.lowStock}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  notifications: { ...prev.notifications, lowStock: e.target.checked }
                }))}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">Critical Alerts</label>
              <input
                type="checkbox"
                checked={settings.notifications.criticalAlerts}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  notifications: { ...prev.notifications, criticalAlerts: e.target.checked }
                }))}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">User Activity</label>
              <input
                type="checkbox"
                checked={settings.notifications.userActivity}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  notifications: { ...prev.notifications, userActivity: e.target.checked }
                }))}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">System Updates</label>
              <input
                type="checkbox"
                checked={settings.notifications.systemUpdates}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  notifications: { ...prev.notifications, systemUpdates: e.target.checked }
                }))}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
            </div>
          </div>
        </div>

        {/* Inventory Settings */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Database className="h-5 w-5 mr-2" />
            Inventory Management
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">Auto Reorder</label>
              <input
                type="checkbox"
                checked={settings.inventory.autoReorder}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  inventory: { ...prev.inventory, autoReorder: e.target.checked }
                }))}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Reorder Threshold</label>
              <input
                type="number"
                value={settings.inventory.reorderThreshold}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  inventory: { ...prev.inventory, reorderThreshold: parseInt(e.target.value) }
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Default Location</label>
              <select
                value={settings.inventory.defaultLocation}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  inventory: { ...prev.inventory, defaultLocation: e.target.value }
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="WAREHOUSE">Warehouse</option>
                <option value="ICU">ICU</option>
                <option value="ER">Emergency Room</option>
                <option value="SURGERY">Surgery</option>
                <option value="PHARMACY">Pharmacy</option>
                <option value="LABORATORY">Laboratory</option>
              </select>
            </div>
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">Batch Tracking</label>
              <input
                type="checkbox"
                checked={settings.inventory.batchTracking}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  inventory: { ...prev.inventory, batchTracking: e.target.checked }
                }))}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
            </div>
          </div>
        </div>

        {/* Security Settings */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Shield className="h-5 w-5 mr-2" />
            Security
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Session Timeout (minutes)</label>
              <input
                type="number"
                value={settings.security.sessionTimeout}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  security: { ...prev.security, sessionTimeout: parseInt(e.target.value) }
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password Expiry (days)</label>
              <input
                type="number"
                value={settings.security.passwordExpiry}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  security: { ...prev.security, passwordExpiry: parseInt(e.target.value) }
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">Two-Factor Authentication</label>
              <input
                type="checkbox"
                checked={settings.security.twoFactorAuth}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  security: { ...prev.security, twoFactorAuth: e.target.checked }
                }))}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">Audit Logging</label>
              <input
                type="checkbox"
                checked={settings.security.auditLogging}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  security: { ...prev.security, auditLogging: e.target.checked }
                }))}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
            </div>
          </div>
        </div>

        {/* System Settings */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Globe className="h-5 w-5 mr-2" />
            System Configuration
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Data Retention (days)</label>
              <input
                type="number"
                value={settings.system.dataRetention}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  system: { ...prev.system, dataRetention: parseInt(e.target.value) }
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Backup Frequency</label>
              <select
                value={settings.system.backupFrequency}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  system: { ...prev.system, backupFrequency: e.target.value }
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="hourly">Hourly</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Maintenance Window</label>
              <input
                type="time"
                value={settings.system.maintenanceWindow}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  system: { ...prev.system, maintenanceWindow: e.target.value }
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Timezone</label>
              <select
                value={settings.system.timezone}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  system: { ...prev.system, timezone: e.target.value }
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="UTC-5">UTC-5 (Eastern)</option>
                <option value="UTC-6">UTC-6 (Central)</option>
                <option value="UTC-7">UTC-7 (Mountain)</option>
                <option value="UTC-8">UTC-8 (Pacific)</option>
                <option value="UTC+0">UTC+0 (GMT)</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
