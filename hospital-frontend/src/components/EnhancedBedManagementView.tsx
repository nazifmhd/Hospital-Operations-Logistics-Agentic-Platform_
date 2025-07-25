import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Tooltip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
} from '@mui/material';
import {
  LocalHospital,
  Person,
  CleaningServices,
  Build,
  CheckCircle,
  Warning,
} from '@mui/icons-material';
import axios from 'axios';

interface Bed {
  id: string;
  number: string;
  department_id: string;
  department_name: string;
  room_number: string;
  bed_type: string;
  status: string;
  current_patient_id?: string;
  last_cleaned: string;
}

interface Department {
  id: string;
  name: string;
  code: string;
  capacity: number;
  occupied: number;
  available: number;
}

interface BedFloorPlanProps {
  beds: Bed[];
  departments: Department[];
  onBedClick: (bed: Bed) => void;
}

const BedFloorPlan: React.FC<BedFloorPlanProps> = ({ beds, departments, onBedClick }) => {
  const [selectedDepartment, setSelectedDepartment] = useState<string>('all');

  const getBedStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'occupied': return '#f44336'; // Red
      case 'available': return '#4caf50'; // Green
      case 'dirty': return '#ff9800'; // Orange
      case 'maintenance': return '#9c27b0'; // Purple
      case 'blocked': return '#607d8b'; // Blue Gray
      default: return '#e0e0e0'; // Light Gray
    }
  };

  const getBedStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'occupied': return <Person />;
      case 'available': return <CheckCircle />;
      case 'dirty': return <CleaningServices />;
      case 'maintenance': return <Build />;
      case 'blocked': return <Warning />;
      default: return <LocalHospital />;
    }
  };

  const filteredBeds = selectedDepartment === 'all' 
    ? beds 
    : beds.filter(bed => bed.department_id === selectedDepartment);

  const groupedBeds = filteredBeds.reduce((groups, bed) => {
    const dept = bed.department_name || 'Unknown';
    if (!groups[dept]) {
      groups[dept] = [];
    }
    groups[dept].push(bed);
    return groups;
  }, {} as Record<string, Bed[]>);

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Department Filter</InputLabel>
          <Select
            value={selectedDepartment}
            label="Department Filter"
            onChange={(e) => setSelectedDepartment(e.target.value)}
          >
            <MenuItem value="all">All Departments</MenuItem>
            {departments.map((dept) => (
              <MenuItem key={dept.id} value={dept.id}>
                {dept.name} ({dept.code})
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Status Legend */}
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip size="small" label="Available" sx={{ backgroundColor: '#4caf50', color: 'white' }} />
          <Chip size="small" label="Occupied" sx={{ backgroundColor: '#f44336', color: 'white' }} />
          <Chip size="small" label="Dirty" sx={{ backgroundColor: '#ff9800', color: 'white' }} />
          <Chip size="small" label="Maintenance" sx={{ backgroundColor: '#9c27b0', color: 'white' }} />
          <Chip size="small" label="Blocked" sx={{ backgroundColor: '#607d8b', color: 'white' }} />
        </Box>
      </Box>

      {/* Floor Plan View */}
      <Box sx={{ maxHeight: '70vh', overflowY: 'auto' }}>
        {Object.entries(groupedBeds).map(([departmentName, deptBeds]) => (
          <Card key={departmentName} sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <LocalHospital />
                {departmentName}
                <Chip 
                  size="small" 
                  label={`${deptBeds.length} beds`} 
                  color="primary" 
                />
              </Typography>
              
              {/* Beds Grid */}
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                {deptBeds.map((bed) => (
                  <Tooltip
                    key={bed.id}
                    title={
                      <Box>
                        <Typography variant="subtitle2">Bed {bed.number}</Typography>
                        <Typography variant="body2">Room: {bed.room_number}</Typography>
                        <Typography variant="body2">Type: {bed.bed_type}</Typography>
                        <Typography variant="body2">Status: {bed.status}</Typography>
                        {bed.current_patient_id && (
                          <Typography variant="body2">Patient: {bed.current_patient_id}</Typography>
                        )}
                        {bed.last_cleaned && (
                          <Typography variant="body2">
                            Last Cleaned: {new Date(bed.last_cleaned).toLocaleDateString()}
                          </Typography>
                        )}
                      </Box>
                    }
                  >
                    <Card
                      sx={{
                        width: 80,
                        height: 80,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: 'pointer',
                        backgroundColor: getBedStatusColor(bed.status),
                        color: 'white',
                        '&:hover': {
                          transform: 'scale(1.05)',
                          boxShadow: 3,
                        },
                        transition: 'all 0.2s ease-in-out',
                      }}
                      onClick={() => onBedClick(bed)}
                    >
                      <Box sx={{ mb: 0.5 }}>
                        {getBedStatusIcon(bed.status)}
                      </Box>
                      <Typography variant="caption" fontWeight="bold">
                        {bed.number}
                      </Typography>
                      <Typography variant="caption" fontSize="0.7rem">
                        {bed.room_number}
                      </Typography>
                    </Card>
                  </Tooltip>
                ))}
              </Box>
            </CardContent>
          </Card>
        ))}
      </Box>
    </Box>
  );
};

