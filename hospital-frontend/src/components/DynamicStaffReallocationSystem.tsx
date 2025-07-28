import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  LinearProgress,
  Avatar,
  IconButton,
  Tooltip,
  Divider,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  SwapHoriz,
  Warning,
  CheckCircle,
  Person,
  Group,
  Schedule,
  Emergency,
  Notifications,
  ThumbUp,
  ThumbDown,
} from '@mui/icons-material';
import axios from 'axios';

interface StaffMember {
  id: string;
  name: string;
  role: string;
  department_id: string;
  department_name: string;
  current_patients: number;
  max_patients: number;
  status: 'active' | 'break' | 'off_duty';
  shift_start: string;
  shift_end: string;
  specialties: string[];
  workload_score: number;
}

interface ReallocationSuggestion {
  id: string;
  type: 'emergency' | 'workload_balance' | 'skill_match' | 'coverage_gap';
  priority: 'low' | 'medium' | 'high' | 'critical';
  staff_member: StaffMember;
  from_department: string;
  to_department: string;
  reason: string;
  impact_description: string;
  estimated_benefit: string;
  status: 'pending' | 'approved' | 'rejected' | 'implemented';
  created_at: string;
  expires_at: string;
}

interface ShiftAdjustment {
  id: string;
  staff_member: StaffMember;
  adjustment_type: 'extend_shift' | 'early_finish' | 'break_extension' | 'overtime';
  current_shift: string;
  proposed_shift: string;
  reason: string;
  impact: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
}

