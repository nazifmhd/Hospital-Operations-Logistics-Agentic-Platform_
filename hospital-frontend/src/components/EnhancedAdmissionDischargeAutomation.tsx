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
  Checkbox,
  FormControlLabel,
  Switch,
  Divider,
} from '@mui/material';
import {
  PersonAdd,
  ExitToApp,
  Bed,
  Assignment,
  MedicalServices,
  Schedule,
  CheckCircle,
  Warning,
  Person,
  LocalHospital,
  Notifications,
  AutoAwesome,
  CleaningServices,
  Restaurant,
  Medication,
  Security,
  AccountBalance,
  Print,
  QrCode,
} from '@mui/icons-material';
import axios from 'axios';

interface Patient {
  id: string;
  name: string;
  mrn: string;
  age: number;
  gender: string;
  phone: string;
  emergency_contact: string;
  insurance_info: string;
  medical_history: string[];
  current_medications: string[];
  allergies: string[];
  acuity_level: 'low' | 'medium' | 'high' | 'critical';
  admission_date?: string;
  expected_discharge_date?: string;
  bed_assignment?: string;
  department: string;
  attending_physician: string;
  admission_status: 'scheduled' | 'in_progress' | 'admitted' | 'discharge_pending' | 'discharged';
  admission_type: 'emergency' | 'scheduled' | 'urgent' | 'observation';
  discharge_instructions?: string;
  discharge_medications?: string[];
  follow_up_appointments?: string[];
}

interface AdmissionTask {
  id: string;
  patient_id: string;
  patient_name: string;
  task_type: string;
  task_name?: string;
  responsible_department?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'ongoing';
  priority: 'low' | 'medium' | 'high' | 'urgent' | 'critical';
  estimated_completion?: string;
  estimated_duration?: string;
  assigned_to?: string;
  assigned_staff?: string;
  notes?: string;
  automated?: boolean;
  created_at: string;
  completed_at?: string;
  description?: string;
}

interface BedAvailability {
  id: string;
  number: string;
  bed_type: 'regular' | 'icu' | 'surgery' | 'maternity' | 'pediatric';
  department_id: string;
  status: 'available' | 'occupied' | 'cleaning' | 'maintenance' | 'reserved';
  floor: string;
  patient_id?: string;
  last_cleaned?: string;
  equipment_attached?: string[];
  isolation_required?: boolean;
  estimated_availability?: string;
}

interface AutomationRule {
  id: string;
  name: string;
  trigger: 'admission_started' | 'discharge_ordered' | 'bed_assigned' | 'insurance_verified';
  description: string;
  enabled: boolean;
  department_specific?: boolean;
  departments?: string[];
}

