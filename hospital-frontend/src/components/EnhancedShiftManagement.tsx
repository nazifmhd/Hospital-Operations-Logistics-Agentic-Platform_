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
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  Divider,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
  Badge,
  LinearProgress,
  Grid,
} from '@mui/material';
import {
  Schedule,
  AccessTime,
  CalendarToday,
  TrendingUp,
  People,
  SwapHoriz,
  Add,
  Edit,
  CheckCircle,
  Warning,
  Info,
  ExpandMore,
  Visibility,
  LocalHospital,
  Groups,
  Timeline,
  Assessment,
  ThumbUp,
  ThumbDown,
  Refresh,
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
  status: string;
  shift_start: string;
  shift_end: string;
  specialties: string[];
  workload_score: number;
}

interface ShiftAdjustment {
  id: string;
  adjustment_type: string;
  staff_member: StaffMember;
  current_shift: string;
  proposed_shift: string;
  reason: string;
  impact: string;
  department: string;
  status: string;
  impact_score: number;
  created_at: string;
}

interface ShiftTemplate {
  id: string;
  name: string;
  start_time: string;
  end_time: string;
  duration_hours: number;
  break_periods: Array<{ time: string; type: string }>;
  suitable_for: string[];
  patient_ratio: Record<string, string>;
  differential_pay?: number;
}

interface DepartmentSchedule {
  department_name: string;
  total_beds: number;
  occupied_beds: number;
  occupancy_rate: number;
  staff_by_role: Record<string, any>;
  coverage_gaps: string[];
  recommended_adjustments: Array<{
    type: string;
    role: string;
    suggestion: string;
    priority: string;
  }>;
}

interface ScheduleOverview {
  departments: Record<string, DepartmentSchedule>;
  summary: {
    total_staff: number;
    active_staff: number;
    overall_efficiency: number;
    departments_count: number;
  };
  shift_patterns: {
    standard: string;
    alternatives: string[];
  };
  recommendations: Array<{
    department: string;
    current_pattern: string;
    recommended_pattern: string;
    reason: string;
    expected_improvement: string;
  }>;
}

interface ScheduleChangeProposal {
  staff_id?: string;
  department_id?: string;
  proposed_shift: {
    start_time: string;
    end_time: string;
    shift_type: string;
    weekly_hours: number;
    effective_date?: string;
  };
  reason: string;
}

const EnhancedShiftManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  
  // Data states
  const [scheduleOverview, setScheduleOverview] = useState<ScheduleOverview | null>(null);
  const [shiftAdjustments, setShiftAdjustments] = useState<ShiftAdjustment[]>([]);
  const [shiftTemplates, setShiftTemplates] = useState<any>(null);
  const [staffData, setStaffData] = useState<StaffMember[]>([]);
  
  // Dialog states
  const [proposeDialogOpen, setProposeDialogOpen] = useState(false);
  const [templateDialogOpen, setTemplateDialogOpen] = useState(false);
  const [selectedDepartment, setSelectedDepartment] = useState('');
  const [selectedStaff, setSelectedStaff] = useState('');
  const [proposalReason, setProposalReason] = useState('');
  const [proposedShift, setProposedShift] = useState({
    start_time: '08:00',
    end_time: '20:00',
    shift_type: 'day_shift',
    weekly_hours: 60
  });

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchScheduleOverview(),
        fetchShiftAdjustments(),
        fetchShiftTemplates(),
        fetchStaffData()
      ]);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchScheduleOverview = async () => {
    try {
      const response = await axios.get('http://localhost:8000/staff_allocation/schedule_overview');
      setScheduleOverview(response.data);
    } catch (error) {
      console.error('Error fetching schedule overview:', error);
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

  const fetchShiftTemplates = async () => {
    try {
      const response = await axios.get('http://localhost:8000/staff_allocation/shift_templates');
      setShiftTemplates(response.data);
    } catch (error) {
      console.error('Error fetching shift templates:', error);
    }
  };

  const fetchStaffData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/staff_allocation/real_time_status');
      setStaffData(response.data.staff || []);
    } catch (error) {
      console.error('Error fetching staff data:', error);
    }
  };

  const proposeScheduleChange = async () => {
    try {
      const proposal: ScheduleChangeProposal = {
        proposed_shift: proposedShift,
        reason: proposalReason
      };

      if (selectedStaff) {
        proposal.staff_id = selectedStaff;
      } else if (selectedDepartment) {
        proposal.department_id = selectedDepartment;
      }

      const response = await axios.post('http://localhost:8000/staff_allocation/propose_schedule_change', proposal);
      console.log('Schedule change proposed:', response.data);
      setProposeDialogOpen(false);
      fetchShiftAdjustments(); // Refresh to show new proposal
    } catch (error) {
      console.error('Error proposing schedule change:', error);
    }
  };

  const approveShiftAdjustment = async (adjustmentId: string) => {
    try {
      await axios.post(`http://localhost:8000/staff_allocation/approve_shift_adjustment/${adjustmentId}`);
      fetchShiftAdjustments();
    } catch (error) {
      console.error('Error approving shift adjustment:', error);
    }
  };

  const getStatusColor = (status: string): "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning" => {
    switch (status) {
      case 'approved': return 'success';
      case 'pending': return 'warning';
      case 'rejected': return 'error';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority: string): "error" | "info" | "success" | "warning" => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'info';
    }
  };

  const renderScheduleOverview = () => (
    <Box>
      {/* Summary Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(4, 1fr)' }, gap: 2, mb: 3 }}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Total Staff
            </Typography>
            <Typography variant="h4">
              {scheduleOverview?.summary.total_staff || 0}
            </Typography>
            <Typography variant="body2" color="success.main">
              <People /> All Departments
            </Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Active Staff
            </Typography>
            <Typography variant="h4">
              {scheduleOverview?.summary.active_staff || 0}
            </Typography>
            <Typography variant="body2" color="primary.main">
              <Groups /> Currently On Duty
            </Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Overall Efficiency
            </Typography>
            <Typography variant="h4">
              {scheduleOverview?.summary.overall_efficiency || 0}%
            </Typography>
            <LinearProgress 
              variant="determinate" 
              value={scheduleOverview?.summary.overall_efficiency || 0} 
              sx={{ mt: 1 }}
            />
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Departments
            </Typography>
            <Typography variant="h4">
              {scheduleOverview?.summary.departments_count || 0}
            </Typography>
            <Typography variant="body2" color="info.main">
              <LocalHospital /> Hospital Units
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Department Analysis */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Department Schedule Analysis
          </Typography>
          {scheduleOverview && Object.entries(scheduleOverview.departments).map(([deptName, dept]) => (
            <Accordion key={deptName}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                  <Typography variant="subtitle1" sx={{ flex: 1 }}>
                    {dept.department_name}
                  </Typography>
                  <Chip 
                    label={`${dept.occupancy_rate}% occupied`}
                    color={dept.occupancy_rate > 75 ? 'error' : dept.occupancy_rate > 50 ? 'warning' : 'success'}
                    size="small"
                  />
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Bed Utilization
                    </Typography>
                    <Typography variant="body2">
                      {dept.occupied_beds}/{dept.total_beds} beds occupied
                    </Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={dept.occupancy_rate} 
                      sx={{ mt: 1, mb: 2 }}
                      color={dept.occupancy_rate > 75 ? 'error' : dept.occupancy_rate > 50 ? 'warning' : 'success'}
                    />
                  </Box>
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Staff by Role
                    </Typography>
                    {Object.entries(dept.staff_by_role).map(([role, data]: [string, any]) => (
                      <Typography key={role} variant="body2">
                        {role}: {data.active_count}/{data.total_count} active
                      </Typography>
                    ))}
                  </Box>
                  {dept.coverage_gaps.length > 0 && (
                    <Box sx={{ gridColumn: '1 / -1' }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Coverage Gaps
                      </Typography>
                      {dept.coverage_gaps.map((gap, index) => (
                        <Alert key={index} severity="warning" sx={{ mb: 1 }}>
                          {gap}
                        </Alert>
                      ))}
                    </Box>
                  )}
                  {dept.recommended_adjustments.length > 0 && (
                    <Box sx={{ gridColumn: '1 / -1' }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Recommended Adjustments
                      </Typography>
                      {dept.recommended_adjustments.map((adj, index) => (
                        <Alert key={index} severity={getPriorityColor(adj.priority)} sx={{ mb: 1 }}>
                          <strong>{adj.type}:</strong> {adj.suggestion}
                        </Alert>
                      ))}
                    </Box>
                  )}
                </Box>
              </AccordionDetails>
            </Accordion>
          ))}
        </CardContent>
      </Card>

      {/* Schedule Recommendations */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Schedule Pattern Recommendations
          </Typography>
          {scheduleOverview?.recommendations.map((rec, index) => (
            <Accordion key={index}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="subtitle1">{rec.department}</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box>
                  <Typography variant="body2" gutterBottom>
                    <strong>Current:</strong> {rec.current_pattern}
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    <strong>Recommended:</strong> {rec.recommended_pattern}
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    <strong>Reason:</strong> {rec.reason}
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    <strong>Expected Improvement:</strong> {rec.expected_improvement}
                  </Typography>
                </Box>
              </AccordionDetails>
            </Accordion>
          ))}
        </CardContent>
      </Card>
    </Box>
  );

  const renderShiftAdjustments = () => (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">
          Current Shift Adjustment Requests
          <Badge badgeContent={shiftAdjustments.filter(a => a.status === 'pending').length} color="warning" sx={{ ml: 2 }}>
            <Schedule />
          </Badge>
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setProposeDialogOpen(true)}
        >
          Propose Schedule Change
        </Button>
      </Box>

      {shiftAdjustments.length === 0 ? (
        <Alert severity="info" sx={{ mb: 3 }}>
          No shift adjustment requests at this time. The current staffing levels appear optimal.
          <br />
          <Typography variant="body2" sx={{ mt: 1 }}>
            You can create manual schedule proposals using the "Propose Schedule Change" button above.
          </Typography>
        </Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Staff Member</TableCell>
                <TableCell>Type</TableCell>
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
                    <Box>
                      <Typography variant="body2" fontWeight="bold">
                        {adjustment.staff_member.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {adjustment.staff_member.role} - {adjustment.department}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={adjustment.adjustment_type.replace('_', ' ').toUpperCase()}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2">{adjustment.current_shift}</Typography>
                      <SwapHoriz sx={{ color: 'text.secondary', fontSize: 16 }} />
                      <Typography variant="body2" fontWeight="bold">
                        {adjustment.proposed_shift}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>{adjustment.reason}</TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2">{adjustment.impact}</Typography>
                      <Typography variant="caption" color="primary.main">
                        Impact Score: {adjustment.impact_score}/10
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={adjustment.status.toUpperCase()}
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
    </Box>
  );

  const renderShiftTemplates = () => (
    <Box>
      {/* Standard Shifts */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Standard Shift Templates
          </Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }, gap: 2 }}>
            {shiftTemplates?.standard_shifts?.map((template: ShiftTemplate) => (
              <Card variant="outlined" key={template.id}>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    {template.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {template.start_time} - {template.end_time}
                  </Typography>
                  <Typography variant="body2">
                    Duration: {template.duration_hours} hours
                  </Typography>
                  {template.differential_pay && (
                    <Chip 
                      label={`+${template.differential_pay}% pay`}
                      color="success"
                      size="small"
                      sx={{ mt: 1 }}
                    />
                  )}
                  <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                    Suitable for: {template.suitable_for.join(', ')}
                  </Typography>
                </CardContent>
              </Card>
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Specialized Shifts */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Specialized Shift Options
          </Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, gap: 2 }}>
            {shiftTemplates?.specialized_shifts?.map((template: any, index: number) => (
              <Card variant="outlined" key={index}>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    {template.name}
                  </Typography>
                  <Typography variant="body2">
                    {template.start_time} - {template.end_time}
                  </Typography>
                  <Typography variant="body2">
                    Type: {template.type}
                  </Typography>
                  {template.departments && (
                    <Typography variant="caption" display="block">
                      Departments: {template.departments.join(', ')}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Rotation Patterns */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Advanced Rotation Patterns
          </Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' }, gap: 2 }}>
            {shiftTemplates?.rotation_patterns?.map((pattern: any, index: number) => (
              <Card variant="outlined" key={index}>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    {pattern.name}
                  </Typography>
                  <Typography variant="body2">
                    Pattern: {pattern.pattern}
                  </Typography>
                  <Typography variant="body2">
                    Cycle: {pattern.cycle_length}
                  </Typography>
                  <Typography variant="body2">
                    Avg Hours: {pattern.average_hours}/week
                  </Typography>
                </CardContent>
              </Card>
            ))}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Enhanced Shift Management
        </Typography>
        <Box>
          <IconButton onClick={fetchAllData} disabled={loading}>
            {loading ? <CircularProgress size={24} /> : <Refresh />}
          </IconButton>
        </Box>
      </Box>

      <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
        <Tab 
          label="Schedule Overview" 
          icon={<Assessment />}
          iconPosition="start"
        />
        <Tab 
          label={
            <Badge badgeContent={shiftAdjustments.filter(a => a.status === 'pending').length} color="warning">
              Shift Adjustments
            </Badge>
          }
          icon={<Schedule />}
          iconPosition="start"
        />
        <Tab 
          label="Shift Templates" 
          icon={<CalendarToday />}
          iconPosition="start"
        />
      </Tabs>

      {activeTab === 0 && renderScheduleOverview()}
      {activeTab === 1 && renderShiftAdjustments()}
      {activeTab === 2 && renderShiftTemplates()}

      {/* Propose Schedule Change Dialog */}
      <Dialog open={proposeDialogOpen} onClose={() => setProposeDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Propose Schedule Change</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, gap: 2, mt: 1 }}>
            <FormControl fullWidth>
              <InputLabel>Staff Member</InputLabel>
              <Select
                value={selectedStaff}
                onChange={(e) => setSelectedStaff(e.target.value)}
              >
                {staffData.map((staff) => (
                  <MenuItem key={staff.id} value={staff.id}>
                    {staff.name} - {staff.role} ({staff.department_name})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Department (Alternative)</InputLabel>
              <Select
                value={selectedDepartment}
                onChange={(e) => setSelectedDepartment(e.target.value)}
                disabled={selectedStaff !== ''}
              >
                {scheduleOverview && Object.keys(scheduleOverview.departments).map((dept) => (
                  <MenuItem key={dept} value={dept}>
                    {dept}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Start Time"
              type="time"
              value={proposedShift.start_time}
              onChange={(e) => setProposedShift({...proposedShift, start_time: e.target.value})}
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              fullWidth
              label="End Time"
              type="time"
              value={proposedShift.end_time}
              onChange={(e) => setProposedShift({...proposedShift, end_time: e.target.value})}
              InputLabelProps={{ shrink: true }}
            />
            <Box sx={{ gridColumn: '1 / -1' }}>
              <TextField
                fullWidth
                label="Reason for Change"
                multiline
                rows={3}
                value={proposalReason}
                onChange={(e) => setProposalReason(e.target.value)}
                placeholder="Explain why this schedule change is needed..."
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProposeDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={proposeScheduleChange}>
            Submit Proposal
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EnhancedShiftManagement;
