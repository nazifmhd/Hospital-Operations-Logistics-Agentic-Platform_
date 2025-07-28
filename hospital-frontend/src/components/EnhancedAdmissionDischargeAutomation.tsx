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
  task_type: string;
  task_name: string;
  responsible_department: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  estimated_duration: string;
  assigned_staff?: string;
  notes?: string;
  automated: boolean;
  created_at: string;
  completed_at?: string;
}

interface BedAvailability {
  id: string;
  room_number: string;
  bed_number: string;
  department: string;
  bed_type: 'regular' | 'icu' | 'surgery' | 'maternity' | 'pediatric';
  status: 'available' | 'occupied' | 'cleaning' | 'maintenance' | 'reserved';
  patient_id?: string;
  last_cleaned: string;
  equipment_attached: string[];
  isolation_required: boolean;
  estimated_availability?: string;
}

interface AutomationRule {
  id: string;
  name: string;
  trigger: 'admission_started' | 'discharge_ordered' | 'bed_assigned' | 'insurance_verified';
  actions: string[];
  enabled: boolean;
  department_specific: boolean;
  departments: string[];
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
      const response = await axios.get('http://localhost:8000/admission_discharge/patients');
      setPatients(response.data.patients || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching patients data:', error);
      setLoading(false);
    }
  };

  const fetchTasksData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/admission_discharge/tasks');
      setTasks(response.data.tasks || []);
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
    } catch (error) {
      console.error('Error completing task:', error);
    }
  };

  const assignBed = async (patientId: string, bedId: string) => {
    try {
      await axios.post(`http://localhost:8000/admission_discharge/assign_bed/${patientId}`, {
        bed_id: bedId
      });
      await fetchPatientsData();
      await fetchBedsData();
    } catch (error) {
      console.error('Error assigning bed:', error);
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

  const pendingAdmissions = patients.filter(p => p.admission_status === 'scheduled' || p.admission_status === 'in_progress');
  const pendingDischarges = patients.filter(p => p.admission_status === 'discharge_pending');
  const activeTasks = tasks.filter(t => t.status !== 'completed');
  const availableBeds = beds.filter(b => b.status === 'available');
  const urgentTasks = tasks.filter(t => t.priority === 'urgent' && t.status !== 'completed');

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
                  {pendingAdmissions.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Pending Admissions
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
              <Typography variant="h6" gutterBottom>
                Active Admissions
              </Typography>
              {pendingAdmissions.length === 0 ? (
                <Alert severity="info">
                  No pending admissions at this time.
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
                      {pendingAdmissions.map((patient) => {
                        const patientTasks = tasks.filter(t => t.patient_id === patient.id);
                        const completedTasks = patientTasks.filter(t => t.status === 'completed').length;
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
                                          b.department === patient.department
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
              <Typography variant="h6" gutterBottom>
                Active Admission Tasks
              </Typography>
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
                    {activeTasks.filter(t => 
                      patients.some(p => p.id === t.patient_id && 
                        (p.admission_status === 'scheduled' || p.admission_status === 'in_progress'))
                    ).map((task) => (
                      <TableRow key={task.id}>
                        <TableCell>
                          {patients.find(p => p.id === task.patient_id)?.name || 'Unknown'}
                        </TableCell>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {task.task_name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {task.task_type}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>{task.responsible_department}</TableCell>
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
                        <TableCell>{task.estimated_duration}</TableCell>
                        <TableCell>
                          {task.automated ? (
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
                        const dischargeTasks = tasks.filter(t => 
                          t.patient_id === patient.id && 
                          t.task_type.includes('discharge')
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
                                  onClick={() => console.log("Print Docs clicked")}
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
                {beds.map((bed) => (
                  <Card key={bed.id} variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Box>
                          <Typography variant="h6">
                            Room {bed.room_number} - Bed {bed.bed_number}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {bed.department}
                          </Typography>
                        </Box>
                        <Chip
                          label={bed.bed_type.toUpperCase()}
                          color={getBedTypeColor(bed.bed_type)}
                          size="small"
                        />
                      </Box>

                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Chip
                          label={bed.status.replace('_', ' ').toUpperCase()}
                          color={getStatusColor(bed.status)}
                          size="small"
                          sx={{ mr: 1 }}
                        />
                        {bed.isolation_required && (
                          <Chip
                            label="ISOLATION"
                            color="warning"
                            size="small"
                            sx={{ mr: 1 }}
                          />
                        )}
                      </Box>

                      {bed.patient_id && (
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          <strong>Patient:</strong> {patients.find(p => p.id === bed.patient_id)?.name || 'Unknown'}
                        </Typography>
                      )}

                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>Last Cleaned:</strong> {new Date(bed.last_cleaned).toLocaleDateString()}
                      </Typography>

                      {bed.equipment_attached.length > 0 && (
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="caption" color="text.secondary">
                            Equipment: {bed.equipment_attached.join(', ')}
                          </Typography>
                        </Box>
                      )}

                      {bed.estimated_availability && (
                        <Typography variant="caption" color="success.main">
                          Available: {bed.estimated_availability}
                        </Typography>
                      )}
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
                      <TableCell>Actions</TableCell>
                      <TableCell>Department Specific</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {automationRules.map((rule) => (
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
                            {rule.actions.slice(0, 2).join(', ')}
                            {rule.actions.length > 2 && ` +${rule.actions.length - 2} more`}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {rule.department_specific ? (
                            <Box>
                              <Chip label="Yes" color="warning" size="small" />
                              <Typography variant="caption" display="block">
                                {rule.departments.join(', ')}
                              </Typography>
                            </Box>
                          ) : (
                            <Chip label="Global" color="success" size="small" />
                          )}
                        </TableCell>
                        <TableCell>
                          <Switch
                            checked={rule.enabled}
                            onChange={() => toggleAutomationRule(rule.id)}
                            color="primary"
                          />
                        </TableCell>
                        <TableCell>
                          <Button size="small" variant="outlined" onClick={() => console.log("Edit clicked")}>Edit</Button>
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
