import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Card,
  CardContent,
  Box,
  Tab,
  Tabs,
  IconButton,
  Chip,
} from '@mui/material';
import {
  Dashboard,
  LocalHospital,
  People,
  MedicalServices,
  Inventory,
  Refresh,
  Assessment,
  AutoAwesome,
  ShoppingCart,
  PersonAdd,
  Assignment,
  Schedule,
} from '@mui/icons-material';
import axios from 'axios';

// Import our custom components
import BedManagementDashboard from './components/BedManagementDashboard';
import EnhancedBedManagementView from './components/EnhancedBedManagementView';
import BedFloorPlanVisualization from './components/BedFloorPlanVisualization';
import StaffAllocationDashboard from './components/StaffAllocationDashboard';
import EquipmentTrackerDashboard from './components/EquipmentTrackerDashboard';
import EquipmentLocationMap from './components/EquipmentLocationMap';
import SupplyInventoryDashboard from './components/SupplyInventoryDashboard';
import ComprehensiveReportingDashboard from './components/ComprehensiveReportingDashboard';
import NotificationCenter from './components/NotificationCenter';
import { NotificationProvider } from './contexts/NotificationContext';

// Import new automated workflow components
import AutomatedSupplyReorderingWorkflow from './components/AutomatedSupplyReorderingWorkflow';
import DynamicStaffReallocationSystem from './components/DynamicStaffReallocationSystem';
import EnhancedShiftManagement from './components/EnhancedShiftManagement';
import EquipmentRequestDispatchInterface from './components/EquipmentRequestDispatchInterface';
import EnhancedAdmissionDischargeAutomation from './components/EnhancedAdmissionDischargeAutomation';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [tabValue, setTabValue] = useState(0);
  const [systemStatus, setSystemStatus] = useState<any>(null);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const fetchSystemStatus = async () => {
    try {
      const response = await axios.get('http://localhost:8000/system/status');
      setSystemStatus(response.data);
    } catch (error) {
      console.error('Error fetching system status:', error);
    }
  };

  useEffect(() => {
    fetchSystemStatus();
    const interval = setInterval(fetchSystemStatus, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
        <Toolbar>
          <LocalHospital sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Hospital Operations Command Center
          </Typography>
          
          {systemStatus && (
            <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
              <Chip
                label={`${systemStatus.agents?.length || 0} Agents`}
                color={systemStatus.overall_status === 'operational' ? 'success' : 'warning'}
                size="small"
                sx={{ mr: 1 }}
              />
              <Chip
                label={systemStatus.overall_status || 'Unknown'}
                color={getStatusColor(systemStatus.overall_status)}
                size="small"
              />
            </Box>
          )}
          
          <NotificationCenter />
          
          <IconButton color="inherit" onClick={fetchSystemStatus}>
            <Refresh />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 2 }}>
        {/* System Overview Cards */}
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 3, mb: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <LocalHospital sx={{ fontSize: 40, color: '#1976d2', mr: 2 }} />
                <Box>
                  <Typography variant="h4" component="div">
                    {systemStatus?.stats?.total_beds || '---'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Beds
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <People sx={{ fontSize: 40, color: '#388e3c', mr: 2 }} />
                <Box>
                  <Typography variant="h4" component="div">
                    {systemStatus?.stats?.total_staff || '---'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Staff Members
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <MedicalServices sx={{ fontSize: 40, color: '#f57c00', mr: 2 }} />
                <Box>
                  <Typography variant="h4" component="div">
                    {systemStatus?.stats?.total_equipment || '---'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Equipment Items
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Inventory sx={{ fontSize: 40, color: '#7b1fa2', mr: 2 }} />
                <Box>
                  <Typography variant="h4" component="div">
                    {systemStatus?.stats?.total_supplies || '---'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Supply Items
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>

        {/* Main Dashboard Tabs */}
        <Card>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs 
              value={tabValue} 
              onChange={handleTabChange} 
              aria-label="hospital dashboard tabs"
              variant="scrollable"
              scrollButtons="auto"
            >
              <Tab 
                icon={<Dashboard />} 
                label="Overview" 
                iconPosition="start"
              />
              <Tab 
                icon={<LocalHospital />} 
                label="Bed Management" 
                iconPosition="start"
              />
              <Tab 
                icon={<LocalHospital />} 
                label="Enhanced Bed View" 
                iconPosition="start"
              />
              <Tab 
                icon={<LocalHospital />} 
                label="Floor Plan" 
                iconPosition="start"
              />
              <Tab 
                icon={<People />} 
                label="Staff Allocation" 
                iconPosition="start"
              />
              <Tab 
                icon={<MedicalServices />} 
                label="Equipment Tracker" 
                iconPosition="start"
              />
              <Tab 
                icon={<MedicalServices />} 
                label="Equipment Map" 
                iconPosition="start"
              />
              <Tab 
                icon={<Inventory />} 
                label="Supply Inventory" 
                iconPosition="start"
              />
              <Tab 
                icon={<Assessment />} 
                label="Analytics & Reports" 
                iconPosition="start"
              />
              <Tab 
                icon={<ShoppingCart />} 
                label="Auto Supply Reordering" 
                iconPosition="start"
              />
              <Tab 
                icon={<AutoAwesome />} 
                label="Dynamic Staff Reallocation" 
                iconPosition="start"
              />
              <Tab 
                icon={<Schedule />} 
                label="Enhanced Shift Management" 
                iconPosition="start"
              />
              <Tab 
                icon={<Assignment />} 
                label="Equipment Request & Dispatch" 
                iconPosition="start"
              />
              <Tab 
                icon={<PersonAdd />} 
                label="Admission & Discharge Automation" 
                iconPosition="start"
              />
            </Tabs>
          </Box>

          <TabPanel value={tabValue} index={0}>
            <Typography variant="h5" gutterBottom>
              Hospital Operations Overview
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              Welcome to the Hospital Operations Command Center. This dashboard provides real-time monitoring
              and management of all hospital operations through our intelligent multi-agent system.
            </Typography>
            
            {systemStatus && (
              <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      System Status
                    </Typography>
                    <Typography variant="body2" paragraph>
                      Overall Status: <Chip 
                        label={systemStatus.overall_status} 
                        color={getStatusColor(systemStatus.overall_status)}
                        size="small"
                      />
                    </Typography>
                    <Typography variant="body2" paragraph>
                      Active Agents: {systemStatus.agents?.length || 0}
                    </Typography>
                    <Typography variant="body2">
                      Last Updated: {new Date(systemStatus.timestamp).toLocaleString()}
                    </Typography>
                  </CardContent>
                </Card>
                
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Recent Alerts
                    </Typography>
                    {systemStatus.alerts?.length > 0 ? (
                      systemStatus.alerts.slice(0, 3).map((alert: any, index: number) => (
                        <Chip
                          key={index}
                          label={alert.message}
                          color={getStatusColor(alert.level)}
                          size="small"
                          sx={{ mr: 1, mb: 1 }}
                        />
                      ))
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No active alerts
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Box>
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <BedManagementDashboard />
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <EnhancedBedManagementView />
          </TabPanel>

          <TabPanel value={tabValue} index={3}>
            <BedFloorPlanVisualization />
          </TabPanel>

          <TabPanel value={tabValue} index={4}>
            <StaffAllocationDashboard />
          </TabPanel>

          <TabPanel value={tabValue} index={5}>
            <EquipmentTrackerDashboard />
          </TabPanel>

          <TabPanel value={tabValue} index={6}>
            <EquipmentLocationMap />
          </TabPanel>

          <TabPanel value={tabValue} index={7}>
            <SupplyInventoryDashboard />
          </TabPanel>

          <TabPanel value={tabValue} index={8}>
            <ComprehensiveReportingDashboard />
          </TabPanel>

          <TabPanel value={tabValue} index={9}>
            <AutomatedSupplyReorderingWorkflow />
          </TabPanel>

          <TabPanel value={tabValue} index={10}>
            <DynamicStaffReallocationSystem />
          </TabPanel>

          <TabPanel value={tabValue} index={11}>
            <EnhancedShiftManagement />
          </TabPanel>

          <TabPanel value={tabValue} index={12}>
            <EquipmentRequestDispatchInterface />
          </TabPanel>

          <TabPanel value={tabValue} index={13}>
            <EnhancedAdmissionDischargeAutomation />
          </TabPanel>
        </Card>
      </Container>
    </Box>
  );
}

const AppWithNotifications = () => (
  <NotificationProvider>
    <App />
  </NotificationProvider>
);

export default AppWithNotifications;
