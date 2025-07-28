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
  IconButton,
  Tooltip,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Stepper,
  Step,
  StepLabel,
  Avatar,
  Fab,
} from '@mui/material';
import {
  MedicalServices,
  Add,
  LocationOn,
  Schedule,
  CheckCircle,
  Warning,
  DirectionsRun,
  Notifications,
  Search,
  QrCodeScanner,
  Navigation,
} from '@mui/icons-material';
import axios from 'axios';

interface Equipment {
  id: string;
  asset_tag: string;
  name: string;
  equipment_type: string;
  manufacturer: string;
  model: string;
  status: 'available' | 'in_use' | 'maintenance' | 'cleaning';
  location: string;
  department_name: string;
  distance_from_requester: number;
  estimated_retrieval_time: string;
  battery_level?: number;
  last_maintenance: string;
}

interface EquipmentRequest {
  id: string;
  requester_name: string;
  requester_department: string;
  requester_location: string;
  equipment_type: string;
  equipment_id?: string;
  equipment_name?: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  reason: string;
  status: 'pending' | 'assigned' | 'dispatched' | 'delivered' | 'completed' | 'cancelled';
  estimated_delivery_time?: string;
  assigned_porter?: string;
  created_at: string;
  updated_at: string;
  notes?: string;
}

interface Porter {
  id: string;
  name: string;
  status: 'available' | 'busy' | 'off_duty';
  current_location: string;
  active_requests: number;
  estimated_availability: string;
}

