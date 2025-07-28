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
  TextField,
  Alert,
} from '@mui/material';
import { 
  Inventory,
  Warning,
  CheckCircle,
  ShoppingCart,
  TrendingDown,
} from '@mui/icons-material';
import axios from 'axios';

interface SupplyItem {
  id: string;
  sku: string;
  name: string;
  category: string;
  current_stock: number;
  available_stock: number;
  minimum_stock: number;
  maximum_stock: number;
  status: string;
  cost_per_unit: number;
  supplier_name: string;
  locations: number;
  total_value?: number;
  utilization_rate?: number;
  stock_level_percentage?: number;
}

const SupplyInventoryDashboard: React.FC = () => {
  const [supplies, setSupplies] = useState<SupplyItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSupply, setSelectedSupply] = useState<SupplyItem | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [reorderQuantity, setReorderQuantity] = useState(0);

  useEffect(() => {
    fetchSupplies();
  }, []);

  const fetchSupplies = async () => {
    try {
      const response = await axios.get('http://localhost:8000/supply_inventory/query');
      setSupplies(response.data.supply_items || response.data.items || []);
    } catch (error) {
      console.error('Error fetching supplies:', error);
    } finally {
      setLoading(false);
    }
  };

  const initiateReorder = async () => {
    if (!selectedSupply || reorderQuantity <= 0) return;

    try {
      await axios.post('http://localhost:8000/supply_inventory/execute', {
        action: 'create_purchase_order',
        parameters: {
          supply_item_id: selectedSupply.id,
          quantity: reorderQuantity,
          urgent: selectedSupply.status === 'out_of_stock'
        }
      });
      
      setDialogOpen(false);
      setReorderQuantity(0);
      fetchSupplies(); // Refresh the data
    } catch (error) {
      console.error('Error creating purchase order:', error);
    }
  };

  const getStatusColor = (status: string, quantity: number, reorderPoint: number) => {
    if (status === 'out_of_stock' || quantity === 0) return 'error';
    if (status === 'low_stock' || quantity <= reorderPoint) return 'warning';
    if (status === 'in_stock' && quantity > reorderPoint) return 'success';
    return 'default';
  };

  const getStatusIcon = (status: string, quantity: number, reorderPoint: number) => {
    if (status === 'out_of_stock' || quantity === 0) return <Warning sx={{ color: 'red' }} />;
    if (status === 'low_stock' || quantity <= reorderPoint) return <TrendingDown sx={{ color: 'orange' }} />;
    if (status === 'in_stock' && quantity > reorderPoint) return <CheckCircle sx={{ color: 'green' }} />;
    return <Inventory sx={{ color: 'gray' }} />;
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      'personal_protective_equipment': '#1976d2',
      'pharmaceuticals': '#d32f2f',
      'medical_supplies': '#388e3c',
      'surgical_instruments': '#f57c00',
      'laboratory_supplies': '#7b1fa2',
      'cleaning_supplies': '#00796b'
    };
    return colors[category.toLowerCase() as keyof typeof colors] || '#757575';
  };

  const supplyStatusCounts = supplies.reduce((acc, item) => {
    if (item.current_stock === 0) {
      acc['out_of_stock'] = (acc['out_of_stock'] || 0) + 1;
    } else if (item.current_stock <= item.minimum_stock) {
      acc['low_stock'] = (acc['low_stock'] || 0) + 1;
    } else {
      acc['in_stock'] = (acc['in_stock'] || 0) + 1;
    }
    return acc;
  }, {} as Record<string, number>);

  const supplyCategoryCounts = supplies.reduce((acc, item) => {
    acc[item.category] = (acc[item.category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const totalValue = supplies.reduce((sum, item) => 
    sum + ((item.current_stock || 0) * (item.cost_per_unit || 0)), 0
  );

  const lowStockItems = supplies.filter(item => 
    (item.current_stock || 0) <= (item.minimum_stock || 0) && (item.current_stock || 0) > 0
  );

  const outOfStockItems = supplies.filter(item => (item.current_stock || 0) === 0);

  if (loading) {
    return <LinearProgress />;
  }
  // Event Handlers
  const handleUpdate = () => {
    console.log('SupplyInventoryDashboard: Update action triggered');
  };

  const handleDelete = () => {
    console.log('SupplyInventoryDashboard: Delete action triggered');
  };

  const handleCreate = () => {
    console.log('SupplyInventoryDashboard: Create action triggered');
  };



  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Supply Inventory Dashboard
      </Typography>

      {/* Alert for Critical Items */}
      {(lowStockItems.length > 0 || outOfStockItems.length > 0) && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          {outOfStockItems.length > 0 && (
            <Typography variant="body2" component="span">
              <strong>{outOfStockItems.length}</strong> items are out of stock. 
            </Typography>
          )}
          {lowStockItems.length > 0 && (
            <Typography variant="body2" component="span">
              <strong>{lowStockItems.length}</strong> items are below reorder point.
            </Typography>
          )}
        </Alert>
      )}

      {/* Summary Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 3, mb: 3 }}>
        <Card>
          <CardContent>
            <Typography variant="h4" component="div" color="primary">
              {supplies.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Items
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h4" component="div" color="success.main">
              {supplyStatusCounts['in_stock'] || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              In Stock
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h4" component="div" color="warning.main">
              {supplyStatusCounts['low_stock'] || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Low Stock
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h4" component="div" color="error.main">
              {supplyStatusCounts['out_of_stock'] || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Out of Stock
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Inventory Value and Categories */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3, mb: 3 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Inventory Value
            </Typography>
            <Typography variant="h4" component="div" color="primary">
              ${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Inventory Value
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Categories
            </Typography>
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1 }}>
              {Object.entries(supplyCategoryCounts).slice(0, 6).map(([category, count]) => (
                <Box key={category} sx={{ display: 'flex', alignItems: 'center' }}>
                  <Inventory sx={{ color: getCategoryColor(category), mr: 1 }} />
                  <Box>
                    <Typography variant="body2" fontWeight="bold">
                      {count}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {category.replace(/_/g, ' ')}
                    </Typography>
                  </Box>
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Supply Items Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Supply Inventory
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>SKU</TableCell>
                  <TableCell>Item Name</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Current Stock</TableCell>
                  <TableCell>Reorder Point</TableCell>
                  <TableCell>Unit Cost</TableCell>
                  <TableCell>Total Value</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {supplies.map((item) => {
                  const stockLevel = item.current_stock || 0;
                  const needsReorder = stockLevel <= item.minimum_stock;
                  const totalItemValue = stockLevel * (item.cost_per_unit || 0);

                  return (
                    <TableRow 
                      key={item.id}
                      sx={{ 
                        backgroundColor: stockLevel === 0 ? '#ffebee' : 
                                       needsReorder ? '#fff3e0' : 'inherit'
                      }}
                    >
                      <TableCell>{item.sku}</TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="bold">
                          {item.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {item.supplier_name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={item.category.replace(/_/g, ' ')}
                          sx={{ bgcolor: getCategoryColor(item.category), color: 'white' }}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {getStatusIcon(item.status, stockLevel, item.minimum_stock)}
                          <Typography variant="body2" sx={{ ml: 1 }}>
                            {stockLevel} units
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>{item.minimum_stock} units</TableCell>
                      <TableCell>${(item.cost_per_unit || 0).toFixed(2)}</TableCell>
                      <TableCell>${(totalItemValue || 0).toFixed(2)}</TableCell>
                      <TableCell>
                        <Chip 
                          label={
                            stockLevel === 0 ? 'Out of Stock' :
                            stockLevel <= item.minimum_stock ? 'Low Stock' : 'In Stock'
                          }
                          color={getStatusColor(item.status, stockLevel, item.minimum_stock)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<ShoppingCart />}
                          onClick={() => {
                            setSelectedSupply(item);
                            setReorderQuantity((item.maximum_stock || 100) - stockLevel);
                            setDialogOpen(true);
                          }}
                          disabled={!needsReorder && stockLevel > 0}
                        >
                          Reorder
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

      {/* Reorder Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>Create Purchase Order</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, minWidth: 400 }}>
            <Typography variant="body2" gutterBottom>
              Item: {selectedSupply?.name}
            </Typography>
            <Typography variant="body2" gutterBottom>
              Current Stock: {selectedSupply?.current_stock || 0} units
            </Typography>
            <Typography variant="body2" gutterBottom>
              Reorder Point: {selectedSupply?.minimum_stock} units
            </Typography>
            <TextField
              fullWidth
              label="Quantity to Order"
              type="number"
              value={reorderQuantity}
              onChange={(e) => setReorderQuantity(Number(e.target.value))}
              sx={{ mt: 2 }}
              helperText={`Estimated cost: $${(reorderQuantity * (selectedSupply?.cost_per_unit || 0)).toFixed(2)}`}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={initiateReorder} 
            variant="contained"
            disabled={reorderQuantity <= 0}
          >
            Create Order
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SupplyInventoryDashboard;
