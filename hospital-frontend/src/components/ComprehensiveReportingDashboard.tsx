import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  LocalHospital,
  People,
  Inventory,
  Assessment,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import axios from 'axios';

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
      id={`reporting-tabpanel-${index}`}
      aria-labelledby={`reporting-tab-${index}`}
      {...other}
    >
      {value === index && <Box>{children}</Box>}
    </div>
  );
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const ComprehensiveReportingDashboard: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [capacityData, setCapacityData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCapacityData();
    // Auto-refresh every 2 minutes
    const interval = setInterval(fetchCapacityData, 120000);
    return () => clearInterval(interval);
  }, []);

  const fetchCapacityData = async () => {
    try {
      setError(null);
      const response = await axios.get('http://localhost:8000/api/v2/analytics/capacity-utilization');
      setCapacityData(response.data);
    } catch (error) {
      console.error('Error fetching capacity data:', error);
      setError('Failed to load capacity data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading comprehensive reports...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" action={
          <button onClick={fetchCapacityData}>Retry</button>
        }>
          {error}
        </Alert>
      </Box>
    );
  }

  const BedUtilizationTab = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Bed Capacity Utilization by Department
      </Typography>
      
      {/* Summary Cards */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 4 }}>
        <Card sx={{ minWidth: 250, flex: '1 1 250px' }}>
          <CardContent>
            <Box display="flex" alignItems="center">
              <LocalHospital color="primary" sx={{ mr: 2 }} />
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Total Beds
                </Typography>
                <Typography variant="h4">
                  {capacityData?.bed_utilization?.reduce((sum: number, item: any) => sum + item.total_beds, 0) || 0}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        <Card sx={{ minWidth: 250, flex: '1 1 250px' }}>
          <CardContent>
            <Box display="flex" alignItems="center">
              <People color="success" sx={{ mr: 2 }} />
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Occupied Beds
                </Typography>
                <Typography variant="h4">
                  {capacityData?.bed_utilization?.reduce((sum: number, item: any) => sum + item.occupied_beds, 0) || 0}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        <Card sx={{ minWidth: 250, flex: '1 1 250px' }}>
          <CardContent>
            <Box display="flex" alignItems="center">
              <Inventory color="info" sx={{ mr: 2 }} />
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Available Beds
                </Typography>
                <Typography variant="h4">
                  {capacityData?.bed_utilization?.reduce((sum: number, item: any) => sum + item.available_beds, 0) || 0}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        <Card sx={{ minWidth: 250, flex: '1 1 250px' }}>
          <CardContent>
            <Box display="flex" alignItems="center">
              <Assessment color="warning" sx={{ mr: 2 }} />
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Avg Utilization
                </Typography>
                <Typography variant="h4">
                  {capacityData?.bed_utilization?.length ? 
                    Math.round(capacityData.bed_utilization.reduce((sum: number, item: any) => sum + item.utilization_rate, 0) / capacityData.bed_utilization.length) 
                    : 0}%
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Chart */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Bed Utilization by Department
          </Typography>
          <Box sx={{ height: 400 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={capacityData?.bed_utilization || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="department" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="occupied_beds" fill="#82ca9d" name="Occupied" />
                <Bar dataKey="available_beds" fill="#8884d8" name="Available" />
              </BarChart>
            </ResponsiveContainer>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );

  const EquipmentUtilizationTab = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Equipment Utilization Analysis
      </Typography>

      {/* Equipment Charts */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 4 }}>
        <Card sx={{ flex: '2 1 600px', minWidth: 600 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Equipment Status by Type
            </Typography>
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={capacityData?.equipment_utilization || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="equipment_type" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="in_use" fill="#82ca9d" name="In Use" />
                  <Bar dataKey="available" fill="#8884d8" name="Available" />
                  <Bar dataKey="maintenance" fill="#ffc658" name="Maintenance" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
        <Card sx={{ flex: '1 1 300px', minWidth: 300 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Overall Status Distribution
            </Typography>
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={[
                      { name: 'In Use', value: capacityData?.equipment_utilization?.reduce((sum: number, item: any) => sum + item.in_use, 0) || 0 },
                      { name: 'Available', value: capacityData?.equipment_utilization?.reduce((sum: number, item: any) => sum + item.available, 0) || 0 },
                      { name: 'Maintenance', value: capacityData?.equipment_utilization?.reduce((sum: number, item: any) => sum + item.maintenance, 0) || 0 }
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {[
                      { name: 'In Use', value: capacityData?.equipment_utilization?.reduce((sum: number, item: any) => sum + item.in_use, 0) || 0 },
                      { name: 'Available', value: capacityData?.equipment_utilization?.reduce((sum: number, item: any) => sum + item.available, 0) || 0 },
                      { name: 'Maintenance', value: capacityData?.equipment_utilization?.reduce((sum: number, item: any) => sum + item.maintenance, 0) || 0 }
                    ].map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );

  const StaffUtilizationTab = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Staff Allocation & Utilization
      </Typography>

      {/* Staff Summary Cards */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 4 }}>
        <Card sx={{ minWidth: 250, flex: '1 1 250px' }}>
          <CardContent>
            <Box display="flex" alignItems="center">
              <People color="primary" sx={{ mr: 2 }} />
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Total Staff
                </Typography>
                <Typography variant="h4">
                  {capacityData?.staff_utilization?.reduce((sum: number, item: any) => sum + item.total_staff, 0) || 0}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        <Card sx={{ minWidth: 250, flex: '1 1 250px' }}>
          <CardContent>
            <Box display="flex" alignItems="center">
              <People color="success" sx={{ mr: 2 }} />
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Active Staff
                </Typography>
                <Typography variant="h4">
                  {capacityData?.staff_utilization?.reduce((sum: number, item: any) => sum + item.active_staff, 0) || 0}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Staff Chart */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Staff Status by Department
          </Typography>
          <Box sx={{ height: 400 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={capacityData?.staff_utilization || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="department" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="active_staff" fill="#82ca9d" name="Active Staff" />
                <Bar dataKey="total_staff" fill="#8884d8" name="Total Staff" />
              </BarChart>
            </ResponsiveContainer>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="reporting dashboard tabs">
          <Tab label="Bed Utilization" />
          <Tab label="Equipment Analysis" />
          <Tab label="Staff Allocation" />
        </Tabs>
      </Box>
      <TabPanel value={tabValue} index={0}>
        <BedUtilizationTab />
      </TabPanel>
      <TabPanel value={tabValue} index={1}>
        <EquipmentUtilizationTab />
      </TabPanel>
      <TabPanel value={tabValue} index={2}>
        <StaffUtilizationTab />
      </TabPanel>
    </Box>
  );
};

export default ComprehensiveReportingDashboard;
