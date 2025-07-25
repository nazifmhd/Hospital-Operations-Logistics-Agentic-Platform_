import React, { useState } from 'react';
import {
  IconButton,
  Badge,
  Popover,
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Button,
  Divider,
  Alert as MuiAlert
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Warning,
  Error,
  Info,
  CheckCircle,
  Clear,
  MarkEmailRead
} from '@mui/icons-material';
import { useNotifications } from '../contexts/NotificationContext';

const NotificationCenter: React.FC = () => {
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
  const { alerts, unreadCount, isConnected, markAsRead, clearAll, dismissAlert } = useNotifications();

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'critical':
        return <Error color="error" />;
      case 'high':
        return <Warning color="warning" />;
      case 'medium':
        return <Info color="info" />;
      case 'low':
        return <CheckCircle color="success" />;
      default:
        return <Info color="info" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMins / 60);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <>
      <IconButton
        color="inherit"
        onClick={handleClick}
        size="large"
      >
        <Badge 
          badgeContent={unreadCount} 
          color="error"
          variant={unreadCount > 0 ? "standard" : "dot"}
          invisible={unreadCount === 0}
        >
          <NotificationsIcon />
        </Badge>
      </IconButton>

      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <Box sx={{ width: 400, maxHeight: 600 }}>
          {/* Header */}
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h6">
                Notifications
                {!isConnected && (
                  <Chip 
                    label="Offline" 
                    size="small" 
                    color="error" 
                    sx={{ ml: 1 }}
                  />
                )}
              </Typography>
              <Box>
                <IconButton size="small" onClick={clearAll} title="Mark all as read">
                  <MarkEmailRead />
                </IconButton>
              </Box>
            </Box>
            {unreadCount > 0 && (
              <Typography variant="body2" color="text.secondary">
                {unreadCount} unread notification{unreadCount > 1 ? 's' : ''}
              </Typography>
            )}
          </Box>

          {/* Connection Status */}
          {!isConnected && (
            <MuiAlert severity="warning" sx={{ m: 1 }}>
              Real-time updates disconnected. Notifications may be delayed.
            </MuiAlert>
          )}

          {/* Notifications List */}
          <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
            {alerts.length === 0 ? (
              <Box sx={{ p: 3, textAlign: 'center' }}>
                <Typography color="text.secondary">
                  No notifications
                </Typography>
              </Box>
            ) : (
              <List sx={{ p: 0 }}>
                {alerts.map((alert, index) => (
                  <React.Fragment key={alert.id}>
                    <ListItem
                      sx={{
                        backgroundColor: alert.read ? 'transparent' : 'action.hover',
                        '&:hover': { backgroundColor: 'action.selected' }
                      }}
                    >
                      <ListItemIcon>
                        {getPriorityIcon(alert.priority)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                            <Typography 
                              variant="subtitle2" 
                              sx={{ 
                                fontWeight: alert.read ? 'normal' : 'bold',
                                flexGrow: 1,
                                mr: 1
                              }}
                            >
                              {alert.title}
                            </Typography>
                            <Box display="flex" alignItems="center" gap={0.5}>
                              <Chip
                                label={alert.priority}
                                size="small"
                                color={getPriorityColor(alert.priority) as any}
                                variant="outlined"
                              />
                              <IconButton
                                size="small"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  dismissAlert(alert.id);
                                }}
                              >
                                <Clear fontSize="small" />
                              </IconButton>
                            </Box>
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography 
                              variant="body2" 
                              color="text.secondary"
                              sx={{ mb: 0.5 }}
                            >
                              {alert.message}
                            </Typography>
                            <Box display="flex" justifyContent="space-between" alignItems="center">
                              <Typography variant="caption" color="text.secondary">
                                {formatTimestamp(alert.timestamp)}
                              </Typography>
                              {alert.department && (
                                <Chip 
                                  label={alert.department} 
                                  size="small" 
                                  variant="outlined"
                                />
                              )}
                            </Box>
                          </Box>
                        }
                        onClick={() => {
                          if (!alert.read) {
                            markAsRead(alert.id);
                          }
                        }}
                      />
                    </ListItem>
                    {index < alerts.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            )}
          </Box>

          {/* Footer */}
          {alerts.length > 0 && (
            <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
              <Button 
                fullWidth 
                variant="outlined" 
                size="small"
                onClick={() => {
                  // Navigate to full notifications page
                  console.log('Navigate to full notifications');
                }}
              >
                View All Notifications
              </Button>
            </Box>
          )}
        </Box>
      </Popover>
    </>
  );
};

export default NotificationCenter;