const DynamicStaffReallocationSystem: React.FC = () => {
  const [staffMembers, setStaffMembers] = useState<StaffMember[]>([]);
  const [reallocationSuggestions, setReallocationSuggestions] = useState<ReallocationSuggestion[]>([]);
  const [shiftAdjustments, setShiftAdjustments] = useState<ShiftAdjustment[]>([]);
  const [selectedSuggestion, setSelectedSuggestion] = useState<ReallocationSuggestion | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [emergencyMode, setEmergencyMode] = useState(false);

  useEffect(() => {
    fetchStaffData();
    fetchReallocationSuggestions();
    fetchShiftAdjustments();
    
    // Auto-refresh every 15 seconds for real-time updates
    const interval = setInterval(() => {
      fetchStaffData();
      fetchReallocationSuggestions();
      fetchShiftAdjustments();
    }, 15000);
  // Event Handlers
  const handleUpdate = () => {
    console.log('DynamicStaffReallocationSystem: Update action triggered');
  };

  const handleDelete = () => {
    console.log('DynamicStaffReallocationSystem: Delete action triggered');
  };

  const handleCreate = () => {
    console.log('DynamicStaffReallocationSystem: Create action triggered');
  };


    
    return () => clearInterval(interval);
  }, []);

  const fetchStaffData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/staff_allocation/real_time_status');
      setStaffMembers(response.data.staff || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching staff data:', error);
      setLoading(false);
    }
  };

  const fetchReallocationSuggestions = async () => {
    try {
      const response = await axios.get('http://localhost:8000/staff_allocation/reallocation_suggestions');
      setReallocationSuggestions(response.data.suggestions || []);
    } catch (error) {
      console.error('Error fetching reallocation suggestions:', error);
    }
  };

  const fetchShiftAdjustments = async () => {
    try {
      const response = await axios.get('http://localhost:8000/staff_allocation/shift_adjustments');
      setShiftAdjustments(response.data.adjustments || []);
    } catch (error) {
      console.error('Error fetching shift adjustments:', error);
    }
  };

  const triggerEmergencyReallocation = async () => {
    try {
      setEmergencyMode(true);
      await axios.post('http://localhost:8000/staff_allocation/emergency_reallocation');
      await fetchReallocationSuggestions();
      setTimeout(() => setEmergencyMode(false), 5000);
    } catch (error) {
      console.error('Error triggering emergency reallocation:', error);
      setEmergencyMode(false);
    }
  };

  const approveSuggestion = async (suggestionId: string) => {
    try {
      await axios.post(`http://localhost:8000/staff_allocation/approve_reallocation/${suggestionId}`);
      await fetchReallocationSuggestions();
      await fetchStaffData();
    } catch (error) {
      console.error('Error approving suggestion:', error);
    }
  };

  const rejectSuggestion = async (suggestionId: string) => {
    try {
      await axios.post(`http://localhost:8000/staff_allocation/reject_reallocation/${suggestionId}`);
      await fetchReallocationSuggestions();
    } catch (error) {
      console.error('Error rejecting suggestion:', error);
    }
  };

  const approveShiftAdjustment = async (adjustmentId: string) => {
    try {
      await axios.post(`http://localhost:8000/staff_allocation/approve_shift_adjustment/${adjustmentId}`);
      await fetchShiftAdjustments();
      await fetchStaffData();
    } catch (error) {
      console.error('Error approving shift adjustment:', error);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'success';
      case 'pending': return 'warning';
      case 'rejected': return 'error';
      case 'implemented': return 'info';
      default: return 'default';
    }
  };

  const getWorkloadColor = (score: number) => {
    if (score >= 90) return 'error';
    if (score >= 75) return 'warning';
    if (score >= 50) return 'info';
    return 'success';
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Dynamic Staff Re-allocation System
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  const criticalSuggestions = reallocationSuggestions.filter(s => s.priority === 'critical');
  const overloadedStaff = staffMembers.filter(s => (s.workload_score || 0) >= 85);
  const availableStaff = staffMembers.filter(s => (s.workload_score || 0) < 50 && s.status === 'active');

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Dynamic Staff Re-allocation System
        </Typography>
        <Box>
          <Button
            variant="contained"
            color="error"
            startIcon={<Emergency />}
            onClick={() => triggerEmergencyReallocation()}
          >
            {emergencyMode ? 'Processing...' : 'Emergency Reallocation'}
          </Button>
          <Chip
            label={emergencyMode ? 'EMERGENCY MODE' : 'Normal Operations'}
            color={emergencyMode ? 'error' : 'success'}
            icon={emergencyMode ? <Emergency /> : <CheckCircle />}
          />
        </Box>
      </Box>

      {/* Critical Alerts */}
      {criticalSuggestions.length > 0 && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="h6">Critical Staffing Issues Detected!</Typography>
          <Typography>
            {criticalSuggestions.length} critical reallocation suggestions require immediate attention.
          </Typography>
        </Alert>
      )}

      {/* Summary Dashboard */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 3, mb: 3 }}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Warning sx={{ fontSize: 40, color: '#f57c00', mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {overloadedStaff.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Overloaded Staff
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <SwapHoriz sx={{ fontSize: 40, color: '#1976d2', mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {reallocationSuggestions.filter(s => s.status === 'pending').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Pending Reallocations
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Group sx={{ fontSize: 40, color: '#388e3c', mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {availableStaff.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Available Staff
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Schedule sx={{ fontSize: 40, color: '#7b1fa2', mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {shiftAdjustments.filter(a => a.status === 'pending').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Shift Adjustments
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Current Staff Workload Overview */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Current Staff Workload Status
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Staff Member</TableCell>
                  <TableCell>Department</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell align="right">Patients</TableCell>
                  <TableCell align="right">Workload Score</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Shift Time</TableCell>
                  <TableCell>Specialties</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {staffMembers.map((staff) => (
                  <TableRow key={staff.id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Avatar sx={{ mr: 2, bgcolor: getWorkloadColor(staff.workload_score || 0) }}>
                          <Person />
                        </Avatar>
                        <Typography variant="body2" fontWeight="bold">
                          {staff.name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{staff.department_name}</TableCell>
                    <TableCell>{staff.role}</TableCell>
                    <TableCell align="right">
                      {staff.current_patients || 0}/{staff.max_patients || 0}
                    </TableCell>
                    <TableCell align="right">
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <LinearProgress
                          variant="determinate"
                          value={staff.workload_score || 0}
                          color={getWorkloadColor(staff.workload_score || 0)}
                          sx={{ width: 100, mr: 1 }}
                        />
                        <Typography variant="body2">
                          {staff.workload_score || 0}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={(staff.status || 'unknown').replace('_', ' ').toUpperCase()}
                        color={staff.status === 'active' ? 'success' : 'warning'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {staff.shift_start} - {staff.shift_end}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {(staff.specialties || []).slice(0, 2).map((specialty) => (
                          <Chip
                            key={specialty}
                            label={specialty || 'Unknown'}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                        {(staff.specialties || []).length > 2 && (
                          <Chip
                            label={`+${(staff.specialties || []).length - 2}`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Reallocation Suggestions */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            AI-Powered Reallocation Suggestions
          </Typography>
          {reallocationSuggestions.length === 0 ? (
            <Alert severity="success">
              No reallocation suggestions at this time. All departments are adequately staffed.
            </Alert>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Staff Member</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>From → To</TableCell>
                    <TableCell>Reason</TableCell>
                    <TableCell>Priority</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Expires</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {reallocationSuggestions.map((suggestion) => (
                    <TableRow key={suggestion.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
                            <Person />
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {suggestion.staff_member.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {suggestion.staff_member.role}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={(suggestion.type || 'unknown').replace('_', ' ').toUpperCase()}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography variant="body2">
                            {suggestion.from_department}
                          </Typography>
                          <SwapHoriz sx={{ mx: 1, color: 'text.secondary' }} />
                          <Typography variant="body2" fontWeight="bold">
                            {suggestion.to_department}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Tooltip title={suggestion.impact_description}>
                          <Typography variant="body2" sx={{ maxWidth: 200 }}>
                            {suggestion.reason}
                          </Typography>
                        </Tooltip>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={(suggestion.priority || 'unknown').toUpperCase()}
                          color={getPriorityColor(suggestion.priority)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={(suggestion.status || 'unknown').toUpperCase()}
                          color={getStatusColor(suggestion.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {new Date(suggestion.expires_at).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Tooltip title="View Details">
                            <IconButton
                              size="small"
                              onClick={() => {
                                setSelectedSuggestion(suggestion);
                                setDialogOpen(true);
                              }}
                            >
                              <Notifications />
                            </IconButton>
                          </Tooltip>
                          {suggestion.status === 'pending' && (
                            <>
                              <Tooltip title="Approve">
                                <IconButton
                                  size="small"
                                  color="success"
                                  onClick={() => approveSuggestion(suggestion.id)}
                                >
                                  <ThumbUp />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Reject">
                                <IconButton
                                  size="small"
                                  color="error"
                                  onClick={() => rejectSuggestion(suggestion.id)}
                                >
                                  <ThumbDown />
                                </IconButton>
                              </Tooltip>
                            </>
                          )}
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Shift Adjustments */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Shift Adjustments & Schedule Changes
          </Typography>
          {shiftAdjustments.length === 0 ? (
            <Alert severity="info">
              No shift adjustment requests at this time.
            </Alert>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Staff Member</TableCell>
                    <TableCell>Adjustment Type</TableCell>
                    <TableCell>Current → Proposed</TableCell>
                    <TableCell>Reason</TableCell>
                    <TableCell>Impact</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {shiftAdjustments.map((adjustment) => (
                    <TableRow key={adjustment.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar sx={{ mr: 2, bgcolor: 'secondary.main' }}>
                            <Schedule />
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {adjustment.staff_member.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {adjustment.staff_member.role}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={(adjustment.adjustment_type || 'unknown').replace('_', ' ').toUpperCase()}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2">
                            {adjustment.current_shift}
                          </Typography>
                          <SwapHoriz sx={{ color: 'text.secondary' }} />
                          <Typography variant="body2" fontWeight="bold">
                            {adjustment.proposed_shift}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>{adjustment.reason}</TableCell>
                      <TableCell>{adjustment.impact}</TableCell>
                      <TableCell>
                        <Chip
                          label={(adjustment.status || 'unknown').toUpperCase()}
                          color={getStatusColor(adjustment.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {adjustment.status === 'pending' && (
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Tooltip title="Approve">
                              <IconButton
                                size="small"
                                color="success"
                                onClick={() => approveShiftAdjustment(adjustment.id)}
                              >
                                <ThumbUp />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Reject">
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => {/* Handle rejection */}}
                              >
                                <ThumbDown />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Suggestion Details Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Reallocation Suggestion Details
        </DialogTitle>
        <DialogContent>
          {selectedSuggestion && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Staff Information
              </Typography>
              <Box sx={{ mb: 3 }}>
                <Typography><strong>Name:</strong> {selectedSuggestion.staff_member.name}</Typography>
                <Typography><strong>Role:</strong> {selectedSuggestion.staff_member.role}</Typography>
                <Typography><strong>Current Workload:</strong> {selectedSuggestion.staff_member.workload_score || 0}%</Typography>
                <Typography><strong>Specialties:</strong> {(selectedSuggestion.staff_member.specialties || []).join(', ') || 'None'}</Typography>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Typography variant="h6" gutterBottom>
                Reallocation Details
              </Typography>
              <Box sx={{ mb: 3 }}>
                <Typography><strong>Type:</strong> {selectedSuggestion.type.replace('_', ' ')}</Typography>
                <Typography><strong>Priority:</strong> {selectedSuggestion.priority}</Typography>
                <Typography><strong>From:</strong> {selectedSuggestion.from_department}</Typography>
                <Typography><strong>To:</strong> {selectedSuggestion.to_department}</Typography>
                <Typography><strong>Reason:</strong> {selectedSuggestion.reason}</Typography>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Typography variant="h6" gutterBottom>
                Impact Analysis
              </Typography>
              <Box sx={{ mb: 3 }}>
                <Typography><strong>Description:</strong> {selectedSuggestion.impact_description}</Typography>
                <Typography><strong>Expected Benefit:</strong> {selectedSuggestion.estimated_benefit}</Typography>
                <Typography><strong>Expires:</strong> {new Date(selectedSuggestion.expires_at).toLocaleString()}</Typography>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
          {selectedSuggestion?.status === 'pending' && (
            <>
              <Button
                color="error"
                onClick={() => {
                  rejectSuggestion(selectedSuggestion.id);
                  setDialogOpen(false);
                }}
              >
                Reject
              </Button>
              <Button
                color="success"
                variant="contained"
                onClick={() => {
                  approveSuggestion(selectedSuggestion?.id || '');
                  setDialogOpen(false);
                }}
              >
                Approve Reallocation
              </Button>
            </>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DynamicStaffReallocationSystem;