const EquipmentRequestDispatchInterface: React.FC = () => {
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [requests, setRequests] = useState<EquipmentRequest[]>([]);
  const [porters, setPorters] = useState<Porter[]>([]);
  const [newRequestDialog, setNewRequestDialog] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<EquipmentRequest | null>(null);
  const [detailsDialog, setDetailsDialog] = useState(false);
  const [loading, setLoading] = useState(true);
  
  // Form state for new request
  const [formData, setFormData] = useState({
    requester_name: '',
    requester_department: '',
    requester_location: '',
    equipment_type: '',
    priority: 'medium' as 'low' | 'medium' | 'high' | 'urgent',
    reason: '',
  });

  useEffect(() => {
    fetchEquipmentData();
    fetchRequests();
    fetchPorters();
    
    // Auto-refresh every 20 seconds
    const interval = setInterval(() => {
      fetchRequests();
      fetchPorters();
    }, 20000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchEquipmentData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/equipment_tracker/available_equipment');
      setEquipment(response.data.equipment || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching equipment data:', error);
      setLoading(false);
    }
  };

  const fetchRequests = async () => {
    try {
      const response = await axios.get('http://localhost:8000/equipment_tracker/equipment_requests');
      setRequests(response.data.requests || []);
    } catch (error) {
      console.error('Error fetching requests:', error);
    }
  };

  const fetchPorters = async () => {
    try {
      const response = await axios.get('http://localhost:8000/equipment_tracker/porter_status');
      setPorters(response.data.porters || []);
    } catch (error) {
      console.error('Error fetching porter status:', error);
    }
  };

  const submitRequest = async () => {
    try {
      await axios.post('http://localhost:8000/equipment_tracker/create_request', formData);
      setNewRequestDialog(false);
      setFormData({
        requester_name: '',
        requester_department: '',
        requester_location: '',
        equipment_type: '',
        priority: 'medium' as 'low' | 'medium' | 'high' | 'urgent',
        reason: '',
      });
      await fetchRequests();
    } catch (error) {
      console.error('Error submitting request:', error);
    }
  };

  const assignEquipment = async (requestId: string, equipmentId: string) => {
    try {
      await axios.post(`http://localhost:8000/equipment_tracker/assign_equipment/${requestId}`, {
        equipment_id: equipmentId
      });
      await fetchRequests();
      await fetchEquipmentData();
    } catch (error) {
      console.error('Error assigning equipment:', error);
    }
  };

  const dispatchRequest = async (requestId: string, porterId: string) => {
    try {
      await axios.post(`http://localhost:8000/equipment_tracker/dispatch_request/${requestId}`, {
        porter_id: porterId
      });
      await fetchRequests();
      await fetchPorters();
    } catch (error) {
      console.error('Error dispatching request:', error);
    }
  };

  const completeRequest = async (requestId: string) => {
    try {
      await axios.post(`http://localhost:8000/equipment_tracker/complete_request/${requestId}`);
      await fetchRequests();
    } catch (error) {
      console.error('Error completing request:', error);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'delivered': return 'info';
      case 'dispatched': return 'primary';
      case 'assigned': return 'secondary';
      case 'pending': return 'warning';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const getRequestSteps = () => [
    'Request Submitted',
    'Equipment Assigned',
    'Porter Dispatched',
    'Equipment Delivered',
    'Request Completed'
  ];

  const getActiveStep = (status: string) => {
    switch (status) {
      case 'pending': return 0;
      case 'assigned': return 1;
      case 'dispatched': return 2;
      case 'delivered': return 3;
      case 'completed': return 4;
      default: return 0;
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Equipment Request & Dispatch Interface
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  const urgentRequests = requests.filter(r => r.priority === 'urgent' && r.status !== 'completed');
  const availableEquipment = equipment.filter(e => e.status === 'available');
  const availablePorters = porters.filter(p => p.status === 'available');

  return (
    <Box sx={{ p: 3, position: 'relative' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Equipment Request & Dispatch Interface
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<Add />}
          onClick={() => setNewRequestDialog(true)}
        >
          New Equipment Request
        </Button>
      </Box>

      {/* Urgent Alerts */}
      {urgentRequests.length > 0 && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="h6">Urgent Equipment Requests!</Typography>
          <Typography>
            {urgentRequests.length} urgent equipment requests require immediate attention.
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
                  {requests.filter(r => r.status === 'pending').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Pending Requests
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <MedicalServices sx={{ fontSize: 40, color: '#1976d2', mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {availableEquipment.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Available Equipment
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <DirectionsRun sx={{ fontSize: 40, color: '#388e3c', mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {availablePorters.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Available Porters
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
                  {requests.filter(r => r.status === 'dispatched').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  In Transit
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Active Equipment Requests */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Active Equipment Requests
          </Typography>
          {requests.length === 0 ? (
            <Alert severity="info">
              No active equipment requests at this time.
            </Alert>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Requester</TableCell>
                    <TableCell>Equipment Type</TableCell>
                    <TableCell>Location</TableCell>
                    <TableCell>Priority</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Progress</TableCell>
                    <TableCell>ETA</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {requests.map((request) => (
                    <TableRow key={request.id}>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" fontWeight="bold">
                            {request.requester_name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {request.requester_department}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <MedicalServices sx={{ mr: 1 }} />
                          <Box>
                            <Typography variant="body2">{request.equipment_type}</Typography>
                            {request.equipment_name && (
                              <Typography variant="caption" color="text.secondary">
                                {request.equipment_name}
                              </Typography>
                            )}
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <LocationOn sx={{ mr: 1, color: 'text.secondary' }} />
                          <Typography variant="body2">
                            {request.requester_location}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={(request.priority || 'unknown').toUpperCase()}
                          color={getPriorityColor(request.priority)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={(request.status || 'unknown').replace('_', ' ').toUpperCase()}
                          color={getStatusColor(request.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ width: 200 }}>
                          <Stepper activeStep={getActiveStep(request.status)} sx={{ fontSize: '0.75rem' }}>
                            {getRequestSteps().map((label, index) => (
                              <Step key={label}>
                                <StepLabel sx={{ fontSize: '0.75rem' }}>
                                  {index === getActiveStep(request.status) ? '' : ''}
                                </StepLabel>
                              </Step>
                            ))}
                          </Stepper>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {request.estimated_delivery_time || 'TBD'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Tooltip title="View Details">
                            <IconButton
                              size="small"
                              onClick={() => {
                                setSelectedRequest(request);
                                setDetailsDialog(true);
                              }}
                            >
                              <Search />
                            </IconButton>
                          </Tooltip>
                          {request.status === 'pending' && (
                            <Tooltip title="Assign Equipment">
                              <IconButton
                                size="small"
                                color="primary"
                                onClick={() => {/* Open assignment dialog */}}
                              >
                                <MedicalServices />
                              </IconButton>
                            </Tooltip>
                          )}
                          {request.status === 'assigned' && (
                            <Tooltip title="Dispatch Porter">
                              <IconButton
                                size="small"
                                color="secondary"
                                onClick={() => {/* Open dispatch dialog */}}
                              >
                                <DirectionsRun />
                              </IconButton>
                            </Tooltip>
                          )}
                          {request.status === 'delivered' && (
                            <Tooltip title="Complete Request">
                              <IconButton
                                size="small"
                                color="success"
                                onClick={() => completeRequest(request.id)}
                              >
                                <CheckCircle />
                              </IconButton>
                            </Tooltip>
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

      {/* Available Equipment Quick View */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Available Equipment for Quick Assignment
          </Typography>
          {availableEquipment.length === 0 ? (
            <Alert severity="info">
              No available equipment found in the database at this time.
            </Alert>
          ) : (
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              {availableEquipment.slice(0, 8).map((item) => (
                <Card key={item.id} variant="outlined" sx={{ minWidth: 250 }}>
                  <CardContent sx={{ p: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <MedicalServices sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="body2" fontWeight="bold">
                        {item.name}
                      </Typography>
                    </Box>
                    <Typography variant="caption" color="text.secondary" display="block">
                      {item.equipment_type} • {item.manufacturer}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                      <LocationOn sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
                      <Typography variant="caption">
                        {item.location}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                      <Chip
                        label={(item.status || 'unknown').toUpperCase()}
                        color="success"
                        size="small"
                      />
                      <Typography variant="caption" color="text.secondary">
                        {item.distance_from_requester || 0}m away
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Porter Status */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Porter Status & Availability
          </Typography>
          {porters.length === 0 ? (
            <Alert severity="info">
              No porters found in the database at this time.
            </Alert>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Porter</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Current Location</TableCell>
                    <TableCell align="right">Active Requests</TableCell>
                    <TableCell>Availability</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {porters.map((porter) => (
                  <TableRow key={porter.id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Avatar sx={{ mr: 2, bgcolor: porter.status === 'available' ? 'success.main' : 'warning.main' }}>
                          <DirectionsRun />
                        </Avatar>
                        <Typography variant="body2" fontWeight="bold">
                          {porter.name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={(porter.status || 'unknown').replace('_', ' ').toUpperCase()}
                        color={porter.status === 'available' ? 'success' : 'warning'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{porter.current_location || 'Unknown'}</TableCell>
                    <TableCell align="right">{porter.active_requests || 0}</TableCell>
                    <TableCell>{porter.estimated_availability || 'Unknown'}</TableCell>
                    <TableCell>
                      {porter.status === 'available' && (
                        <Tooltip title="Assign to Request">
                          <IconButton size="small" color="primary">
                            <Navigation />
                          </IconButton>
                        </Tooltip>
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

      {/* Floating Action Button for Emergency Request */}
      <Fab
        color="error"
        aria-label="emergency request"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => {
          setFormData({ ...formData, priority: 'urgent' });
          setNewRequestDialog(true);
        }}
      >
        <Warning />
      </Fab>

      {/* New Request Dialog */}
      <Dialog open={newRequestDialog} onClose={() => setNewRequestDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Equipment Request</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Requester Name"
              value={formData.requester_name}
              onChange={(e) => setFormData({ ...formData, requester_name: e.target.value })}
              fullWidth
            />
            <TextField
              label="Department"
              value={formData.requester_department}
              onChange={(e) => setFormData({ ...formData, requester_department: e.target.value })}
              fullWidth
            />
            <TextField
              label="Location"
              value={formData.requester_location}
              onChange={(e) => setFormData({ ...formData, requester_location: e.target.value })}
              fullWidth
              placeholder="e.g., ICU Room 205, Emergency Bay 3"
            />
            <FormControl fullWidth>
              <InputLabel>Equipment Type</InputLabel>
              <Select
                value={formData.equipment_type}
                onChange={(e) => setFormData({ ...formData, equipment_type: e.target.value })}
              >
                <MenuItem value="Ventilator">Ventilator</MenuItem>
                <MenuItem value="IV Pump">IV Pump</MenuItem>
                <MenuItem value="Defibrillator">Defibrillator</MenuItem>
                <MenuItem value="Wheelchair">Wheelchair</MenuItem>
                <MenuItem value="Stretcher">Stretcher</MenuItem>
                <MenuItem value="Monitor">Patient Monitor</MenuItem>
                <MenuItem value="Ultrasound">Ultrasound Machine</MenuItem>
                <MenuItem value="X-Ray">Portable X-Ray</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value as any })}
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="urgent">Urgent</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Reason for Request"
              value={formData.reason}
              onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
              multiline
              rows={3}
              fullWidth
              placeholder="Brief description of why this equipment is needed"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewRequestDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={submitRequest}
            disabled={!formData.requester_name || !formData.equipment_type}
          >
            Submit Request
          </Button>
        </DialogActions>
      </Dialog>

      {/* Request Details Dialog */}
      <Dialog open={detailsDialog} onClose={() => setDetailsDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Equipment Request Details
        </DialogTitle>
        <DialogContent>
          {selectedRequest && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Request Information
              </Typography>
              <Box sx={{ mb: 3 }}>
                <Typography><strong>Requester:</strong> {selectedRequest.requester_name}</Typography>
                <Typography><strong>Department:</strong> {selectedRequest.requester_department}</Typography>
                <Typography><strong>Location:</strong> {selectedRequest.requester_location}</Typography>
                <Typography><strong>Equipment Type:</strong> {selectedRequest.equipment_type}</Typography>
                <Typography><strong>Priority:</strong> {selectedRequest.priority}</Typography>
                <Typography><strong>Status:</strong> {selectedRequest.status}</Typography>
                <Typography><strong>Reason:</strong> {selectedRequest.reason}</Typography>
                <Typography><strong>Created:</strong> {new Date(selectedRequest.created_at).toLocaleString()}</Typography>
                {selectedRequest.estimated_delivery_time && (
                  <Typography><strong>ETA:</strong> {selectedRequest.estimated_delivery_time}</Typography>
                )}
                {selectedRequest.assigned_porter && (
                  <Typography><strong>Assigned Porter:</strong> {selectedRequest.assigned_porter}</Typography>
                )}
                {selectedRequest.notes && (
                  <Typography><strong>Notes:</strong> {selectedRequest.notes}</Typography>
                )}
              </Box>

              <Box sx={{ width: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Request Progress
                </Typography>
                <Stepper activeStep={getActiveStep(selectedRequest.status)} orientation="vertical">
                  {getRequestSteps().map((label, index) => (
                    <Step key={label}>
                      <StepLabel>
                        <Typography variant="body2">{label}</Typography>
                      </StepLabel>
                    </Step>
                  ))}
                </Stepper>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialog(false)}>Close</Button>
          {selectedRequest?.status === 'delivered' && (
            <Button
              color="success"
              variant="contained"
              onClick={() => {
                completeRequest(selectedRequest.id);
                setDetailsDialog(false);
              }}
            >
              Mark as Completed
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EquipmentRequestDispatchInterface;
