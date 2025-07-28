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
  Stepper,
  Step,
  StepLabel,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ShoppingCart,
  CheckCircle,
  Warning,
  Schedule,
  Approval,
  LocalShipping,
  Receipt,
} from '@mui/icons-material';
import axios from 'axios';

interface AutoReorderItem {
  id: string;
  supply_name: string;
  current_quantity: number;
  reorder_point: number;
  suggested_quantity: number;
  estimated_cost: number;
  supplier: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'approved' | 'ordered' | 'delivered' | 'rejected';
  created_at: string;
  expected_delivery: string;
}

interface PurchaseOrder {
  id: string;
  order_number: string;
  supplier: string;
  total_items: number;
  total_cost: number;
  status: 'draft' | 'pending_approval' | 'approved' | 'sent' | 'delivered';
  created_at: string;
  approved_by?: string;
  items: AutoReorderItem[];
}

const AutomatedSupplyReorderingWorkflow: React.FC = () => {
  const [reorderItems, setReorderItems] = useState<AutoReorderItem[]>([]);
  const [purchaseOrders, setPurchaseOrders] = useState<PurchaseOrder[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<PurchaseOrder | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [autoReorderEnabled, setAutoReorderEnabled] = useState(true);
  
  // Supplier selection state
  const [suppliers, setSuppliers] = useState<Array<{id: string, name: string, contact_person: string}>>([]);
  const [supplierDialogOpen, setSupplierDialogOpen] = useState(false);
  const [selectedReorderItem, setSelectedReorderItem] = useState<AutoReorderItem | null>(null);
  const [selectedSupplierId, setSelectedSupplierId] = useState<string>('');

  useEffect(() => {
    fetchReorderData();
    fetchPurchaseOrders();
    fetchSuppliers();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchReorderData();
      fetchPurchaseOrders();
    }, 30000);
  // Event Handlers
  const handleUpdate = () => {
    console.log('AutomatedSupplyReorderingWorkflow: Update action triggered');
  };

  const handleDelete = () => {
    console.log('AutomatedSupplyReorderingWorkflow: Delete action triggered');
  };

  const handleCreate = () => {
    console.log('AutomatedSupplyReorderingWorkflow: Create action triggered');
  };


    
    return () => clearInterval(interval);
  }, []);

  const fetchReorderData = async () => {
    try {
      const response = await axios.get('http://localhost:8000/supply_inventory/auto_reorder_status');
      setReorderItems(response.data.auto_reorders || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching reorder data:', error);
      setLoading(false);
    }
  };

  const fetchPurchaseOrders = async () => {
    try {
      const response = await axios.get('http://localhost:8000/supply_inventory/purchase_orders');
      setPurchaseOrders(response.data.purchase_orders || []);
    } catch (error) {
      console.error('Error fetching purchase orders:', error);
    }
  };

  const fetchSuppliers = async () => {
    try {
      const response = await axios.get('http://localhost:8000/supply_inventory/suppliers');
      setSuppliers(response.data.suppliers || []);
    } catch (error) {
      console.error('Error fetching suppliers:', error);
    }
  };

  const triggerAutoReorder = async () => {
    try {
      await axios.post('http://localhost:8000/supply_inventory/trigger_auto_reorder');
      fetchReorderData();
      fetchPurchaseOrders();
    } catch (error) {
      console.error('Error triggering auto reorder:', error);
    }
  };

  const approvePurchaseOrder = async (orderId: string) => {
    try {
      await axios.post(`http://localhost:8000/supply_inventory/approve_purchase_order/${orderId}`);
      fetchPurchaseOrders();
    } catch (error) {
      console.error('Error approving purchase order:', error);
    }
  };

  const rejectPurchaseOrder = async (orderId: string) => {
    try {
      await axios.post(`http://localhost:8000/supply_inventory/reject_purchase_order/${orderId}`);
      fetchPurchaseOrders();
    } catch (error) {
      console.error('Error rejecting purchase order:', error);
    }
  };

  const approveReorderItem = async (itemId: string) => {
    // Find the item to approve
    const item = reorderItems.find(r => r.id === itemId);
    if (!item) {
      console.error('Reorder item not found');
      return;
    }
    
    // Set the selected item and open supplier selection dialog
    setSelectedReorderItem(item);
    setSelectedSupplierId('');
    setSupplierDialogOpen(true);
  };

  const confirmApproveWithSupplier = async () => {
    if (!selectedReorderItem || !selectedSupplierId) {
      console.error('Missing reorder item or supplier selection');
      return;
    }

    try {
      const response = await axios.post(
        `http://localhost:8000/supply_inventory/approve_reorder/${selectedReorderItem.id}`,
        { supplier_id: selectedSupplierId }
      );
      console.log('Reorder approved:', response.data);
      
      // Close dialog and refresh data
      setSupplierDialogOpen(false);
      setSelectedReorderItem(null);
      setSelectedSupplierId('');
      
      // Refresh both auto reorder status and purchase orders
      fetchReorderData();
      fetchPurchaseOrders();
    } catch (error) {
      console.error('Error approving reorder item:', error);
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
      case 'pending_approval': return 'warning';
      case 'ordered': return 'info';
      case 'delivered': return 'success';
      case 'rejected': return 'error';
      default: return 'default';
    }
  };

  const getWorkflowSteps = () => [
    'Detection',
    'Order Generation',
    'Approval',
    'Purchase',
    'Delivery'
  ];

  const getActiveStep = (status: string) => {
    switch (status) {
      case 'draft': return 0;
      case 'pending_approval': return 1;
      case 'approved': return 2;
      case 'sent': return 3;
      case 'delivered': return 4;
      default: return 0;
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Automated Supply Reordering Workflow
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Automated Supply Reordering Workflow
        </Typography>
        <Box>
          <Button
            variant="contained"
            color="primary"
            startIcon={<ShoppingCart />}
            onClick={() => triggerAutoReorder()}
          >
            Trigger Auto Reorder
          </Button>
          <Chip
            label={autoReorderEnabled ? 'Auto-Reorder: ON' : 'Auto-Reorder: OFF'}
            color={autoReorderEnabled ? 'success' : 'error'}
            icon={autoReorderEnabled ? <CheckCircle /> : <Warning />}
          />
        </Box>
      </Box>

      {/* Summary Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 3, mb: 3 }}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Warning sx={{ fontSize: 40, color: '#f57c00', mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {reorderItems.filter(item => item.priority === 'critical').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Critical Items
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Schedule sx={{ fontSize: 40, color: '#1976d2', mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {purchaseOrders.filter(order => order.status === 'pending_approval').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Pending Approval
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <LocalShipping sx={{ fontSize: 40, color: '#388e3c', mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  {purchaseOrders.filter(order => order.status === 'sent').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  In Transit
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Receipt sx={{ fontSize: 40, color: '#7b1fa2', mr: 2 }} />
              <Box>
                <Typography variant="h4" component="div">
                  ${purchaseOrders.reduce((sum, order) => sum + order.total_cost, 0).toFixed(2)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Pending Cost
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Auto-Reorder Items Needing Attention */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Items Requiring Reorder
          </Typography>
          {reorderItems.length === 0 ? (
            <Alert severity="success">
              All supply levels are adequate. No items require immediate reordering.
            </Alert>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Supply Item</TableCell>
                    <TableCell align="right">Current Stock</TableCell>
                    <TableCell align="right">Reorder Point</TableCell>
                    <TableCell align="right">Suggested Quantity</TableCell>
                    <TableCell align="right">Est. Cost</TableCell>
                    <TableCell>Priority</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {reorderItems.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" fontWeight="bold">
                            {item.supply_name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Supplier: {item.supplier}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="right">{item.current_quantity}</TableCell>
                      <TableCell align="right">{item.reorder_point}</TableCell>
                      <TableCell align="right">{item.suggested_quantity}</TableCell>
                      <TableCell align="right">${item.estimated_cost.toFixed(2)}</TableCell>
                      <TableCell>
                        <Chip
                          label={item.priority.toUpperCase()}
                          color={getPriorityColor(item.priority)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={item.status.replace('_', ' ').toUpperCase()}
                          color={getStatusColor(item.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {item.status === 'pending' && (
                          <Button
                            size="small"
                            variant="outlined"
                            color="primary"
                            onClick={() => approveReorderItem(item.id)}
                          >
                            Approve
                          </Button>
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

      {/* Purchase Orders */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Purchase Orders & Approval Workflow
          </Typography>
          {purchaseOrders.length === 0 ? (
            <Alert severity="info">
              No active purchase orders at this time.
            </Alert>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Order #</TableCell>
                    <TableCell>Supplier</TableCell>
                    <TableCell align="right">Items</TableCell>
                    <TableCell align="right">Total Cost</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Workflow Progress</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {purchaseOrders.map((order) => (
                    <TableRow key={order.id}>
                      <TableCell>
                        <Typography variant="body2" fontWeight="bold">
                          {order.order_number}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(order.created_at).toLocaleDateString()}
                        </Typography>
                      </TableCell>
                      <TableCell>{order.supplier}</TableCell>
                      <TableCell align="right">{order.total_items}</TableCell>
                      <TableCell align="right">${order.total_cost.toFixed(2)}</TableCell>
                      <TableCell>
                        <Chip
                          label={order.status.replace('_', ' ').toUpperCase()}
                          color={getStatusColor(order.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ width: 200 }}>
                          <Stepper activeStep={getActiveStep(order.status)} sx={{ fontSize: '0.75rem' }}>
                            {getWorkflowSteps().map((label, index) => (
                              <Step key={label}>
                                <StepLabel sx={{ fontSize: '0.75rem' }}>
                                  {index === getActiveStep(order.status) ? label : ''}
                                </StepLabel>
                              </Step>
                            ))}
                          </Stepper>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Tooltip title="View Details">
                            <IconButton
                              size="small"
                              onClick={() => {
                                setSelectedOrder(order);
                                setDialogOpen(true);
                              }}
                            >
                              <Receipt />
                            </IconButton>
                          </Tooltip>
                          {order.status === 'pending_approval' && (
                            <>
                              <Tooltip title="Approve">
                                <IconButton
                                  size="small"
                                  color="success"
                                  onClick={() => approvePurchaseOrder(order.id)}
                                >
                                  <CheckCircle />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Reject">
                                <IconButton
                                  size="small"
                                  color="error"
                                  onClick={() => rejectPurchaseOrder(order.id)}
                                >
                                  <Warning />
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

      {/* Purchase Order Details Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Purchase Order Details: {selectedOrder?.order_number}
        </DialogTitle>
        <DialogContent>
          {selectedOrder && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Order Information
              </Typography>
              <Box sx={{ mb: 3 }}>
                <Typography><strong>Supplier:</strong> {selectedOrder.supplier}</Typography>
                <Typography><strong>Total Items:</strong> {selectedOrder.total_items}</Typography>
                <Typography><strong>Total Cost:</strong> ${selectedOrder.total_cost.toFixed(2)}</Typography>
                <Typography><strong>Status:</strong> {selectedOrder.status}</Typography>
                {selectedOrder.approved_by && (
                  <Typography><strong>Approved By:</strong> {selectedOrder.approved_by}</Typography>
                )}
              </Box>

              <Typography variant="h6" gutterBottom>
                Items in Order
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Item Name</TableCell>
                      <TableCell align="right">Quantity</TableCell>
                      <TableCell align="right">Unit Cost</TableCell>
                      <TableCell>Priority</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {selectedOrder.items.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>{item.supply_name}</TableCell>
                        <TableCell align="right">{item.suggested_quantity}</TableCell>
                        <TableCell align="right">${item.estimated_cost.toFixed(2)}</TableCell>
                        <TableCell>
                          <Chip
                            label={item.priority.toUpperCase()}
                            color={getPriorityColor(item.priority)}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
          {selectedOrder?.status === 'pending_approval' && (
            <>
              <Button
                color="error"
                onClick={() => {
                  rejectPurchaseOrder(selectedOrder.id);
                  setDialogOpen(false);
                }}
              >
                Reject
              </Button>
              <Button
                color="success"
                variant="contained"
                onClick={() => {
                  approvePurchaseOrder(selectedOrder.id);
                  setDialogOpen(false);
                }}
              >
                Approve
              </Button>
            </>
          )}
        </DialogActions>
      </Dialog>

      {/* Supplier Selection Dialog */}
      <Dialog 
        open={supplierDialogOpen} 
        onClose={() => setSupplierDialogOpen(false)} 
        maxWidth="sm" 
        fullWidth
      >
        <DialogTitle>
          Select Supplier for {selectedReorderItem?.supply_name}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Choose a supplier to process this reorder:
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {suppliers.map((supplier) => (
              <Paper
                key={supplier.id}
                sx={{
                  p: 2,
                  cursor: 'pointer',
                  border: selectedSupplierId === supplier.id ? '2px solid #1976d2' : '1px solid #e0e0e0',
                  backgroundColor: selectedSupplierId === supplier.id ? '#f3f7ff' : 'white',
                  '&:hover': {
                    backgroundColor: '#f5f5f5'
                  }
                }}
                onClick={() => setSelectedSupplierId(supplier.id)}
              >
                <Typography variant="subtitle1" fontWeight="bold">
                  {supplier.name}
                </Typography>
                {supplier.contact_person && (
                  <Typography variant="body2" color="text.secondary">
                    Contact: {supplier.contact_person}
                  </Typography>
                )}
              </Paper>
            ))}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSupplierDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={confirmApproveWithSupplier}
            variant="contained"
            disabled={!selectedSupplierId}
          >
            Approve with Selected Supplier
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AutomatedSupplyReorderingWorkflow;
