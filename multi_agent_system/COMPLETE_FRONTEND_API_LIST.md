# Complete Frontend API Analysis

## All API Endpoints Found in Frontend Code

### System & Core
1. `GET /system/status` - App.tsx
2. `GET /api/v2/notifications` - NotificationContext.tsx

### Bed Management
3. `POST /bed_management/query` - BedFloorPlanVisualization.tsx, BedManagementDashboard.tsx, EnhancedBedManagementView.tsx
4. `POST /bed_management/execute` - BedManagementDashboard.tsx, EnhancedBedManagementView.tsx

### Equipment Tracker
5. `POST /equipment_tracker/query` - EquipmentLocationMap.tsx, EquipmentTrackerDashboard.tsx
6. `POST /equipment_tracker/execute` - EquipmentTrackerDashboard.tsx
7. `GET /equipment_tracker/available_equipment` - EquipmentRequestDispatchInterface.tsx
8. `GET /equipment_tracker/equipment_requests` - EquipmentRequestDispatchInterface.tsx
9. `GET /equipment_tracker/porter_status` - EquipmentRequestDispatchInterface.tsx
10. `POST /equipment_tracker/create_request` - EquipmentRequestDispatchInterface.tsx
11. `POST /equipment_tracker/assign_equipment/{requestId}` - EquipmentRequestDispatchInterface.tsx
12. `POST /equipment_tracker/dispatch_request/{requestId}` - EquipmentRequestDispatchInterface.tsx
13. `POST /equipment_tracker/complete_request/{requestId}` - EquipmentRequestDispatchInterface.tsx

### Staff Allocation
14. `POST /staff_allocation/query` - StaffAllocationDashboard.tsx
15. `POST /staff_allocation/execute` - StaffAllocationDashboard.tsx
16. `GET /staff_allocation/real_time_status` - DynamicStaffReallocationSystem.tsx
17. `GET /staff_allocation/reallocation_suggestions` - DynamicStaffReallocationSystem.tsx
18. `GET /staff_allocation/shift_adjustments` - DynamicStaffReallocationSystem.tsx
19. `POST /staff_allocation/emergency_reallocation` - DynamicStaffReallocationSystem.tsx
20. `POST /staff_allocation/approve_reallocation/{suggestionId}` - DynamicStaffReallocationSystem.tsx
21. `POST /staff_allocation/reject_reallocation/{suggestionId}` - DynamicStaffReallocationSystem.tsx
22. `POST /staff_allocation/approve_shift_adjustment/{adjustmentId}` - DynamicStaffReallocationSystem.tsx

### Supply Inventory
23. `POST /supply_inventory/query` - SupplyInventoryDashboard.tsx
24. `POST /supply_inventory/execute` - SupplyInventoryDashboard.tsx
25. `GET /supply_inventory/auto_reorder_status` - AutomatedSupplyReorderingWorkflow.tsx
26. `GET /supply_inventory/purchase_orders` - AutomatedSupplyReorderingWorkflow.tsx
27. `POST /supply_inventory/trigger_auto_reorder` - AutomatedSupplyReorderingWorkflow.tsx
28. `POST /supply_inventory/approve_purchase_order/{orderId}` - AutomatedSupplyReorderingWorkflow.tsx
29. `POST /supply_inventory/reject_purchase_order/{orderId}` - AutomatedSupplyReorderingWorkflow.tsx

### Admission/Discharge
30. `GET /admission_discharge/patients` - EnhancedAdmissionDischargeAutomation.tsx
31. `GET /admission_discharge/tasks` - EnhancedAdmissionDischargeAutomation.tsx
32. `GET /admission_discharge/beds` - EnhancedAdmissionDischargeAutomation.tsx
33. `GET /admission_discharge/automation_rules` - EnhancedAdmissionDischargeAutomation.tsx
34. `POST /admission_discharge/start_admission` - EnhancedAdmissionDischargeAutomation.tsx
35. `POST /admission_discharge/start_discharge/{patientId}` - EnhancedAdmissionDischargeAutomation.tsx
36. `POST /admission_discharge/complete_task/{taskId}` - EnhancedAdmissionDischargeAutomation.tsx
37. `POST /admission_discharge/assign_bed/{patientId}` - EnhancedAdmissionDischargeAutomation.tsx
38. `POST /admission_discharge/toggle_automation/{ruleId}` - EnhancedAdmissionDischargeAutomation.tsx

### Analytics
39. `POST /analytics/capacity_utilization` - ComprehensiveReportingDashboard.tsx

## TOTAL: 39 API Endpoints

## Missing from Test File:
- POST /equipment_tracker/execute
- GET /equipment_tracker/porter_status  
- POST /equipment_tracker/create_request
- POST /equipment_tracker/assign_equipment/{requestId}
- POST /equipment_tracker/dispatch_request/{requestId}
- POST /equipment_tracker/complete_request/{requestId}
- POST /supply_inventory/execute
- GET /staff_allocation/shift_adjustments
- POST /staff_allocation/execute
- POST /staff_allocation/emergency_reallocation
- POST /staff_allocation/approve_reallocation/{suggestionId}
- POST /staff_allocation/reject_reallocation/{suggestionId}
- POST /staff_allocation/approve_shift_adjustment/{adjustmentId}
- POST /supply_inventory/trigger_auto_reorder
- POST /supply_inventory/approve_purchase_order/{orderId}
- POST /supply_inventory/reject_purchase_order/{orderId}
- POST /admission_discharge/start_admission
- POST /admission_discharge/start_discharge/{patientId}
- POST /admission_discharge/complete_task/{taskId}
- POST /admission_discharge/assign_bed/{patientId}
- POST /admission_discharge/toggle_automation/{ruleId}
