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
  equipment_name?: string;
  equipment_id?: string;
  porter_id?: string;
  porter_name?: string;
  status: 'pending' | 'assigned' | 'dispatched' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  reason: string;
  requested_at: string;
  assigned_at?: string;
  dispatched_at?: string;
  completed_at?: string;
  estimated_delivery: string;
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
  const [assignEquipmentDialog, setAssignEquipmentDialog] = useState(false);
  const [dispatchPorterDialog, setDispatchPorterDialog] = useState(false);
  const [selectedEquipmentForAssignment, setSelectedEquipmentForAssignment] = useState('');
  const [selectedPorterForDispatch, setSelectedPorterForDispatch] = useState('');
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

  // API Functions
  const fetchRequests = async () => {
    try {
      const response = await axios.get('http://localhost:8000/equipment_tracker/equipment_requests');
      setRequests(response.data.requests || []); // Extract requests array from response
    } catch (error) {
      console.error('Error fetching requests:', error);
      setRequests([]); // Set empty array on error
    }
  };

  const fetchEquipmentData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/equipment_tracker/available_equipment');
      console.log('Equipment API Response:', response.data);
      setEquipment(response.data.equipment || []); // Extract equipment array from response
      console.log('Equipment after setting:', response.data.equipment || []);
    } catch (error) {
      console.error('Error fetching equipment:', error);
      setEquipment([]); // Set empty array on error
    }
  };

  const fetchPorters = async () => {
    try {
      const response = await axios.get('http://localhost:8000/equipment_tracker/porter_status');
      setPorters(response.data.porters || []); // Extract porters array from response
    } catch (error) {
      console.error('Error fetching porters:', error);
      setPorters([]); // Set empty array on error
    }
  };

  const createRequest = async () => {
    try {
      await axios.post('http://localhost:8000/equipment_tracker/create_request', formData);
      await fetchRequests();
      setNewRequestDialog(false);
      setFormData({
        requester_name: '',
        requester_department: '',
        requester_location: '',
        equipment_type: '',
        priority: 'medium',
        reason: '',
      });
    } catch (error) {
      console.error('Error creating request:', error);
    }
  };

  const assignEquipment = async (requestId: string, equipmentId: string) => {
    try {
      await axios.post(`http://localhost:8000/equipment_tracker/assign_equipment/${requestId}`, {
        equipment_id: equipmentId
      });
      await fetchRequests();
      await fetchEquipmentData();
      setAssignEquipmentDialog(false);
      setSelectedEquipmentForAssignment('');
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
      setDispatchPorterDialog(false);
      setSelectedPorterForDispatch('');
    } catch (error) {
      console.error('Error dispatching request:', error);
    }
  };

  const completeRequest = async (requestId: string) => {
    try {
      await axios.post(`http://localhost:8000/equipment_tracker/complete_request/${requestId}`);
      await fetchRequests();
      await fetchEquipmentData();
    } catch (error) {
      console.error('Error completing request:', error);
    }
  };

  // Event Handlers
  const handleAssignEquipment = (request: EquipmentRequest) => {
    setSelectedRequest(request);
    setAssignEquipmentDialog(true);
  };

  const handleDispatchPorter = (request: EquipmentRequest) => {
    setSelectedRequest(request);
    setDispatchPorterDialog(true);
  };

  const confirmAssignEquipment = () => {
    if (selectedRequest && selectedEquipmentForAssignment) {
      assignEquipment(selectedRequest.id, selectedEquipmentForAssignment);
    }
  };

  const confirmDispatchPorter = () => {
    if (selectedRequest && selectedPorterForDispatch) {
      dispatchRequest(selectedRequest.id, selectedPorterForDispatch);
    }
  };

  const handleViewDetails = (request: EquipmentRequest) => {
    setSelectedRequest(request);
    setDetailsDialog(true);
  };

  const handleCompleteRequest = (requestId: string) => {
    completeRequest(requestId);
  };

  useEffect(() => {
    const loadInitialData = async () => {
      setLoading(true);
      try {
        await Promise.all([
          fetchEquipmentData(),
          fetchRequests(),
          fetchPorters()
        ]);
        setLoading(false);
      } catch (error) {
        console.error('Error loading initial data:', error);
        setLoading(false);
      }
    };

    loadInitialData();
    
    // Auto-refresh every 20 seconds
    const interval = setInterval(() => {
      fetchRequests();
      fetchPorters();
    }, 20000);
    
    return () => clearInterval(interval);
  }, []);

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
      case 'dispatched': return 'info';
      case 'assigned': return 'warning';
      case 'pending': return 'default';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>Equipment Request & Dispatch</Typography>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 2 }}>Loading equipment data...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Equipment Request & Dispatch
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setNewRequestDialog(true)}
        >
          New Request
        </Button>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Current Status
          </Typography>
          <Box sx={{ display: 'flex', gap: 4 }}>
            <Box>
              <Typography variant="h4" color="primary">
                {requests.filter(r => r.status === 'pending').length}
              </Typography>
              <Typography variant="body2">Pending Requests</Typography>
            </Box>
            <Box>
              <Typography variant="h4" color="warning.main">
                {requests.filter(r => r.status === 'assigned').length}
              </Typography>
              <Typography variant="body2">Assigned</Typography>
            </Box>
            <Box>
              <Typography variant="h4" color="info.main">
                {requests.filter(r => r.status === 'dispatched').length}
              </Typography>
              <Typography variant="body2">Dispatched</Typography>
            </Box>
            <Box>
              <Typography variant="h4" color="success.main">
                {porters.filter(p => p.status === 'available').length}
              </Typography>
              <Typography variant="body2">Available Porters</Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Equipment Requests
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Request ID</TableCell>
                  <TableCell>Requester</TableCell>
                  <TableCell>Department</TableCell>
                  <TableCell>Equipment Type</TableCell>
                  <TableCell>Priority</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Requested</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {requests.map((request) => (
                  <TableRow key={request.id}>
                    <TableCell>{request.id.substring(0, 8)}</TableCell>
                    <TableCell>{request.requester_name}</TableCell>
                    <TableCell>{request.requester_department}</TableCell>
                    <TableCell>{request.equipment_type}</TableCell>
                    <TableCell>
                      <Chip
                        label={request.priority.toUpperCase()}
                        color={getPriorityColor(request.priority) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={request.status.toUpperCase()}
                        color={getStatusColor(request.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {new Date(request.requested_at).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="View Details">
                          <IconButton 
                            size="small" 
                            onClick={() => handleViewDetails(request)}
                          >
                            <Search />
                          </IconButton>
                        </Tooltip>
                        
                        {request.status === 'pending' && (
                          <Tooltip title="Assign Equipment">
                            <IconButton 
                              size="small"
                              onClick={() => handleAssignEquipment(request)}
                            >
                              <MedicalServices />
                            </IconButton>
                          </Tooltip>
                        )}
                        
                        {request.status === 'assigned' && (
                          <Tooltip title="Dispatch Porter">
                            <IconButton 
                              size="small"
                              onClick={() => handleDispatchPorter(request)}
                            >
                              <DirectionsRun />
                            </IconButton>
                          </Tooltip>
                        )}
                        
                        {request.status === 'dispatched' && (
                          <Tooltip title="Mark Complete">
                            <IconButton 
                              size="small"
                              onClick={() => handleCompleteRequest(request.id)}
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
        </CardContent>
      </Card>

      {/* New Request Dialog */}
      <Dialog open={newRequestDialog} onClose={() => setNewRequestDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Equipment Request</DialogTitle>
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
            />
            <TextField
              label="Equipment Type"
              value={formData.equipment_type}
              onChange={(e) => setFormData({ ...formData, equipment_type: e.target.value })}
              fullWidth
            />
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
              label="Reason"
              value={formData.reason}
              onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
              multiline
              rows={3}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewRequestDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={createRequest}>Create Request</Button>
        </DialogActions>
      </Dialog>

      {/* Request Details Dialog */}
      <Dialog open={detailsDialog} onClose={() => setDetailsDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Request Details</DialogTitle>
        <DialogContent>
          {selectedRequest && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="h6" gutterBottom>Request Information</Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mb: 3 }}>
                <Typography><strong>ID:</strong> {selectedRequest.id}</Typography>
                <Typography><strong>Status:</strong> {selectedRequest.status}</Typography>
                <Typography><strong>Requester:</strong> {selectedRequest.requester_name}</Typography>
                <Typography><strong>Department:</strong> {selectedRequest.requester_department}</Typography>
                <Typography><strong>Location:</strong> {selectedRequest.requester_location}</Typography>
                <Typography><strong>Equipment Type:</strong> {selectedRequest.equipment_type}</Typography>
                <Typography><strong>Priority:</strong> {selectedRequest.priority}</Typography>
                <Typography><strong>Requested:</strong> {new Date(selectedRequest.requested_at).toLocaleString()}</Typography>
              </Box>
              
              {selectedRequest.equipment_name && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="h6" gutterBottom>Assigned Equipment</Typography>
                  <Typography><strong>Equipment:</strong> {selectedRequest.equipment_name}</Typography>
                  {selectedRequest.assigned_at && (
                    <Typography><strong>Assigned:</strong> {new Date(selectedRequest.assigned_at).toLocaleString()}</Typography>
                  )}
                </Box>
              )}
              
              {selectedRequest.porter_name && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="h6" gutterBottom>Assigned Porter</Typography>
                  <Typography><strong>Porter:</strong> {selectedRequest.porter_name}</Typography>
                  {selectedRequest.dispatched_at && (
                    <Typography><strong>Dispatched:</strong> {new Date(selectedRequest.dispatched_at).toLocaleString()}</Typography>
                  )}
                </Box>
              )}
              
              <Box>
                <Typography variant="h6" gutterBottom>Reason</Typography>
                <Typography>{selectedRequest.reason}</Typography>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Assign Equipment Dialog */}
      <Dialog open={assignEquipmentDialog} onClose={() => setAssignEquipmentDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Assign Equipment to Request
        </DialogTitle>
        <DialogContent>
          {selectedRequest && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Request Details
              </Typography>
              <Typography><strong>Requester:</strong> {selectedRequest.requester_name}</Typography>
              <Typography><strong>Department:</strong> {selectedRequest.requester_department}</Typography>
              <Typography><strong>Equipment Type:</strong> {selectedRequest.equipment_type}</Typography>
              <Typography><strong>Priority:</strong> {selectedRequest.priority.toUpperCase()}</Typography>
            </Box>
          )}
          
          <Typography variant="h6" gutterBottom>
            Available Equipment
          </Typography>
          {equipment.length === 0 && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              No equipment data loaded yet. Please wait...
            </Alert>
          )}
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Select Equipment</InputLabel>
            <Select
              value={selectedEquipmentForAssignment}
              onChange={(e) => setSelectedEquipmentForAssignment(e.target.value)}
            >
              {equipment
                .filter(eq => {
                  // Only show available equipment
                  if (eq.status !== 'available') return false;
                  
                  // Handle type mismatches like "IV Pump" vs "IV_PUMP"
                  const normalizeType = (type: string) => 
                    type.toLowerCase().replace(/[_\s-]/g, '');
                  
                  const requestType = normalizeType(selectedRequest?.equipment_type || '');
                  const equipmentType = normalizeType(eq.equipment_type);
                  
                  return requestType === equipmentType;
                })
                .map((eq) => (
                <MenuItem key={eq.id} value={eq.id}>
                  {eq.name} - {eq.equipment_type} ({eq.location}) {eq.battery_level ? `- Battery: ${eq.battery_level}%` : ''}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          {equipment.filter(eq => {
            if (eq.status !== 'available') return false;
            const normalizeType = (type: string) => type.toLowerCase().replace(/[_\s-]/g, '');
            const requestType = normalizeType(selectedRequest?.equipment_type || '');
            const equipmentType = normalizeType(eq.equipment_type);
            return requestType === equipmentType;
          }).length === 0 && equipment.length > 0 && (
            <Alert severity="info" sx={{ mb: 2 }}>
              No available {selectedRequest?.equipment_type} equipment found. 
              Total equipment loaded: {equipment.length}, 
              Available equipment: {equipment.filter(eq => eq.status === 'available').length}
            </Alert>
          )}
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Showing available {selectedRequest?.equipment_type} equipment
          </Typography>
          
          {selectedEquipmentForAssignment && (
            <Alert severity="info" sx={{ mt: 2 }}>
              Equipment will be marked as "in use" and assigned to this request.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAssignEquipmentDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={confirmAssignEquipment}
            disabled={!selectedEquipmentForAssignment}
          >
            Assign Equipment
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dispatch Porter Dialog */}
      <Dialog open={dispatchPorterDialog} onClose={() => setDispatchPorterDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Dispatch Porter for Equipment Request
        </DialogTitle>
        <DialogContent>
          {selectedRequest && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Request Details
              </Typography>
              <Typography><strong>Requester:</strong> {selectedRequest.requester_name}</Typography>
              <Typography><strong>Location:</strong> {selectedRequest.requester_location}</Typography>
              <Typography><strong>Equipment:</strong> {selectedRequest.equipment_name || 'Equipment assigned'}</Typography>
              <Typography><strong>Priority:</strong> {selectedRequest.priority.toUpperCase()}</Typography>
            </Box>
          )}
          
          <Typography variant="h6" gutterBottom>
            Available Porters
          </Typography>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Select Porter</InputLabel>
            <Select
              value={selectedPorterForDispatch}
              onChange={(e) => setSelectedPorterForDispatch(e.target.value)}
            >
              {porters
                .filter(porter => porter.status === 'available')
                .map((porter) => (
                <MenuItem key={porter.id} value={porter.id}>
                  {porter.name} - {porter.current_location} (Active requests: {porter.active_requests})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          {selectedPorterForDispatch && (
            <Alert severity="info" sx={{ mt: 2 }}>
              Porter will be notified and the request status will be updated to "dispatched".
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDispatchPorterDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={confirmDispatchPorter}
            disabled={!selectedPorterForDispatch}
          >
            Dispatch Porter
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EquipmentRequestDispatchInterface;
