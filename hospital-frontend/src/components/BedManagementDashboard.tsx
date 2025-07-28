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
import { LocalHospital, Warning, CheckCircle, Block } from '@mui/icons-material';
import axios from 'axios';

interface Bed {
  id: string;
  number: string;
  department_id: string;
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
}

const BedManagementDashboard: React.FC = () => {
  const [beds, setBeds] = useState<Bed[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedBed, setSelectedBed] = useState<Bed | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newStatus, setNewStatus] = useState('');
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    const initializeData = async () => {
      console.log('🏥 Initializing Bed Management Dashboard...');
      setLoading(true);
      setFetchError(null);
      
      try {
        await Promise.all([fetchBeds(), fetchDepartments()]);
        console.log('✅ All data fetched successfully');
      } catch (error) {
        console.error('❌ Error during data initialization:', error);
        setFetchError('Failed to load data. Please refresh the page.');
      } finally {
        setLoading(false);
      }
    };
    
    initializeData();
  }, []);

  const fetchBeds = async () => {
    try {
      console.log('🛏️ Fetching beds data...');
      const response = await axios.get('http://localhost:8000/bed_management/query');
      console.log('📊 Beds API Response status:', response.status);
      console.log('📊 Beds API Response data keys:', Object.keys(response.data));
      console.log('📊 Beds API Full Response:', response.data);
      
      const bedsData = response.data.beds || [];
      console.log(`✅ Processed beds data: ${bedsData.length} beds found`);
      console.log('📋 Sample bed data:', bedsData[0]);
      
      if (!Array.isArray(bedsData)) {
        throw new Error('Beds data is not an array');
      }
      
      setBeds(bedsData);
      setLastUpdate(new Date());
      return bedsData;
    } catch (error) {
      console.error('❌ Error fetching beds:', error);
      setBeds([]);
      throw error;
    }
  };

  const fetchDepartments = async () => {
    try {
      console.log('🏢 Fetching departments data...');
      const response = await axios.post('http://localhost:8000/bed_management/query', {
        query: 'Show all departments',
        parameters: {}
      });
      console.log('📊 Departments API Response status:', response.status);
      console.log('📊 Departments API Response data keys:', Object.keys(response.data));
      console.log('📊 Departments API Full Response:', response.data);
      
      const departmentsData = response.data.departments || [];
      console.log(`✅ Processed departments data: ${departmentsData.length} departments found`);
      console.log('📋 Sample department data:', departmentsData[0]);
      
      if (!Array.isArray(departmentsData)) {
        throw new Error('Departments data is not an array');
      }
      
      setDepartments(departmentsData);
      return departmentsData;
    } catch (error) {
      console.error('❌ Error fetching departments:', error);
      setDepartments([]);
      throw error;
    }
  };

  const updateBedStatus = async () => {
    if (!selectedBed || !newStatus) {
      console.error('Missing selected bed or new status');
      alert('Please select a bed and status before updating.');
      return;
    }

    try {
      console.log('🔄 Updating bed status:', {
        bedId: selectedBed.id,
        currentStatus: selectedBed.status,
        newStatus: newStatus
      });
      
      const response = await axios.post('http://localhost:8000/bed_management/direct_update', {
        bed_id: selectedBed.id,
        status: newStatus
      });
      
      console.log('✅ Update response:', response.data);
      
      if (response.status === 200) {
        // Close dialog first
        setDialogOpen(false);
        setSelectedBed(null);
        setNewStatus('');
        
        // Show loading state during refresh
        setLoading(true);
        
        // Refresh the data with error handling
        try {
          console.log('🔄 Refreshing data after successful update...');
          await Promise.all([fetchBeds(), fetchDepartments()]);
          console.log('✅ Data refreshed successfully after update');
          
          // Force component re-render by updating lastUpdate
          setLastUpdate(new Date());
          
          // Show success feedback
          alert(`Bed ${selectedBed.number} status updated to ${newStatus}`);
        } catch (refreshError) {
          console.error('❌ Error refreshing data after update:', refreshError);
          alert('Update successful, but failed to refresh data. Please reload the page.');
        } finally {
          setLoading(false);
        }
      } else {
        throw new Error(`Update failed with status ${response.status}`);
      }
      
    } catch (error) {
      console.error('❌ Error updating bed status:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      alert(`Failed to update bed status: ${errorMessage}`);
    }
  };

  const getStatusColor = (status: string) => {
    const statusLower = status.toLowerCase();
    switch (statusLower) {
      case 'available': return 'success';
      case 'occupied': return 'warning';
      case 'maintenance': return 'error';
      case 'cleaning': return 'info';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    const statusLower = status.toLowerCase();
    switch (statusLower) {
      case 'available': return <CheckCircle sx={{ color: 'green' }} />;
      case 'occupied': return <LocalHospital sx={{ color: 'orange' }} />;
      case 'maintenance': return <Warning sx={{ color: 'red' }} />;
      case 'cleaning': return <Block sx={{ color: 'blue' }} />;
      default: return null;
    }
  };

  const bedStatusCounts = beds.reduce((acc, bed) => {
    const status = bed.status || 'unknown';
    acc[status] = (acc[status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const occupancyRate = beds.length > 0 ? 
    ((bedStatusCounts['OCCUPIED'] || bedStatusCounts['occupied'] || 0) / beds.length * 100).toFixed(1) : '0';

  console.log('🔍 Bed Management Debug:', {
    totalBeds: beds.length,
    bedStatusCounts,
    occupancyRate,
    sampleBed: beds[0],
    departments: departments.length,
    loading: loading,
    fetchError: fetchError
  });

  if (loading) {
    console.log('🔄 Loading state - showing progress bar');
    return (
      <Box sx={{ width: '100%', padding: 2 }}>
        <Typography variant="h6" gutterBottom>Loading Bed Management Data...</Typography>
        <LinearProgress />
      </Box>
    );
  }

  if (fetchError) {
    console.log('❌ Error state - showing error message');
    return (
      <Box sx={{ width: '100%', padding: 2 }}>
        <Typography variant="h6" color="error" gutterBottom>Error Loading Data</Typography>
        <Typography variant="body1">{fetchError}</Typography>
        <Button onClick={() => window.location.reload()} sx={{ mt: 2 }}>
          Retry
        </Button>
      </Box>
    );
  }
  // Event Handlers
  const handleUpdate = () => {
    console.log('BedManagementDashboard: Update action triggered');
  };

  const handleDelete = () => {
    console.log('BedManagementDashboard: Delete action triggered');
  };

  const handleCreate = () => {
    console.log('BedManagementDashboard: Create action triggered');
  };



  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5">
          Bed Management Dashboard
        </Typography>
        <Button 
          variant="outlined" 
          onClick={async () => {
            setLoading(true);
            try {
              await Promise.all([fetchBeds(), fetchDepartments()]);
              setLastUpdate(new Date());
              console.log('✅ Manual refresh completed');
            } catch (error) {
              console.error('❌ Manual refresh failed:', error);
            } finally {
              setLoading(false);
            }
          }}
          disabled={loading}
        >
          🔄 Refresh Data
        </Button>
      </Box>

      {/* Debug Information (remove in production) */}
      <Box sx={{ mb: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
        <Typography variant="caption" color="text.secondary">
          Debug: {beds.length} beds loaded, {departments.length} departments, Status: {Object.keys(bedStatusCounts).join(', ')}, Last Update: {lastUpdate.toLocaleTimeString()}
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 3, mb: 3 }}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="h4" component="div" color="primary">
                  {beds.length || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Beds
                </Typography>
              </Box>
              <LocalHospital sx={{ fontSize: 40, color: 'primary.main' }} />
            </Box>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="h4" component="div" color="success.main">
                  {bedStatusCounts['AVAILABLE'] || bedStatusCounts['available'] || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Available Beds
                </Typography>
              </Box>
              <CheckCircle sx={{ fontSize: 40, color: 'success.main' }} />
            </Box>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="h4" component="div" color="warning.main">
                  {bedStatusCounts['OCCUPIED'] || bedStatusCounts['occupied'] || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Occupied Beds
                </Typography>
              </Box>
              <Warning sx={{ fontSize: 40, color: 'warning.main' }} />
            </Box>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="h4" component="div" color="error.main">
                  {occupancyRate}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Occupancy Rate
                </Typography>
              </Box>
              <Block sx={{ fontSize: 40, color: 'error.main' }} />
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Beds Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Bed Status Overview
          </Typography>
          <TableContainer component={Paper}>
            <Table key={`bed-table-${lastUpdate.getTime()}`}>
              <TableHead>
                <TableRow>
                  <TableCell>Bed Number</TableCell>
                  <TableCell>Department</TableCell>
                  <TableCell>Room</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Patient</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {beds.map((bed) => {
                  const department = departments.find(d => d.id === bed.department_id);
                  return (
                    <TableRow key={bed.id}>
                      <TableCell>{bed.number}</TableCell>
                      <TableCell>{department?.name || 'Unknown'}</TableCell>
                      <TableCell>{bed.room_number}</TableCell>
                      <TableCell>{bed.bed_type}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {getStatusIcon(bed.status)}
                          <Chip 
                            label={bed.status} 
                            color={getStatusColor(bed.status)}
                            size="small"
                            sx={{ ml: 1 }}
                          />
                        </Box>
                      </TableCell>
                      <TableCell>
                        {bed.current_patient_id ? (
                          <Chip label="Assigned" color="warning" size="small" />
                        ) : (
                          <Chip label="None" color="default" size="small" />
                        )}
                      </TableCell>
                      <TableCell>
                        <Button
                          size="small"
                          variant="outlined"
                          color="primary"
                          onClick={() => {
                            console.log('Update button clicked for bed:', bed);
                            setSelectedBed(bed);
                            setNewStatus(bed.status || 'AVAILABLE');
                            setDialogOpen(true);
                          }}
                          sx={{ minWidth: 80 }}
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

      {/* Update Bed Status Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={() => {
          console.log('Dialog closing');
          setDialogOpen(false);
          setSelectedBed(null);
          setNewStatus('');
        }}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Update Bed Status
          {selectedBed && (
            <Typography variant="body2" color="text.secondary">
              Bed {selectedBed.number} in Room {selectedBed.room_number}
            </Typography>
          )}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, minWidth: 300 }}>
            {selectedBed && (
              <>
                <Typography variant="body2" gutterBottom>
                  Current Status: <strong>{selectedBed.status}</strong>
                </Typography>
                <FormControl fullWidth sx={{ mt: 2 }}>
                  <InputLabel>New Status</InputLabel>
                  <Select
                    value={newStatus}
                    label="New Status"
                    onChange={(e) => {
                      console.log('Status changed to:', e.target.value);
                      setNewStatus(e.target.value);
                    }}
                  >
                    <MenuItem value="AVAILABLE">Available</MenuItem>
                    <MenuItem value="OCCUPIED">Occupied</MenuItem>
                    <MenuItem value="CLEANING">Cleaning</MenuItem>
                    <MenuItem value="MAINTENANCE">Maintenance</MenuItem>
                  </Select>
                </FormControl>
              </>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => {
              console.log('Cancel clicked');
              setDialogOpen(false);
              setSelectedBed(null);
              setNewStatus('');
            }}
          >
            Cancel
          </Button>
          <Button 
            onClick={updateBedStatus} 
            variant="contained"
            disabled={!newStatus || !selectedBed}
          >
            Update Status
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BedManagementDashboard;
