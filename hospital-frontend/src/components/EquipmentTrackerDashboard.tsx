import React, { useState, useEffect } from 'react';
import {
  Typography,
  Card,
  CardContent,
  Box,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { 
  MedicalServices, 
  Build, 
  CheckCircle, 
  Warning, 
  Error,
  Schedule
} from '@mui/icons-material';
import axios from 'axios';

interface Equipment {
  id: string;
  asset_tag: string;
  name: string;
  equipment_type: string;
  manufacturer: string;
  model: string;
  status: string;
  department_id: string;
  location_type: string;
  current_location_id: string;
  last_maintenance: string;
  next_maintenance: string;
}

interface Department {
  id: string;
  name: string;
  code: string;
}

const EquipmentTrackerDashboard: React.FC = () => {
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEquipment, setSelectedEquipment] = useState<Equipment | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newStatus, setNewStatus] = useState('');
  const [maintenanceDueCount, setMaintenanceDueCount] = useState(0);

  useEffect(() => {
    fetchEquipment();
    fetchDepartments();
  }, []);

  const fetchEquipment = async () => {
    try {
      const response = await axios.get('http://localhost:8000/equipment_tracker/query');
      setEquipment(response.data.equipment || []);
      setMaintenanceDueCount(response.data.maintenance_due_30_days || 0);
    } catch (error) {
      console.error('Error fetching equipment:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDepartments = async () => {
    try {
      const response = await axios.post('http://localhost:8000/equipment_tracker/query', {
        query: 'Show all departments',
        parameters: {}
      });
      setDepartments(response.data.departments || []);
    } catch (error) {
      console.error('Error fetching departments:', error);
    }
  };

  const updateEquipmentStatus = async () => {
    if (!selectedEquipment || !newStatus) return;

    try {
      // Use direct update endpoint for immediate database update
      const response = await axios.post('http://localhost:8000/equipment_tracker/direct_update', {
        equipment_id: selectedEquipment.id,
        status: newStatus
      });
      
      console.log('Equipment status update response:', response.data);
      
      setDialogOpen(false);
      fetchEquipment(); // Refresh the data
    } catch (error) {
      console.error('Error updating equipment status:', error);
      alert('Failed to update equipment status. Please try again.');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'available': return 'success';
      case 'in_use': return 'primary';
      case 'maintenance': return 'warning';
      case 'broken': return 'error';
      case 'cleaning': return 'info';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'available': return <CheckCircle sx={{ color: 'green' }} />;
      case 'in_use': return <MedicalServices sx={{ color: 'blue' }} />;
      case 'maintenance': return <Build sx={{ color: 'orange' }} />;
      case 'broken': return <Error sx={{ color: 'red' }} />;
      case 'cleaning': return <Warning sx={{ color: 'purple' }} />;
      default: return null;
    }
  };

  const getTypeColor = (type: string) => {
    const colors = {
      'ventilator': '#d32f2f',
      'iv_pump': '#1976d2',
      'monitor': '#388e3c',
      'defibrillator': '#f57c00',
      'wheelchair': '#7b1fa2',
      'transport_bed': '#00796b',
      'dialysis': '#c2185b',
      'ultrasound': '#5d4037'
    };
    return colors[type.toLowerCase() as keyof typeof colors] || '#757575';
  };

  const equipmentStatusCounts = equipment.reduce((acc, item) => {
    // Normalize status to lowercase for consistent counting
    const normalizedStatus = item.status.toLowerCase();
    acc[normalizedStatus] = (acc[normalizedStatus] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const equipmentTypeCounts = equipment.reduce((acc, item) => {
    acc[item.equipment_type] = (acc[item.equipment_type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  if (loading) {
    return <LinearProgress />;
  }
  // Event Handlers
  const handleUpdate = () => {
    console.log('EquipmentTrackerDashboard: Update action triggered');
  };

  const handleDelete = () => {
    console.log('EquipmentTrackerDashboard: Delete action triggered');
  };

  const handleCreate = () => {
    console.log('EquipmentTrackerDashboard: Create action triggered');
  };



  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Equipment Tracker Dashboard
      </Typography>

      {/* Summary Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 3, mb: 3 }}>
        <Card>
          <CardContent>
            <Typography variant="h4" component="div" color="primary">
              {equipment.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Equipment
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h4" component="div" color="success.main">
              {equipmentStatusCounts['available'] || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Available
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h4" component="div" color="primary.main">
              {equipmentStatusCounts['in_use'] || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              In Use
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h4" component="div" color="warning.main">
              {maintenanceDueCount}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Maintenance Due (30 days)
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Equipment Type Distribution */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3, mb: 3 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Equipment by Type
            </Typography>
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
              {Object.entries(equipmentTypeCounts).slice(0, 6).map(([type, count]) => (
                <Box key={type} sx={{ display: 'flex', alignItems: 'center' }}>
                  <MedicalServices sx={{ color: getTypeColor(type), mr: 1 }} />
                  <Box>
                    <Typography variant="h6" component="div">
                      {count}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {type.replace('_', ' ')}
                    </Typography>
                  </Box>
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Status Distribution
            </Typography>
            {Object.entries(equipmentStatusCounts).map(([status, count]) => (
              <Box key={status} sx={{ mb: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    {getStatusIcon(status)}
                    <Typography variant="body2" sx={{ ml: 1 }}>
                      {status.replace('_', ' ')}
                    </Typography>
                  </Box>
                  <Typography variant="body2">{count}</Typography>
                </Box>
              </Box>
            ))}
          </CardContent>
        </Card>
      </Box>

      {/* Equipment Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Equipment Inventory
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Asset Tag</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Manufacturer</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Location</TableCell>
                  <TableCell>Next Maintenance</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {equipment.map((item) => {
                  const department = departments.find(d => d.id === item.department_id);
                  const nextMaintenance = new Date(item.next_maintenance);
                  const today = new Date();
                  const daysUntil = Math.ceil((nextMaintenance.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
                  
                  return (
                    <TableRow key={item.id}>
                      <TableCell>{item.asset_tag}</TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="bold">
                          {item.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {item.model}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={item.equipment_type.replace('_', ' ')}
                          sx={{ bgcolor: getTypeColor(item.equipment_type), color: 'white' }}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{item.manufacturer}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {getStatusIcon(item.status)}
                          <Chip 
                            label={item.status.replace('_', ' ')} 
                            color={getStatusColor(item.status)}
                            size="small"
                            sx={{ ml: 1 }}
                          />
                        </Box>
                      </TableCell>
                      <TableCell>{department?.name || 'Unknown'}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {daysUntil <= 30 && <Schedule sx={{ color: 'orange', mr: 1 }} />}
                          <Typography 
                            variant="body2" 
                            color={daysUntil <= 30 ? 'warning.main' : 'text.primary'}
                          >
                            {daysUntil} days
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => {
                            setSelectedEquipment(item);
                            setNewStatus(item.status);
                            setDialogOpen(true);
                          }}
                        >
                          Update
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Update Equipment Status Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>Update Equipment Status</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, minWidth: 300 }}>
            <Typography variant="body2" gutterBottom>
              Equipment: {selectedEquipment?.name} ({selectedEquipment?.asset_tag})
            </Typography>
            <FormControl fullWidth sx={{ mt: 2 }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={newStatus}
                label="Status"
                onChange={(e) => setNewStatus(e.target.value)}
              >
                <MenuItem value="AVAILABLE">Available</MenuItem>
                <MenuItem value="IN_USE">In Use</MenuItem>
                <MenuItem value="MAINTENANCE">Maintenance</MenuItem>
                <MenuItem value="BROKEN">Broken</MenuItem>
                <MenuItem value="CLEANING">Cleaning</MenuItem>
                <MenuItem value="CALIBRATION">Calibration</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={updateEquipmentStatus} variant="contained">
            Update
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EquipmentTrackerDashboard;