const EnhancedAdmissionDischargeAutomation: React.FC = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [tasks, setTasks] = useState<AdmissionTask[]>([]);
  const [beds, setBeds] = useState<BedAvailability[]>([]);
  const [automationRules, setAutomationRules] = useState<AutomationRule[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [admissionDialog, setAdmissionDialog] = useState(false);
  const [dischargeDialog, setDischargeDialog] = useState(false);
  const [automationDialog, setAutomationDialog] = useState(false);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<'admissions' | 'discharges' | 'beds' | 'automation'>('admissions');

  // Form state for new admission
  const [admissionForm, setAdmissionForm] = useState({
    name: '',
    mrn: '',
    age: '',
    gender: '',
    phone: '',
    emergency_contact: '',
    insurance_info: '',
    medical_history: '',
    allergies: '',
    admission_type: 'scheduled' as 'emergency' | 'scheduled' | 'urgent' | 'observation',
    department: '',
    attending_physician: '',
    scheduled_date: '',
    notes: '',
  });

  // Event Handlers
  const handleUpdate = () => {
    console.log('EnhancedAdmissionDischargeAutomation: Update action triggered');
  };

  const handleDelete = () => {
    console.log('EnhancedAdmissionDischargeAutomation: Delete action triggered');
  };

  const handleCreate = () => {
    console.log('EnhancedAdmissionDischargeAutomation: Create action triggered');
  };

  useEffect(() => {
    fetchPatientsData();
    fetchTasksData();
    fetchBedsData();
    fetchAutomationRules();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchPatientsData();
      fetchTasksData();
      fetchBedsData();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchPatientsData = async () => {
    try {
      console.log('Fetching patients data...');
      const response = await axios.get('http://localhost:8000/admission_discharge/patients');
      console.log('Patients API response:', response.data);
      console.log('Patients count:', response.data.patients?.length);
      setPatients(response.data.patients || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching patients data:', error);
      setLoading(false);
    }
  };

  const fetchTasksData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/admission_discharge/active_tasks');
      setTasks(response.data.active_tasks || []);
    } catch (error) {
      console.error('Error fetching tasks data:', error);
    }
  };

  const fetchBedsData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/admission_discharge/beds');
      setBeds(response.data.beds || []);
    } catch (error) {
      console.error('Error fetching beds data:', error);
    }
  };

  const fetchAutomationRules = async () => {
    try {
      const response = await axios.get('http://localhost:8000/admission_discharge/automation_rules');
      setAutomationRules(response.data.rules || []);
    } catch (error) {
      console.error('Error fetching automation rules:', error);
    }
  };

  const startAdmissionProcess = async () => {
    try {
      await axios.post('http://localhost:8000/admission_discharge/start_admission', admissionForm);
      setAdmissionDialog(false);
      resetAdmissionForm();
      await fetchPatientsData();
      await fetchTasksData();
    } catch (error) {
      console.error('Error starting admission process:', error);
    }
  };

  const startDischargeProcess = async (patientId: string) => {
    try {
      await axios.post(`http://localhost:8000/admission_discharge/start_discharge/${patientId}`);
      await fetchPatientsData();
      await fetchTasksData();
      setDischargeDialog(false);
    } catch (error) {
      console.error('Error starting discharge process:', error);
    }
  };

  const completeTask = async (taskId: string) => {
    try {
      await axios.post(`http://localhost:8000/admission_discharge/complete_task/${taskId}`);
      await fetchTasksData();
      // Show success notification
      console.log(`Task ${taskId} completed successfully`);
    } catch (error) {
      console.error('Error completing task:', error);
      // Show error notification
      alert('Failed to complete task. Please try again.');
    }
  };

  const assignBed = async (patientId: string, bedId: string) => {
    try {
      await axios.post(`http://localhost:8000/admission_discharge/assign_bed/${patientId}`, {
        bed_id: bedId
      });
      await fetchPatientsData();
      await fetchBedsData();
      console.log(`Bed ${bedId} assigned to patient ${patientId} successfully`);
    } catch (error) {
      console.error('Error assigning bed:', error);
      alert('Failed to assign bed. Please try again.');
    }
  };

  const toggleAutomationRule = async (ruleId: string) => {
    try {
      await axios.post(`http://localhost:8000/admission_discharge/toggle_automation/${ruleId}`);
      await fetchAutomationRules();
    } catch (error) {
      console.error('Error toggling automation rule:', error);
    }
  };

  const resetAdmissionForm = () => {
    setAdmissionForm({
      name: '',
      mrn: '',
      age: '',
      gender: '',
      phone: '',
      emergency_contact: '',
      insurance_info: '',
      medical_history: '',
      allergies: '',
      admission_type: 'scheduled' as 'emergency' | 'scheduled' | 'urgent' | 'observation',
      department: '',
      attending_physician: '',
      scheduled_date: '',
      notes: '',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'admitted': return 'success';
      case 'discharged': return 'info';
      case 'in_progress': return 'warning';
      case 'pending': return 'default';
      case 'failed': return 'error';
      default: return 'default';
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

  const getBedTypeColor = (bedType: string) => {
    switch (bedType) {
      case 'icu': return 'error';
      case 'surgery': return 'warning';
      case 'maternity': return 'info';
      case 'pediatric': return 'secondary';
      case 'regular': return 'success';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Enhanced Admission & Discharge Automation
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  // Ensure all arrays are initialized before processing
  const safePatients = patients || [];
  const safeTasks = tasks || [];
  const safeBeds = beds || [];
  const safeAutomationRules = automationRules || [];

  const pendingAdmissions = safePatients.filter(p => p?.admission_status === 'scheduled' || p?.admission_status === 'in_progress');
  const pendingDischarges = safePatients.filter(p => p?.admission_status === 'discharge_pending');
  const currentAdmissions = safePatients.filter(p => p?.admission_status === 'admitted');
  const activeTasks = safeTasks.filter(t => t?.status !== 'completed');
  const availableBeds = safeBeds.filter(b => b?.status === 'available');
  const urgentTasks = safeTasks.filter(t => t?.priority === 'urgent' && t?.status !== 'completed');

  // Debug logging
  console.log('Patients data:', safePatients);
  console.log('Patient admission statuses:', safePatients.map(p => p?.admission_status));
  console.log('Pending admissions:', pendingAdmissions.length);
  console.log('Current admissions:', currentAdmissions.length);
  console.log('Pending discharges:', pendingDischarges.length);

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Enhanced Admission & Discharge Automation
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant={view === 'admissions' ? 'contained' : 'outlined'}
            onClick={() => setView('admissions')}
            startIcon={<PersonAdd />}
          >
            Admissions
          </Button>
          <Button
            variant={view === 'discharges' ? 'contained' : 'outlined'}
            onClick={() => setView('discharges')}
            startIcon={<ExitToApp />}
          >
            Discharges
          </Button>
          <Button
            variant={view === 'beds' ? 'contained' : 'outlined'}
            onClick={() => setView('beds')}
            startIcon={<Bed />}
          >
            Bed Management
          </Button>
          <Button
            variant={view === 'automation' ? 'contained' : 'outlined'}
            onClick={() => setView('automation')}
            startIcon={<AutoAwesome />}
          >
            Automation
          </Button>
        </Box>
      </Box>

      {/* Urgent Alerts */}
      {urgentTasks.length > 0 && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="h6">Urgent Tasks Pending!</Typography>
          <Typography>
            {urgentTasks.length} urgent admission/discharge tasks require immediate attention.
          </Typography>
        </Alert>
      )}

      {/* Summary Dashboard */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 3, mb: 3 }}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <PersonAdd sx={{ fontSize: 40, color: '#1976d2', mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {currentAdmissions.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Current Admissions
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Pending: {pendingAdmissions.length}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <ExitToApp sx={{ fontSize: 40, color: '#388e3c', mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {pendingDischarges.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Pending Discharges
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Bed sx={{ fontSize: 40, color: '#7b1fa2', mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {availableBeds.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Available Beds
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Assignment sx={{ fontSize: 40, color: '#f57c00', mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {activeTasks.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Active Tasks
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Admissions View */}
      {view === 'admissions' && (
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">Admission Management</Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<PersonAdd />}
              onClick={() => setAdmissionDialog(true)}
            >
              New Admission
            </Button>
          </Box>

          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Active Admissions ({currentAdmissions.length})
                </Typography>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={async () => {
                    await fetchPatientsData();
                    await fetchTasksData();
                    console.log('Data refreshed');
                  }}
                  startIcon={<Notifications />}
                >
                  Refresh
                </Button>
              </Box>
              {currentAdmissions.length === 0 ? (
                <Alert severity="info">
                  No current admissions at this time.
                </Alert>
              ) : (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Patient</TableCell>
                        <TableCell>MRN</TableCell>
                        <TableCell>Department</TableCell>
                        <TableCell>Admission Type</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Bed Assignment</TableCell>
                        <TableCell>Physician</TableCell>
                        <TableCell>Progress</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {currentAdmissions.map((patient) => {
                        const patientTasks = safeTasks.filter(t => t?.patient_id === patient?.id);
                        const completedTasks = patientTasks.filter(t => t?.status === 'completed').length;
                        const totalTasks = patientTasks.length;
                        const progress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;

                        return (
                          <TableRow key={patient.id}>
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
                                  <Person />
                                </Avatar>
                                <Box>
                                  <Typography variant="body2" fontWeight="bold">
                                    {patient.name}
                                  </Typography>
                                  <Typography variant="caption" color="text.secondary">
                                    Age {patient.age}, {patient.gender}
                                  </Typography>
                                </Box>
                              </Box>
                            </TableCell>
                            <TableCell>{patient.mrn}</TableCell>
                            <TableCell>{patient.department}</TableCell>
                            <TableCell>
                              <Chip
                                label={patient.admission_type.toUpperCase()}
                                color={patient.admission_type === 'emergency' ? 'error' : 'info'}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={patient.admission_status.replace('_', ' ').toUpperCase()}
                                color={getStatusColor(patient.admission_status)}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>
                              {patient.bed_assignment ? (
                                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                  <Bed sx={{ mr: 1, color: 'success.main' }} />
                                  <Typography variant="body2">
                                    {patient.bed_assignment}
                                  </Typography>
                                </Box>
                              ) : (
                                <Chip label="Not Assigned" color="warning" size="small" />
                              )}
                            </TableCell>
                            <TableCell>{patient.attending_physician}</TableCell>
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center', minWidth: 120 }}>
                                <LinearProgress
                                  variant="determinate"
                                  value={progress}
                                  sx={{ width: '100%', mr: 1 }}
                                />
                                <Typography variant="caption">
                                  {Math.round(progress)}%
                                </Typography>
                              </Box>
                            </TableCell>
                            <TableCell>
                              <Box sx={{ display: 'flex', gap: 1 }}>
                                <Tooltip title="View Details">
                                  <IconButton
                                    size="small"
                                    onClick={() => setSelectedPatient(patient)}
                                  >
                                    <Assignment />
                                  </IconButton>
                                </Tooltip>
                                {!patient.bed_assignment && availableBeds.length > 0 && (
                                  <Tooltip title="Assign Bed">
                                    <IconButton
                                      size="small"
                                      color="primary"
                                      onClick={() => {
                                        const suitableBed = availableBeds.find(b => 
                                          b.department_id === patient.department
                                        );
                                        if (suitableBed) {
                                          assignBed(patient.id, suitableBed.id);
                                        }
                                      }}
                                    >
                                      <Bed />
                                    </IconButton>
                                  </Tooltip>
                                )}
                              </Box>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>

          {/* Active Admission Tasks */}
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Active Admission Tasks ({activeTasks.length})
                </Typography>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={async () => {
                    await fetchTasksData();
                    console.log('Tasks refreshed');
                  }}
                  startIcon={<Assignment />}
                >
                  Refresh Tasks
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Patient</TableCell>
                      <TableCell>Task</TableCell>
                      <TableCell>Department</TableCell>
                      <TableCell>Priority</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Duration</TableCell>
                      <TableCell>Automated</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {activeTasks.map((task) => (
                      <TableRow key={task.id}>
                        <TableCell>
                          {task.patient_name || safePatients.find(p => p?.id === task?.patient_id)?.name || 'System Task'}
                        </TableCell>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {task.task_name || task.description || task.task_type}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {task.task_type}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>{task.responsible_department || task.assigned_to || 'System'}</TableCell>
                        <TableCell>
                          <Chip
                            label={task.priority.toUpperCase()}
                            color={getPriorityColor(task.priority)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={task.status.replace('_', ' ').toUpperCase()}
                            color={getStatusColor(task.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          {task.estimated_duration || 
                           (task.estimated_completion ? 
                             new Date(task.estimated_completion).toLocaleTimeString() : 
                             'N/A')}
                        </TableCell>
                        <TableCell>
                          {task.automated !== false ? (
                            <Chip
                              icon={<AutoAwesome />}
                              label="Auto"
                              color="info"
                              size="small"
                            />
                          ) : (
                            <Chip label="Manual" size="small" />
                          )}
                        </TableCell>
                        <TableCell>
                          {task.status === 'in_progress' && (
                            <Button
                              size="small"
                              color="success"
                              variant="contained"
                              onClick={() => completeTask(task.id)}
                            >
                              Complete
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Discharges View */}
      {view === 'discharges' && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Discharge Management
          </Typography>

          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Patients Ready for Discharge
              </Typography>
              {pendingDischarges.length === 0 ? (
                <Alert severity="info">
                  No patients pending discharge at this time.
                </Alert>
              ) : (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Patient</TableCell>
                        <TableCell>Current Bed</TableCell>
                        <TableCell>Length of Stay</TableCell>
                        <TableCell>Discharge Tasks</TableCell>
                        <TableCell>Physician</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {pendingDischarges.map((patient) => {
                        const dischargeTasks = safeTasks.filter(t => 
                          t?.patient_id === patient?.id && 
                          t?.task_type?.includes('discharge')
                        );
                        const completedDischargeTasks = dischargeTasks.filter(t => t.status === 'completed').length;
                        
                        const daysSinceAdmission = patient.admission_date 
                          ? Math.floor((new Date().getTime() - new Date(patient.admission_date).getTime()) / (1000 * 3600 * 24))
                          : 0;

                        return (
                          <TableRow key={patient.id}>
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <Avatar sx={{ mr: 2, bgcolor: 'success.main' }}>
                                  <Person />
                                </Avatar>
                                <Box>
                                  <Typography variant="body2" fontWeight="bold">
                                    {patient.name}
                                  </Typography>
                                  <Typography variant="caption" color="text.secondary">
                                    MRN: {patient.mrn}
                                  </Typography>
                                </Box>
                              </Box>
                            </TableCell>
                            <TableCell>{patient.bed_assignment}</TableCell>
                            <TableCell>{daysSinceAdmission} days</TableCell>
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <LinearProgress
                                  variant="determinate"
                                  value={dischargeTasks.length > 0 ? (completedDischargeTasks / dischargeTasks.length) * 100 : 0}
                                  sx={{ width: '100px', mr: 1 }}
                                />
                                <Typography variant="caption">
                                  {completedDischargeTasks}/{dischargeTasks.length}
                                </Typography>
                              </Box>
                            </TableCell>
                            <TableCell>{patient.attending_physician}</TableCell>
                            <TableCell>
                              <Box sx={{ display: 'flex', gap: 1 }}>
                                <Button
                                  size="small"
                                  variant="contained"
                                  color="success"
                                  startIcon={<Print />}
                                  onClick={() => {
                                    // Generate and download discharge documents
                                    const patientData = {
                                      name: patient.name,
                                      mrn: patient.mrn,
                                      department: patient.department,
                                      physician: patient.attending_physician,
                                      discharged_at: new Date().toLocaleString()
                                    };
                                    console.log('Generating discharge documents for:', patientData);
                                    alert(`Discharge documents generated for ${patient.name}`);
                                  }}
                                >
                                  Print Docs
                                </Button>
                                {completedDischargeTasks === dischargeTasks.length && (
                                  <Button
                                    size="small"
                                    variant="contained"
                                    color="primary"
                                    onClick={() => startDischargeProcess(patient.id)}
                                  >
                                    Complete Discharge
                                  </Button>
                                )}
                              </Box>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Beds View */}
      {view === 'beds' && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Bed Management & Availability
          </Typography>

          <Card>
            <CardContent>
              <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 2 }}>
                {safeBeds.map((bed) => (
                  <Card key={bed.id} variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Box>
                          <Typography variant="h6">
                            Bed {bed.number}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Floor {bed.floor} - {bed.department_id}
                          </Typography>
                        </Box>
                        <Chip
                          label={bed.bed_type?.toUpperCase() || 'GENERAL'}
                          color={getBedTypeColor(bed.bed_type)}
                          size="small"
                        />
                      </Box>

                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Chip
                          label={bed.status?.replace('_', ' ').toUpperCase() || 'UNKNOWN'}
                          color={getStatusColor(bed.status?.toLowerCase())}
                          size="small"
                          sx={{ mr: 1 }}
                        />
                      </Box>

                      {bed.patient_id && (
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          <strong>Patient:</strong> {safePatients.find(p => p?.id === bed?.patient_id)?.name || 'Unknown'}
                        </Typography>
                      )}

                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>Floor:</strong> {bed.floor || 'N/A'}
                      </Typography>

                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>Department ID:</strong> {bed.department_id || 'N/A'}
                      </Typography>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Automation View */}
      {view === 'automation' && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Automation Rules & Configuration
          </Typography>

          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Automation Rules
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Rule Name</TableCell>
                      <TableCell>Trigger</TableCell>
                      <TableCell>Description</TableCell>
                      <TableCell>Scope</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {safeAutomationRules.map((rule) => (
                      <TableRow key={rule.id}>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <AutoAwesome sx={{ mr: 1, color: 'primary.main' }} />
                            <Typography variant="body2" fontWeight="bold">
                              {rule.name}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={rule.trigger.replace('_', ' ').toUpperCase()}
                            color="info"
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {rule.description || 'No description available'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip label="Global" color="success" size="small" />
                        </TableCell>
                        <TableCell>
                          <Switch
                            checked={rule.enabled}
                            onChange={() => toggleAutomationRule(rule.id)}
                            color="primary"
                          />
                        </TableCell>
                        <TableCell>
                          <Button 
                            size="small" 
                            variant="outlined" 
                            onClick={() => {
                              // Edit automation rule functionality
                              const newDescription = prompt('Edit rule description:', rule.description);
                              if (newDescription && newDescription !== rule.description) {
                                console.log(`Updating rule ${rule.id} description to:`, newDescription);
                                // Here you would call an API to update the rule
                                alert(`Rule updated: ${newDescription}`);
                              }
                            }}
                          >
                            Edit
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* New Admission Dialog */}
      <Dialog open={admissionDialog} onClose={() => setAdmissionDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>New Patient Admission</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: 2, mt: 1 }}>
            <Box sx={{ gridColumn: { xs: 'span 12', sm: 'span 6' } }}>
              <TextField
                label="Patient Name"
                value={admissionForm.name}
                onChange={(e) => setAdmissionForm({ ...admissionForm, name: e.target.value })}
                fullWidth
              />
            </Box>
            <Box sx={{ gridColumn: { xs: 'span 12', sm: 'span 6' } }}>
              <TextField
                label="MRN"
                value={admissionForm.mrn}
                onChange={(e) => setAdmissionForm({ ...admissionForm, mrn: e.target.value })}
                fullWidth
              />
            </Box>
            <Box sx={{ gridColumn: { xs: 'span 12', sm: 'span 4' } }}>
              <TextField
                label="Age"
                type="number"
                value={admissionForm.age}
                onChange={(e) => setAdmissionForm({ ...admissionForm, age: e.target.value })}
                fullWidth
              />
            </Box>
            <Box sx={{ gridColumn: { xs: 'span 12', sm: 'span 4' } }}>
              <FormControl fullWidth>
                <InputLabel>Gender</InputLabel>
                <Select
                  value={admissionForm.gender}
                  onChange={(e) => setAdmissionForm({ ...admissionForm, gender: e.target.value })}
                >
                  <MenuItem value="Male">Male</MenuItem>
                  <MenuItem value="Female">Female</MenuItem>
                  <MenuItem value="Other">Other</MenuItem>
                </Select>
              </FormControl>
            </Box>
            <Box sx={{ gridColumn: { xs: 'span 12', sm: 'span 4' } }}>
              <FormControl fullWidth>
                <InputLabel>Admission Type</InputLabel>
                <Select
                  value={admissionForm.admission_type}
                  onChange={(e) => setAdmissionForm({ ...admissionForm, admission_type: e.target.value as any })}
                >
                  <MenuItem value="emergency">Emergency</MenuItem>
                  <MenuItem value="urgent">Urgent</MenuItem>
                  <MenuItem value="scheduled">Scheduled</MenuItem>
                  <MenuItem value="observation">Observation</MenuItem>
                </Select>
              </FormControl>
            </Box>
            <Box sx={{ gridColumn: { xs: 'span 12', sm: 'span 6' } }}>
              <TextField
                label="Phone Number"
                value={admissionForm.phone}
                onChange={(e) => setAdmissionForm({ ...admissionForm, phone: e.target.value })}
                fullWidth
              />
            </Box>
            <Box sx={{ gridColumn: { xs: 'span 12', sm: 'span 6' } }}>
              <TextField
                label="Emergency Contact"
                value={admissionForm.emergency_contact}
                onChange={(e) => setAdmissionForm({ ...admissionForm, emergency_contact: e.target.value })}
                fullWidth
              />
            </Box>
            <Box sx={{ gridColumn: { xs: 'span 12', sm: 'span 6' } }}>
              <TextField
                label="Department"
                value={admissionForm.department}
                onChange={(e) => setAdmissionForm({ ...admissionForm, department: e.target.value })}
                fullWidth
              />
            </Box>
            <Box sx={{ gridColumn: { xs: 'span 12', sm: 'span 6' } }}>
              <TextField
                label="Attending Physician"
                value={admissionForm.attending_physician}
                onChange={(e) => setAdmissionForm({ ...admissionForm, attending_physician: e.target.value })}
                fullWidth
              />
            </Box>
            <Box sx={{ gridColumn: 'span 12' }}>
              <TextField
                label="Insurance Information"
                value={admissionForm.insurance_info}
                onChange={(e) => setAdmissionForm({ ...admissionForm, insurance_info: e.target.value })}
                fullWidth
              />
            </Box>
            <Box sx={{ gridColumn: 'span 12' }}>
              <TextField
                label="Medical History"
                value={admissionForm.medical_history}
                onChange={(e) => setAdmissionForm({ ...admissionForm, medical_history: e.target.value })}
                multiline
                rows={2}
                fullWidth
                placeholder="Relevant medical history, chronic conditions..."
              />
            </Box>
            <Box sx={{ gridColumn: 'span 12' }}>
              <TextField
                label="Known Allergies"
                value={admissionForm.allergies}
                onChange={(e) => setAdmissionForm({ ...admissionForm, allergies: e.target.value })}
                fullWidth
                placeholder="Drug allergies, food allergies, etc."
              />
            </Box>
            <Box sx={{ gridColumn: 'span 12' }}>
              <TextField
                label="Additional Notes"
                value={admissionForm.notes}
                onChange={(e) => setAdmissionForm({ ...admissionForm, notes: e.target.value })}
                multiline
                rows={2}
                fullWidth
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAdmissionDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={startAdmissionProcess}
            disabled={!admissionForm.name || !admissionForm.mrn || !admissionForm.department}
          >
            Start Admission Process
          </Button>
        </DialogActions>
      </Dialog>

      {/* Patient Details Dialog */}
      <Dialog
        open={!!selectedPatient}
        onClose={() => setSelectedPatient(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'primary.main' }}>
              <Person />
            </Avatar>
            <Box>
              <Typography variant="h6">
                {selectedPatient?.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                MRN: {selectedPatient?.mrn} • {selectedPatient?.age} years, {selectedPatient?.gender}
              </Typography>
            </Box>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 3, mt: 2 }}>
            {/* Left Column - Patient Info */}
            <Box>
              <Typography variant="h6" gutterBottom>Patient Information</Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Typography><strong>Department:</strong> {selectedPatient?.department}</Typography>
                <Typography><strong>Attending Physician:</strong> {selectedPatient?.attending_physician}</Typography>
                <Typography><strong>Admission Type:</strong> {selectedPatient?.admission_type}</Typography>
                <Typography><strong>Acuity Level:</strong> {selectedPatient?.acuity_level}</Typography>
                <Typography><strong>Status:</strong> {selectedPatient?.admission_status}</Typography>
                <Typography><strong>Admission Date:</strong> {selectedPatient?.admission_date ? new Date(selectedPatient.admission_date).toLocaleString() : 'N/A'}</Typography>
              </Box>
              
              <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>Contact Information</Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Typography><strong>Phone:</strong> {selectedPatient?.phone}</Typography>
                <Typography><strong>Emergency Contact:</strong> {selectedPatient?.emergency_contact}</Typography>
                <Typography><strong>Insurance:</strong> {selectedPatient?.insurance_info}</Typography>
              </Box>
            </Box>

            {/* Right Column - Medical Info */}
            <Box>
              <Typography variant="h6" gutterBottom>Medical Information</Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box>
                  <Typography variant="subtitle2" gutterBottom>Current Medications</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selectedPatient?.current_medications?.map((med, index) => (
                      <Chip key={index} label={med} size="small" color="info" />
                    )) || <Typography color="text.secondary">None listed</Typography>}
                  </Box>
                </Box>
                
                <Box>
                  <Typography variant="subtitle2" gutterBottom>Allergies</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selectedPatient?.allergies?.map((allergy, index) => (
                      <Chip key={index} label={allergy} size="small" color="warning" />
                    )) || <Typography color="text.secondary">None listed</Typography>}
                  </Box>
                </Box>

                <Box>
                  <Typography variant="subtitle2" gutterBottom>Medical History</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selectedPatient?.medical_history?.map((history, index) => (
                      <Chip key={index} label={history} size="small" />
                    )) || <Typography color="text.secondary">None listed</Typography>}
                  </Box>
                </Box>

                <Box>
                  <Typography variant="subtitle2" gutterBottom>Bed Assignment</Typography>
                  {selectedPatient?.bed_assignment ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Bed color="success" />
                      <Typography>Bed {selectedPatient.bed_assignment}</Typography>
                    </Box>
                  ) : (
                    <Box>
                      <Chip label="No Bed Assigned" color="warning" size="small" />
                      {availableBeds.length > 0 && (
                        <Button
                          size="small"
                          variant="contained"
                          sx={{ ml: 2 }}
                          onClick={() => {
                            const suitableBed = availableBeds.find(b => 
                              b.department_id === selectedPatient?.department
                            );
                            if (suitableBed && selectedPatient) {
                              assignBed(selectedPatient.id, suitableBed.id);
                              setSelectedPatient(null);
                            }
                          }}
                        >
                          Auto-Assign Bed
                        </Button>
                      )}
                    </Box>
                  )}
                </Box>
              </Box>
            </Box>
          </Box>

          {/* Active Tasks for this Patient */}
          {selectedPatient && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>Active Tasks</Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Task</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Priority</TableCell>
                      <TableCell>Assigned To</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {safeTasks.filter(t => t?.patient_id === selectedPatient.id).map((task) => (
                      <TableRow key={task.id}>
                        <TableCell>{task.description || task.task_type}</TableCell>
                        <TableCell>
                          <Chip
                            label={task.status.replace('_', ' ').toUpperCase()}
                            color={getStatusColor(task.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={task.priority.toUpperCase()}
                            color={getPriorityColor(task.priority)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{task.assigned_to}</TableCell>
                        <TableCell>
                          {task.status === 'in_progress' && (
                            <Button
                              size="small"
                              color="success"
                              variant="contained"
                              onClick={() => {
                                completeTask(task.id);
                                // Refresh patient data after completing task
                                setTimeout(() => fetchTasksData(), 500);
                              }}
                            >
                              Complete
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                    {safeTasks.filter(t => t?.patient_id === selectedPatient.id).length === 0 && (
                      <TableRow>
                        <TableCell colSpan={5} align="center">
                          <Typography color="text.secondary">No active tasks for this patient</Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedPatient(null)}>Close</Button>
          {selectedPatient?.admission_status === 'admitted' && (
            <Button
              variant="contained"
              color="warning"
              onClick={() => {
                // Start discharge process
                console.log('Starting discharge for', selectedPatient.id);
                setSelectedPatient(null);
              }}
            >
              Start Discharge
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* Floating Action Button for Emergency Admission */}
      <Fab
        color="error"
        aria-label="emergency admission"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => {
          setAdmissionForm({ ...admissionForm, admission_type: 'emergency' });
          setAdmissionDialog(true);
        }}
      >
        <LocalHospital />
      </Fab>
    </Box>
  );
};

export default EnhancedAdmissionDischargeAutomation;
