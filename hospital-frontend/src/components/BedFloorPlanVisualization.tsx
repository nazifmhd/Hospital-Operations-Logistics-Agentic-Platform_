import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Tooltip,
  Switch,
  FormControlLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  CheckCircle,
  Person,
  CleaningServices,
  Warning,
  Block,
  LocalHospital,
} from '@mui/icons-material';
import axios from 'axios';

interface Bed {
  id: string;
  number: string;
  room_number: string;
  department_id: string;
  department_name: string;
  bed_type: string;
  status: string;
  current_patient_id?: string;
  patient_name?: string;
  admission_date?: string;
  floor: string;
  last_cleaned?: string;
}

const BedFloorPlanVisualization: React.FC = () => {
  const [beds, setBeds] = useState<Bed[]>([]);
  const [selectedDepartment, setSelectedDepartment] = useState<string>('all');
  const [selectedFloor, setSelectedFloor] = useState<number>(1);
  const [showOccupiedOnly, setShowOccupiedOnly] = useState(false);
  const [selectedBed, setSelectedBed] = useState<Bed | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBeds();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchBeds, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchBeds = async () => {
    try {
      const response = await axios.post('http://localhost:8000/bed_management/query', {
        query: 'Show all beds with current status and location',
        parameters: {}
      });
      setBeds(response.data.beds || []);
    } catch (error) {
      console.error('Error fetching beds:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'available': return '#4caf50';
      case 'occupied': return '#2196f3';
      case 'maintenance': return '#ff9800';
      case 'cleaning': return '#9c27b0';
      case 'blocked': return '#f44336';
      default: return '#757575';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'available': return <CheckCircle sx={{ color: 'white', fontSize: 16 }} />;
      case 'occupied': return <Person sx={{ color: 'white', fontSize: 16 }} />;
      case 'maintenance': return <Warning sx={{ color: 'white', fontSize: 16 }} />;
      case 'cleaning': return <CleaningServices sx={{ color: 'white', fontSize: 16 }} />;
      case 'blocked': return <Block sx={{ color: 'white', fontSize: 16 }} />;
      default: return <LocalHospital sx={{ color: 'white', fontSize: 16 }} />;
    }
  };

  const getFilteredBeds = () => {
    let filtered = beds.filter(bed => bed.floor === selectedFloor.toString());
    
    if (selectedDepartment !== 'all') {
      filtered = filtered.filter(bed => bed.department_id === selectedDepartment);
    }
    
    if (showOccupiedOnly) {
      filtered = filtered.filter(bed => bed.status.toLowerCase() === 'occupied');
    }
    
    return filtered;
  };

  const getDepartments = () => {
    const departments = Array.from(new Set(beds.map(bed => ({ 
      id: bed.department_id, 
      name: bed.department_name 
    })).map(dept => JSON.stringify(dept))))
    .map(dept => JSON.parse(dept));
    return departments;
  };

  const getFloors = () => {
    const floors = Array.from(new Set(beds.map(bed => bed.floor))).sort();
    return floors;
  };

  const groupBedsByWing = (beds: Bed[]) => {
    const grouped: { [key: string]: Bed[] } = {};
    beds.forEach(bed => {
      const wing = 'Main Wing'; // Simplified since backend doesn't provide wing data
      if (!grouped[wing]) {
        grouped[wing] = [];
      }
      grouped[wing].push(bed);
    });
    return grouped;
  };

  const BedCard: React.FC<{ bed: Bed }> = ({ bed }) => (
    <Tooltip
      title={
        <Box>
          <Typography variant="body2"><strong>Bed:</strong> {bed.number}</Typography>
          <Typography variant="body2"><strong>Room:</strong> {bed.room_number}</Typography>
          <Typography variant="body2"><strong>Type:</strong> {bed.bed_type}</Typography>
          <Typography variant="body2"><strong>Status:</strong> {bed.status}</Typography>
          <Typography variant="body2"><strong>Department:</strong> {bed.department_name}</Typography>
          {bed.patient_name && (
            <>
              <Typography variant="body2"><strong>Patient:</strong> {bed.patient_name}</Typography>
              <Typography variant="body2"><strong>Admitted:</strong> {bed.admission_date}</Typography>
            </>
          )}
        </Box>
      }
      arrow
    >
      <Box
        sx={{
          width: 60,
          height: 40,
          backgroundColor: getStatusColor(bed.status),
          borderRadius: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          border: '2px solid #fff',
          boxShadow: 1,
          transition: 'transform 0.2s, box-shadow 0.2s',
          '&:hover': {
            transform: 'scale(1.1)',
            boxShadow: 3,
          },
          m: 0.5,
        }}
        onClick={() => {
          setSelectedBed(bed);
          setDialogOpen(true);
        }}
      >
        {getStatusIcon(bed.status)}
        <Typography variant="caption" sx={{ color: 'white', fontSize: 8, fontWeight: 'bold' }}>
          {bed.number}
        </Typography>
      </Box>
    </Tooltip>
  );

  const StatusLegend = () => (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Bed Status Legend
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
          {[
            { status: 'available', label: 'Available', count: beds.filter(bed => bed.status.toLowerCase() === 'available').length },
            { status: 'occupied', label: 'Occupied', count: beds.filter(bed => bed.status.toLowerCase() === 'occupied').length },
            { status: 'maintenance', label: 'Maintenance', count: beds.filter(bed => bed.status.toLowerCase() === 'maintenance').length },
            { status: 'cleaning', label: 'Cleaning', count: beds.filter(bed => bed.status.toLowerCase() === 'cleaning').length },
            { status: 'blocked', label: 'Blocked', count: beds.filter(bed => bed.status.toLowerCase() === 'blocked').length },
          ].map((item) => (
            <Box key={item.status} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box
                sx={{
                  width: 20,
                  height: 20,
                  backgroundColor: getStatusColor(item.status),
                  borderRadius: 0.5,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {getStatusIcon(item.status)}
              </Box>
              <Typography variant="body2">
                {item.label} ({item.count})
              </Typography>
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );

  const filteredBeds = getFilteredBeds();
  const groupedBeds = groupBedsByWing(filteredBeds);
  const departments = getDepartments();
  const floors = getFloors();

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          🏥 Bed Floor Plan Visualization
        </Typography>
        <Typography>Loading bed data...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        🏥 Hospital Bed Floor Plan - Floor {selectedFloor}
      </Typography>

      {/* Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 3, alignItems: 'center', flexWrap: 'wrap' }}>
            <FormControl sx={{ minWidth: 120 }}>
              <InputLabel>Floor</InputLabel>
              <Select
                value={selectedFloor}
                onChange={(e) => setSelectedFloor(Number(e.target.value))}
                label="Floor"
              >
                {floors.map((floor) => (
                  <MenuItem key={floor} value={floor}>
                    Floor {floor}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Department</InputLabel>
              <Select
                value={selectedDepartment}
                onChange={(e) => setSelectedDepartment(e.target.value)}
                label="Department"
              >
                <MenuItem value="all">All Departments</MenuItem>
                {departments.map((dept) => (
                  <MenuItem key={dept.id} value={dept.id}>
                    {dept.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControlLabel
              control={
                <Switch
                  checked={showOccupiedOnly}
                  onChange={(e) => setShowOccupiedOnly(e.target.checked)}
                />
              }
              label="Show Occupied Only"
            />
            <Typography variant="body2" color="text.secondary">
              Total Beds: {filteredBeds.length} | 
              Last Updated: {new Date().toLocaleTimeString()}
            </Typography>
          </Box>
        </CardContent>
      </Card>

      <StatusLegend />

      {/* Statistics Cards */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 3 }}>
        {departments.slice(0, 3).map((dept) => {
          const deptBeds = beds.filter(bed => bed.department_id === dept.id);
          const occupiedBeds = deptBeds.filter(bed => bed.status.toLowerCase() === 'occupied');
          const occupancyRate = deptBeds.length > 0 ? (occupiedBeds.length / deptBeds.length) * 100 : 0;
          
          return (
            <Card key={dept.id} sx={{ minWidth: 250, flex: '1 1 250px' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ fontSize: '1rem' }}>
                  {dept.name}
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Chip label={`Total: ${deptBeds.length}`} size="small" />
                  <Chip label={`Occupied: ${occupiedBeds.length}`} size="small" color="primary" />
                </Box>
                <Typography variant="caption" color="text.secondary">
                  Occupancy Rate: {occupancyRate.toFixed(1)}%
                </Typography>
              </CardContent>
            </Card>
          );
        })}
        
        <Card sx={{ minWidth: 250, flex: '1 1 250px' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ fontSize: '1rem' }}>
              Quick Stats
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Chip 
                label={`Available: ${beds.filter(b => b.status.toLowerCase() === 'available').length}`} 
                size="small" 
                color="success" 
              />
              <Chip 
                label={`Cleaning: ${beds.filter(b => b.status.toLowerCase() === 'cleaning').length}`} 
                size="small" 
                color="warning" 
              />
            </Box>
            <Typography variant="caption" color="text.secondary">
              Floor {selectedFloor} Capacity
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Floor Plan */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Floor {selectedFloor} Layout
          </Typography>
          <Box sx={{ minHeight: 600, p: 2, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
            {Object.entries(groupedBeds).map(([wing, wingBeds]) => (
              <Box key={wing} sx={{ mb: 4 }}>
                <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold', color: 'primary.main' }}>
                  {wing} ({wingBeds.length} beds)
                </Typography>
                
                {/* Group beds by department within wing */}
                {departments.filter(dept => wingBeds.some(bed => bed.department_id === dept.id)).map(dept => {
                  const deptBeds = wingBeds.filter(bed => bed.department_id === dept.id);
                  return (
                    <Box key={dept.id} sx={{ mb: 3 }}>
                      <Typography variant="subtitle2" sx={{ mb: 1, color: 'text.secondary' }}>
                        {dept.name}
                      </Typography>
                      <Box sx={{ 
                        display: 'flex', 
                        flexWrap: 'wrap', 
                        gap: 1,
                        p: 2,
                        border: '1px dashed #ccc',
                        borderRadius: 1,
                        backgroundColor: 'white'
                      }}>
                        {deptBeds.map((bed) => (
                          <BedCard key={bed.id} bed={bed} />
                        ))}
                      </Box>
                    </Box>
                  );
                })}
              </Box>
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Bed Details Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Bed Details - {selectedBed?.number}
        </DialogTitle>
        <DialogContent>
          {selectedBed && (
            <Box sx={{ pt: 1 }}>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                <Box sx={{ flex: '1 1 300px' }}>
                  <Typography variant="body2" color="text.secondary">Bed Number</Typography>
                  <Typography variant="body1" sx={{ mb: 2 }}>{selectedBed.number}</Typography>
                </Box>
                <Box sx={{ flex: '1 1 300px' }}>
                  <Typography variant="body2" color="text.secondary">Room Number</Typography>
                  <Typography variant="body1" sx={{ mb: 2 }}>{selectedBed.room_number}</Typography>
                </Box>
                <Box sx={{ flex: '1 1 300px' }}>
                  <Typography variant="body2" color="text.secondary">Type</Typography>
                  <Typography variant="body1" sx={{ mb: 2 }}>{selectedBed.bed_type}</Typography>
                </Box>
                <Box sx={{ flex: '1 1 300px' }}>
                  <Typography variant="body2" color="text.secondary">Status</Typography>
                  <Box sx={{ mb: 2 }}>
                    <Chip
                      label={selectedBed.status}
                      sx={{ backgroundColor: getStatusColor(selectedBed.status), color: 'white' }}
                      size="small"
                    />
                  </Box>
                </Box>
                {selectedBed.patient_name && (
                  <Box sx={{ flex: '1 1 300px' }}>
                    <Typography variant="body2" color="text.secondary">Patient</Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>{selectedBed.patient_name}</Typography>
                  </Box>
                )}
                {selectedBed.admission_date && (
                  <Box sx={{ flex: '1 1 300px' }}>
                    <Typography variant="body2" color="text.secondary">Admission Date</Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                      {new Date(selectedBed.admission_date).toLocaleDateString()}
                    </Typography>
                  </Box>
                )}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
          <Button variant="contained" onClick={() => setDialogOpen(false)}>
            Update Status
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BedFloorPlanVisualization;
