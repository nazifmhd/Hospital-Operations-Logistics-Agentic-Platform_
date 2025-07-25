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

  useEffect(() => {
    fetchBeds();
    fetchDepartments();
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

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'available': return 'success';
      case 'occupied': return 'warning';
      case 'maintenance': return 'error';
      case 'cleaning': return 'info';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'available': return <CheckCircle sx={{ color: 'green' }} />;
      case 'occupied': return <LocalHospital sx={{ color: 'orange' }} />;
      case 'maintenance': return <Warning sx={{ color: 'red' }} />;
      case 'cleaning': return <Block sx={{ color: 'blue' }} />;
      default: return null;
    }
  };

  const bedStatusCounts = beds.reduce((acc, bed) => {
    acc[bed.status] = (acc[bed.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const occupancyRate = beds.length > 0 ? 
    ((bedStatusCounts['occupied'] || 0) / beds.length * 100).toFixed(1) : '0';

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Bed Management Dashboard
      </Typography>

      {/* Summary Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 3, mb: 3 }}>
        <Card>
          <CardContent>
            <Typography variant="h4" component="div" color="primary">
              {beds.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Beds
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h4" component="div" color="success.main">
              {bedStatusCounts['available'] || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Available Beds
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h4" component="div" color="warning.main">
              {bedStatusCounts['occupied'] || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Occupied Beds
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h4" component="div" color="error.main">
              {occupancyRate}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Occupancy Rate
            </Typography>
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
            <Table>
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
                          onClick={() => {
                            setSelectedBed(bed);
                            setNewStatus(bed.status);
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

      {/* Update Bed Status Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>Update Bed Status</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, minWidth: 300 }}>
            <Typography variant="body2" gutterBottom>
              Bed: {selectedBed?.number} - Room {selectedBed?.room_number}
            </Typography>
            <FormControl fullWidth sx={{ mt: 2 }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={newStatus}
                label="Status"
                onChange={(e) => setNewStatus(e.target.value)}
              >
                <MenuItem value="available">Available</MenuItem>
                <MenuItem value="occupied">Occupied</MenuItem>
                <MenuItem value="cleaning">Cleaning</MenuItem>
                <MenuItem value="maintenance">Maintenance</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={updateBedStatus} variant="contained">
            Update
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BedManagementDashboard;
