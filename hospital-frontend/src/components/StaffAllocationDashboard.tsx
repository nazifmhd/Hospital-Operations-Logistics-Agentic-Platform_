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
  Avatar,
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
import { Person } from '@mui/icons-material';
import axios from 'axios';

interface StaffMember {
  id: string;
  employee_id: string;
  name: string;
  role: string;
  department_id: string;
  specialties: string[];
  status: string;
  email: string;
  phone: string;
  max_patients: number;
}

interface Department {
  id: string;
  name: string;
  code: string;
}

const StaffAllocationDashboard: React.FC = () => {
  const [staff, setStaff] = useState<StaffMember[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStaff, setSelectedStaff] = useState<StaffMember | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newStatus, setNewStatus] = useState('');

  useEffect(() => {
    fetchStaff();
    fetchDepartments();
  }, []);

  const fetchStaff = async () => {
    try {
      const response = await axios.post('http://localhost:8000/staff_allocation/query', {
        query: 'Show all staff members with their current assignments',
        parameters: {}
      });
      setStaff(response.data.staff_members || []);
    } catch (error) {
      console.error('Error fetching staff:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDepartments = async () => {
    try {
      const response = await axios.post('http://localhost:8000/staff_allocation/query', {
        query: 'Show all departments',
        parameters: {}
      });
      setDepartments(response.data.departments || []);
    } catch (error) {
      console.error('Error fetching departments:', error);
    }
  };

  const updateStaffStatus = async () => {
    if (!selectedStaff || !newStatus) return;

    try {
      await axios.post('http://localhost:8000/staff_allocation/execute', {
        action: 'update_staff_status',
        parameters: {
          staff_id: selectedStaff.id,
          status: newStatus
        }
      });
      
      setDialogOpen(false);
      fetchStaff(); // Refresh the data
    } catch (error) {
      console.error('Error updating staff status:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'available': return 'success';
      case 'on_duty': return 'primary';
      case 'break': return 'warning';
      case 'unavailable': return 'error';
      case 'off_duty': return 'default';
      default: return 'default';
    }
  };

  const getRoleColor = (role: string) => {
    switch (role.toLowerCase()) {
      case 'doctor': return '#1976d2';
      case 'nurse': return '#388e3c';
      case 'technician': return '#f57c00';
      default: return '#757575';
    }
  };

  const staffStatusCounts = staff.reduce((acc, member) => {
    acc[member.status] = (acc[member.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const roleDistribution = staff.reduce((acc, member) => {
    acc[member.role] = (acc[member.role] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Staff Allocation Dashboard
      </Typography>

      {/* Summary Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 3, mb: 3 }}>
        <Card>
          <CardContent>
            <Typography variant="h4" component="div" color="primary">
              {staff.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Staff
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h4" component="div" color="success.main">
              {staffStatusCounts['available'] || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Available
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h4" component="div" color="primary.main">
              {staffStatusCounts['on_duty'] || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              On Duty
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h4" component="div" color="warning.main">
              {staffStatusCounts['break'] || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              On Break
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Role Distribution */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3, mb: 3 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Staff by Role
            </Typography>
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
              {Object.entries(roleDistribution).map(([role, count]) => (
                <Box key={role} sx={{ display: 'flex', alignItems: 'center' }}>
                  <Person sx={{ color: getRoleColor(role), mr: 1 }} />
                  <Box>
                    <Typography variant="h6" component="div">
                      {count}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {role}s
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
              Department Distribution
            </Typography>
            {departments.slice(0, 4).map((dept) => {
              const deptStaffCount = staff.filter(s => s.department_id === dept.id).length;
              return (
                <Box key={dept.id} sx={{ mb: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">{dept.name}</Typography>
                    <Typography variant="body2">{deptStaffCount}</Typography>
                  </Box>
                </Box>
              );
            })}
          </CardContent>
        </Card>
      </Box>

      {/* Staff Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Staff Members
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Staff Member</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Department</TableCell>
                  <TableCell>Specialties</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Max Patients</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {staff.map((member) => {
                  const department = departments.find(d => d.id === member.department_id);
                  return (
                    <TableRow key={member.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar sx={{ mr: 2, bgcolor: getRoleColor(member.role) }}>
                            {member.name.charAt(0)}
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {member.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {member.employee_id}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={member.role}
                          sx={{ bgcolor: getRoleColor(member.role), color: 'white' }}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{department?.name || 'Unknown'}</TableCell>
                      <TableCell>
                        {member.specialties?.map((specialty, index) => (
                          <Chip 
                            key={index}
                            label={specialty} 
                            variant="outlined"
                            size="small"
                            sx={{ mr: 0.5, mb: 0.5 }}
                          />
                        ))}
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={member.status.replace('_', ' ')} 
                          color={getStatusColor(member.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{member.max_patients}</TableCell>
                      <TableCell>
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => {
                            setSelectedStaff(member);
                            setNewStatus(member.status);
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

      {/* Update Staff Status Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>Update Staff Status</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, minWidth: 300 }}>
            <Typography variant="body2" gutterBottom>
              Staff: {selectedStaff?.name} ({selectedStaff?.employee_id})
            </Typography>
            <FormControl fullWidth sx={{ mt: 2 }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={newStatus}
                label="Status"
                onChange={(e) => setNewStatus(e.target.value)}
              >
                <MenuItem value="available">Available</MenuItem>
                <MenuItem value="on_duty">On Duty</MenuItem>
                <MenuItem value="break">On Break</MenuItem>
                <MenuItem value="unavailable">Unavailable</MenuItem>
                <MenuItem value="off_duty">Off Duty</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={updateStaffStatus} variant="contained">
            Update
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default StaffAllocationDashboard;