const EnhancedBedManagementView: React.FC = () => {
  const [beds, setBeds] = useState<Bed[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedBed, setSelectedBed] = useState<Bed | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newStatus, setNewStatus] = useState('');
  const [viewMode, setViewMode] = useState(0); // 0: Floor Plan, 1: List View

  useEffect(() => {
    fetchBeds();
    fetchDepartments();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchBeds();
      fetchDepartments();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchBeds = async () => {
    try {
      const response = await axios.post('http://localhost:8000/bed_management/query', {
        query: 'Show all beds with their current status',
        parameters: {}
      });
      setBeds(response.data.beds || []);
    } catch (error) {
      console.error('Error fetching beds:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDepartments = async () => {
    try {
      const response = await axios.post('http://localhost:8000/bed_management/query', {
        query: 'Show all departments',
        parameters: {}
      });
      setDepartments(response.data.departments || []);
    } catch (error) {
      console.error('Error fetching departments:', error);
    }
  };

  const handleBedClick = (bed: Bed) => {
    setSelectedBed(bed);
    setNewStatus(bed.status);
    setDialogOpen(true);
  };

  const updateBedStatus = async () => {
    if (!selectedBed || !newStatus) return;

    try {
      await axios.post('http://localhost:8000/bed_management/execute', {
        action: 'update_bed_status',
        parameters: {
          bed_id: selectedBed.id,
          status: newStatus
        }
      });
      
      setDialogOpen(false);
      fetchBeds(); // Refresh the data
    } catch (error) {
      console.error('Error updating bed status:', error);
    }
  };

  const getDepartmentStats = () => {
    const totalBeds = beds.length;
    const occupiedBeds = beds.filter(bed => bed.status.toLowerCase() === 'occupied').length;
    const availableBeds = beds.filter(bed => bed.status.toLowerCase() === 'available').length;
    const maintenanceBeds = beds.filter(bed => bed.status.toLowerCase() === 'maintenance').length;
    const dirtyBeds = beds.filter(bed => bed.status.toLowerCase() === 'dirty').length;

    return {
      total: totalBeds,
      occupied: occupiedBeds,
      available: availableBeds,
      maintenance: maintenanceBeds,
      dirty: dirtyBeds,
      utilization: totalBeds > 0 ? ((occupiedBeds / totalBeds) * 100).toFixed(1) : '0'
    };
  };

  const stats = getDepartmentStats();

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h6">Loading bed management data...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        🏥 Real-time Bed Status Dashboard
      </Typography>

      {/* Statistics Overview */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 3 }}>
        <Card sx={{ minWidth: 150, flex: '1 1 150px' }}>
          <CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="primary">{stats.total}</Typography>
            <Typography variant="body2" color="textSecondary">Total Beds</Typography>
          </CardContent>
        </Card>
        <Card sx={{ minWidth: 150, flex: '1 1 150px' }}>
          <CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="error">{stats.occupied}</Typography>
            <Typography variant="body2" color="textSecondary">Occupied</Typography>
          </CardContent>
        </Card>
        <Card sx={{ minWidth: 150, flex: '1 1 150px' }}>
          <CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="success">{stats.available}</Typography>
            <Typography variant="body2" color="textSecondary">Available</Typography>
          </CardContent>
        </Card>
        <Card sx={{ minWidth: 150, flex: '1 1 150px' }}>
          <CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="warning">{stats.dirty}</Typography>
            <Typography variant="body2" color="textSecondary">Dirty</Typography>
          </CardContent>
        </Card>
        <Card sx={{ minWidth: 150, flex: '1 1 150px' }}>
          <CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="info">{stats.utilization}%</Typography>
            <Typography variant="body2" color="textSecondary">Utilization</Typography>
          </CardContent>
        </Card>
      </Box>

      {/* View Mode Tabs */}
      <Card sx={{ mb: 3 }}>
        <Tabs value={viewMode} onChange={(_, newValue) => setViewMode(newValue)}>
          <Tab label="Floor Plan View" />
          <Tab label="Department Summary" />
        </Tabs>
      </Card>

      {/* Content based on view mode */}
      {viewMode === 0 && (
        <BedFloorPlan 
          beds={beds} 
          departments={departments} 
          onBedClick={handleBedClick}
        />
      )}

      {viewMode === 1 && (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
          {departments.map((dept) => (
            <Card key={dept.id} sx={{ minWidth: 300, flex: '1 1 300px' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {dept.name}
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Capacity:</Typography>
                  <Typography variant="body2" fontWeight="bold">{dept.capacity}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Occupied:</Typography>
                  <Typography variant="body2" fontWeight="bold" color="error">{dept.occupied}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2">Available:</Typography>
                  <Typography variant="body2" fontWeight="bold" color="success">{dept.available}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Utilization:</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {dept.capacity > 0 ? ((dept.occupied / dept.capacity) * 100).toFixed(1) : 0}%
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      {/* Bed Status Update Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>Update Bed Status</DialogTitle>
        <DialogContent>
          {selectedBed && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body1" gutterBottom>
                Bed: {selectedBed.number} (Room {selectedBed.room_number})
              </Typography>
              <Typography variant="body2" gutterBottom>
                Department: {selectedBed.department_name}
              </Typography>
              <Typography variant="body2" gutterBottom>
                Type: {selectedBed.bed_type}
              </Typography>
              
              <FormControl fullWidth sx={{ mt: 2 }}>
                <InputLabel>New Status</InputLabel>
                <Select
                  value={newStatus}
                  label="New Status"
                  onChange={(e) => setNewStatus(e.target.value)}
                >
                  <MenuItem value="available">Available</MenuItem>
                  <MenuItem value="occupied">Occupied</MenuItem>
                  <MenuItem value="dirty">Dirty</MenuItem>
                  <MenuItem value="maintenance">Maintenance</MenuItem>
                  <MenuItem value="blocked">Blocked</MenuItem>
                </Select>
              </FormControl>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={updateBedStatus} variant="contained">Update</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EnhancedBedManagementView;
