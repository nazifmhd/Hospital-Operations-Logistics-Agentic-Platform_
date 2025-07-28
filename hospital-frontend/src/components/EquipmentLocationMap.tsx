import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Tooltip,
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
  MedicalServices,
  Build,
  CheckCircle,
  Warning,
  Error,
  Schedule,
  LocationOn,
} from '@mui/icons-material';
import axios from 'axios';

interface Equipment {
  id: string;
  asset_tag: string;
  name: string;
  equipment_type: string;
  manufacturer: string;
  model: string;
  status: string;
  department_id: string;
  department_name: string;
  location_type: string;
  current_location_id: string;
  location_name: string;
  last_maintenance: string;
  next_maintenance: string;
}

const EquipmentLocationMap: React.FC = () => {
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedEquipment, setSelectedEquipment] = useState<Equipment | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEquipment();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchEquipment, 30000);
  // Event Handlers
  const handleUpdate = () => {
    console.log('EquipmentLocationMap: Update action triggered');
  };

  const handleDelete = () => {
    console.log('EquipmentLocationMap: Delete action triggered');
  };

  const handleCreate = () => {
    console.log('EquipmentLocationMap: Create action triggered');
  };


    return () => clearInterval(interval);
  }, []);

  const fetchEquipment = async () => {
    try {
      const response = await axios.post('http://localhost:8000/equipment_tracker/query', {
        query: 'Show all equipment with current status and location',
        parameters: {}
      });
      setEquipment(response.data.equipment || []);
    } catch (error) {
      console.error('Error fetching equipment:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'available': return '#4caf50';
      case 'in_use': return '#2196f3';
      case 'maintenance': return '#ff9800';
      case 'broken': return '#f44336';
      case 'cleaning': return '#9c27b0';
      default: return '#757575';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'available': return <CheckCircle sx={{ color: 'white', fontSize: 16 }} />;
      case 'in_use': return <MedicalServices sx={{ color: 'white', fontSize: 16 }} />;
      case 'maintenance': return <Build sx={{ color: 'white', fontSize: 16 }} />;
      case 'broken': return <Error sx={{ color: 'white', fontSize: 16 }} />;
      case 'cleaning': return <Warning sx={{ color: 'white', fontSize: 16 }} />;
      default: return <Schedule sx={{ color: 'white', fontSize: 16 }} />;
    }
  };

  const getFilteredEquipment = () => {
    if (selectedType === 'all') {
      return equipment;
    }
    return equipment.filter(eq => eq.equipment_type === selectedType);
  };

  const getEquipmentTypes = () => {
    const types = Array.from(new Set(equipment.map(eq => eq.equipment_type)));
    return types.sort();
  };

  const groupEquipmentByLocation = (equipment: Equipment[]) => {
    const grouped: { [key: string]: Equipment[] } = {};
    equipment.forEach(eq => {
      const locationKey = eq.location_name || 'Unknown Location';
      if (!grouped[locationKey]) {
        grouped[locationKey] = [];
      }
      grouped[locationKey].push(eq);
    });
    return grouped;
  };

  const EquipmentCard: React.FC<{ equipment: Equipment }> = ({ equipment }) => (
    <Tooltip
      title={
        <Box>
          <Typography variant="body2"><strong>Asset:</strong> {equipment.asset_tag}</Typography>
          <Typography variant="body2"><strong>Name:</strong> {equipment.name}</Typography>
          <Typography variant="body2"><strong>Type:</strong> {equipment.equipment_type}</Typography>
          <Typography variant="body2"><strong>Status:</strong> {equipment.status}</Typography>
          <Typography variant="body2"><strong>Location:</strong> {equipment.location_name}</Typography>
          <Typography variant="body2"><strong>Department:</strong> {equipment.department_name}</Typography>
        </Box>
      }
      arrow
    >
      <Box
        sx={{
          width: 80,
          height: 60,
          backgroundColor: getStatusColor(equipment.status),
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
            transform: 'scale(1.05)',
            boxShadow: 3,
          },
          m: 0.5,
        }}
        onClick={() => {
          setSelectedEquipment(equipment);
          setDialogOpen(true);
        }}
      >
        {getStatusIcon(equipment.status)}
        <Typography variant="caption" sx={{ color: 'white', fontSize: 9, fontWeight: 'bold', textAlign: 'center' }}>
          {equipment.asset_tag}
        </Typography>
      </Box>
    </Tooltip>
  );

  const StatusLegend = () => (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Equipment Status Legend
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
          {[
            { status: 'available', label: 'Available', count: equipment.filter(eq => eq.status.toLowerCase() === 'available').length },
            { status: 'in_use', label: 'In Use', count: equipment.filter(eq => eq.status.toLowerCase() === 'in_use').length },
            { status: 'maintenance', label: 'Maintenance', count: equipment.filter(eq => eq.status.toLowerCase() === 'maintenance').length },
            { status: 'broken', label: 'Broken', count: equipment.filter(eq => eq.status.toLowerCase() === 'broken').length },
            { status: 'cleaning', label: 'Cleaning', count: equipment.filter(eq => eq.status.toLowerCase() === 'cleaning').length },
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

  const filteredEquipment = getFilteredEquipment();
  const groupedEquipment = groupEquipmentByLocation(filteredEquipment);
  const equipmentTypes = getEquipmentTypes();

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          🗺️ Equipment Location Map
        </Typography>
        <Typography>Loading equipment data...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        🗺️ Equipment Location & Status Map
      </Typography>

      {/* Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 3, alignItems: 'center', flexWrap: 'wrap' }}>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Equipment Type</InputLabel>
              <Select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                label="Equipment Type"
              >
                <MenuItem value="all">All Equipment Types</MenuItem>
                {equipmentTypes.map((type) => (
                  <MenuItem key={type} value={type}>
                    {type}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Typography variant="body2" color="text.secondary">
              Total Equipment: {filteredEquipment.length} | 
              Last Updated: {new Date().toLocaleTimeString()}
            </Typography>
          </Box>
        </CardContent>
      </Card>

      <StatusLegend />

      {/* Equipment Statistics */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 3 }}>
        {equipmentTypes.slice(0, 4).map((type) => {
          const typeEquipment = equipment.filter(eq => eq.equipment_type === type);
          const available = typeEquipment.filter(eq => eq.status.toLowerCase() === 'available').length;
          const inUse = typeEquipment.filter(eq => eq.status.toLowerCase() === 'in_use').length;
          
          return (
            <Card key={type} sx={{ minWidth: 250, flex: '1 1 250px' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ fontSize: '1rem' }}>
                  {type}
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Chip label={`Total: ${typeEquipment.length}`} size="small" />
                  <Chip 
                    label={`Available: ${available}`} 
                    size="small" 
                    color={available > 0 ? 'success' : 'error'} 
                  />
                </Box>
                <Typography variant="caption" color="text.secondary">
                  Utilization: {typeEquipment.length > 0 ? Math.round((inUse / typeEquipment.length) * 100) : 0}%
                </Typography>
              </CardContent>
            </Card>
          );
        })}
      </Box>

      {/* Location Map */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Equipment Location Map
          </Typography>
          <Box sx={{ minHeight: 400, p: 2, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
            {Object.entries(groupedEquipment).map(([location, locationEquipment]) => (
              <Box key={location} sx={{ mb: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <LocationOn sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                    {location} ({locationEquipment.length} items)
                  </Typography>
                </Box>
                <Box sx={{ 
                  display: 'flex', 
                  flexWrap: 'wrap', 
                  gap: 1,
                  maxWidth: '100%',
                  border: '1px dashed #ccc',
                  borderRadius: 1,
                  p: 2,
                  backgroundColor: 'white'
                }}>
                  {locationEquipment.map((eq) => (
                    <EquipmentCard key={eq.id} equipment={eq} />
                  ))}
                </Box>
              </Box>
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Equipment Details Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Equipment Details - {selectedEquipment?.asset_tag}
        </DialogTitle>
        <DialogContent>
          {selectedEquipment && (
            <Box sx={{ pt: 1 }}>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                <Box sx={{ flex: '1 1 300px' }}>
                  <Typography variant="body2" color="text.secondary">Asset Tag</Typography>
                  <Typography variant="body1" sx={{ mb: 2 }}>{selectedEquipment.asset_tag}</Typography>
                </Box>
                <Box sx={{ flex: '1 1 300px' }}>
                  <Typography variant="body2" color="text.secondary">Name</Typography>
                  <Typography variant="body1" sx={{ mb: 2 }}>{selectedEquipment.name}</Typography>
                </Box>
                <Box sx={{ flex: '1 1 300px' }}>
                  <Typography variant="body2" color="text.secondary">Type</Typography>
                  <Typography variant="body1" sx={{ mb: 2 }}>{selectedEquipment.equipment_type}</Typography>
                </Box>
                <Box sx={{ flex: '1 1 300px' }}>
                  <Typography variant="body2" color="text.secondary">Status</Typography>
                  <Box sx={{ mb: 2 }}>
                    <Chip
                      label={selectedEquipment.status}
                      sx={{ backgroundColor: getStatusColor(selectedEquipment.status), color: 'white' }}
                      size="small"
                    />
                  </Box>
                </Box>
                <Box sx={{ flex: '1 1 300px' }}>
                  <Typography variant="body2" color="text.secondary">Manufacturer</Typography>
                  <Typography variant="body1" sx={{ mb: 2 }}>{selectedEquipment.manufacturer}</Typography>
                </Box>
                <Box sx={{ flex: '1 1 300px' }}>
                  <Typography variant="body2" color="text.secondary">Model</Typography>
                  <Typography variant="body1" sx={{ mb: 2 }}>{selectedEquipment.model}</Typography>
                </Box>
                <Box sx={{ flex: '1 1 300px' }}>
                  <Typography variant="body2" color="text.secondary">Location</Typography>
                  <Typography variant="body1" sx={{ mb: 2 }}>{selectedEquipment.location_name}</Typography>
                </Box>
                <Box sx={{ flex: '1 1 300px' }}>
                  <Typography variant="body2" color="text.secondary">Department</Typography>
                  <Typography variant="body1" sx={{ mb: 2 }}>{selectedEquipment.department_name}</Typography>
                </Box>
                {selectedEquipment.last_maintenance && (
                  <Box sx={{ flex: '1 1 300px' }}>
                    <Typography variant="body2" color="text.secondary">Last Maintenance</Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                      {new Date(selectedEquipment.last_maintenance).toLocaleDateString()}
                    </Typography>
                  </Box>
                )}
                {selectedEquipment.next_maintenance && (
                  <Box sx={{ flex: '1 1 300px' }}>
                    <Typography variant="body2" color="text.secondary">Next Maintenance</Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                      {new Date(selectedEquipment.next_maintenance).toLocaleDateString()}
                    </Typography>
                  </Box>
                )}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
          <Button 
            variant="contained" 
            onClick={() => {
              setDialogOpen(false); 
              console.log("Status updated");
            }}
          >
            Update Status
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EquipmentLocationMap;
