import React, { useState, useEffect } from 'react';
import { useSupplyData } from '../context/SupplyDataContext';
import { 
  Users, 
  UserPlus, 
  Shield, 
  Edit, 
  Trash2, 
  Search,
  CheckCircle,
  XCircle,
  Lock,
  Mail,
  Phone
} from 'lucide-react';

const UserManagement = () => {
  const { loading } = useSupplyData();
  const [users, setUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRole, setFilterRole] = useState('ALL');
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [showUserModal, setShowUserModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [roles, setRoles] = useState([]);
  const [userLoading, setUserLoading] = useState(false);
  const [userForm, setUserForm] = useState({
    username: '',
    email: '',
    full_name: '',
    role: '',
    department: '',
    phone: '',
    is_active: true
  });

  useEffect(() => {
    initializeUserData();
    fetchRoles();
  }, []);

  const initializeUserData = () => {
    // Use sample data for users since user management data is not in shared context
    const sampleUsers = [
      {
        id: 1,
        username: 'admin',
        email: 'admin@hospital.com',
        full_name: 'System Administrator',
        role: 'ADMINISTRATOR',
        department: 'IT',
        phone: '+1-555-0100',
        is_active: true,
        created_at: '2024-01-15T08:00:00Z',
        last_login: '2025-07-14T09:30:00Z'
      },
      {
        id: 2,
        username: 'dr.smith',
        email: 'smith@hospital.com',
        full_name: 'Dr. Jennifer Smith',
        role: 'INVENTORY_MANAGER',
        department: 'Surgery',
        phone: '+1-555-0101',
        is_active: true,
        created_at: '2024-02-01T08:00:00Z',
        last_login: '2025-07-14T08:45:00Z'
      },
      {
        id: 3,
        username: 'nurse.johnson',
        email: 'johnson@hospital.com',
        full_name: 'Nurse Patricia Johnson',
        role: 'STAFF',
        department: 'ICU',
        phone: '+1-555-0102',
        is_active: true,
        created_at: '2024-03-01T08:00:00Z',
        last_login: '2025-07-13T16:20:00Z'
      }
    ];
    setUsers(sampleUsers);
  };

  const fetchUsers = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v2/users');
      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      } else {
        // Provide sample user data if endpoint fails
        setUsers([
          {
            id: 1,
            username: 'admin',
            email: 'admin@hospital.com',
            full_name: 'Hospital Administrator',
            role: 'Admin',
            department: 'Administration',
            phone: '+1-555-0001',
            is_active: true,
            last_login: '2025-07-12T10:30:00Z'
          },
          {
            id: 2,
            username: 'manager1',
            email: 'manager@hospital.com',
            full_name: 'Supply Manager',
            role: 'Manager',
            department: 'Supply Chain',
            phone: '+1-555-0002',
            is_active: true,
            last_login: '2025-07-12T09:15:00Z'
          },
          {
            id: 3,
            username: 'staff1',
            email: 'staff@hospital.com',
            full_name: 'ICU Staff',
            role: 'Staff',
            department: 'ICU',
            phone: '+1-555-0003',
            is_active: true,
            last_login: '2025-07-12T08:45:00Z'
          }
        ]);
      }
      setUserLoading(false);
    } catch (error) {
      console.error('Error fetching users:', error);
      setUserLoading(false);
    }
  };

  const fetchRoles = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v2/users/roles');
      if (response.ok) {
        const data = await response.json();
        setRoles(data);
      } else {
        // Provide sample roles data
        setRoles({
          'Admin': { permissions: ['all'], color: 'red' },
          'Manager': { permissions: ['read', 'write', 'approve'], color: 'blue' },
          'Staff': { permissions: ['read', 'write'], color: 'green' },
          'Viewer': { permissions: ['read'], color: 'gray' }
        });
      }
    } catch (error) {
      console.error('Error fetching roles:', error);
      // Provide sample roles data as fallback
      setRoles({
        'Admin': { permissions: ['all'], color: 'red' },
        'Manager': { permissions: ['read', 'write', 'approve'], color: 'blue' },
        'Staff': { permissions: ['read', 'write'], color: 'green' },
        'Viewer': { permissions: ['read'], color: 'gray' }
      });
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      const endpoint = isEditing 
        ? `http://localhost:8000/api/v2/users/${selectedUser.user_id}`
        : 'http://localhost:8000/api/v2/users';
      
      const method = isEditing ? 'PUT' : 'POST';
      
      const response = await fetch(endpoint, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userForm)
      });

      if (response.ok) {
        setShowUserModal(false);
        setIsEditing(false);
        setSelectedUser(null);
        setUserForm({
          username: '',
          email: '',
          full_name: '',
          role: '',
          department: '',
          phone: '',
          is_active: true
        });
        fetchUsers();
        alert(`User ${isEditing ? 'updated' : 'created'} successfully!`);
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      alert(`Error ${isEditing ? 'updating' : 'creating'} user`);
    }
  };

  const handleEditUser = (user) => {
    setSelectedUser(user);
    setUserForm({
      username: user.username,
      email: user.email,
      full_name: user.full_name,
      role: user.role,
      department: user.department,
      phone: user.phone || '',
      is_active: user.is_active
    });
    setIsEditing(true);
    setShowUserModal(true);
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    
    try {
      const response = await fetch(`http://localhost:8000/api/v2/users/${userId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        fetchUsers();
        alert('User deleted successfully!');
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      alert('Error deleting user');
    }
  };

  const handleToggleUserStatus = async (userId, currentStatus) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v2/users/${userId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !currentStatus })
      });

      if (response.ok) {
        fetchUsers();
        alert(`User ${!currentStatus ? 'activated' : 'deactivated'} successfully!`);
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      alert('Error updating user status');
    }
  };

  const getRoleColor = (role) => {
    const roleKey = role.toLowerCase();
    switch (roleKey) {
      case 'admin':
        return 'bg-purple-100 text-purple-800';
      case 'manager':
        return 'bg-blue-100 text-blue-800';
      case 'staff':
        return 'bg-green-100 text-green-800';
      case 'viewer':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesRole = filterRole === 'ALL' || user.role.toLowerCase() === filterRole.toLowerCase();
    const matchesStatus = filterStatus === 'ALL' || 
                         (filterStatus === 'active' && user.is_active) ||
                         (filterStatus === 'inactive' && !user.is_active);
    
    return matchesSearch && matchesRole && matchesStatus;
  });

  const userStats = {
    total: users.length,
    active: users.filter(u => u.is_active).length,
    inactive: users.filter(u => !u.is_active).length,
    admins: users.filter(u => u.role.toLowerCase() === 'admin').length,
    managers: users.filter(u => u.role.toLowerCase() === 'manager').length,
    staff: users.filter(u => u.role.toLowerCase() === 'staff').length
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <Users className="h-6 w-6 mr-2" />
              User Management
            </h1>
            <p className="mt-2 text-gray-600">
              Manage user accounts, roles, and permissions
            </p>
          </div>
          <button
            onClick={() => {
              setIsEditing(false);
              setSelectedUser(null);
              setUserForm({
                username: '',
                email: '',
                full_name: '',
                role: '',
                department: '',
                phone: '',
                is_active: true
              });
              setShowUserModal(true);
            }}
            className="btn btn-primary flex items-center"
          >
            <UserPlus className="h-4 w-4 mr-2" />
            Add User
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Users className="h-5 w-5 text-blue-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Users</p>
              <p className="text-2xl font-bold text-gray-900">{userStats.total}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Active</p>
              <p className="text-2xl font-bold text-gray-900">{userStats.active}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <XCircle className="h-5 w-5 text-red-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Inactive</p>
              <p className="text-2xl font-bold text-gray-900">{userStats.inactive}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Shield className="h-5 w-5 text-purple-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Admins</p>
              <p className="text-2xl font-bold text-gray-900">{userStats.admins}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Users className="h-5 w-5 text-blue-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Managers</p>
              <p className="text-2xl font-bold text-gray-900">{userStats.managers}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <Users className="h-5 w-5 text-green-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Staff</p>
              <p className="text-2xl font-bold text-gray-900">{userStats.staff}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <select
              value={filterRole}
              onChange={(e) => setFilterRole(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="ALL">All Roles</option>
              {roles && typeof roles === 'object' && Object.keys(roles).map(roleKey => (
                <option key={roleKey} value={roleKey}>
                  {roles[roleKey].name || roleKey}
                </option>
              ))}
              <option value="admin">Admin</option>
              <option value="manager">Manager</option>
              <option value="staff">Staff</option>
              <option value="viewer">Viewer</option>
            </select>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="ALL">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
          <div className="text-sm text-gray-600">
            Showing {filteredUsers.length} of {users.length} users
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {userLoading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-2">Loading users...</p>
          </div>
        ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contact
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Department
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Login
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredUsers.map((user) => (
                <tr key={user.id || user.user_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="h-10 w-10 bg-gray-300 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-gray-700">
                          {user.full_name.split(' ').map(n => n[0]).join('').toUpperCase()}
                        </span>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
                        <div className="text-sm text-gray-500">@{user.username}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 flex items-center">
                      <Mail className="h-4 w-4 mr-1" />
                      {user.email}
                    </div>
                    {user.phone && (
                      <div className="text-sm text-gray-500 flex items-center">
                        <Phone className="h-4 w-4 mr-1" />
                        {user.phone}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleColor(user.role)}`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {user.department}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEditUser(user)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleToggleUserStatus(user.id || user.user_id, user.is_active)}
                        className={user.is_active ? 'text-red-600 hover:text-red-800' : 'text-green-600 hover:text-green-800'}
                      >
                        {user.is_active ? <Lock className="h-4 w-4" /> : <CheckCircle className="h-4 w-4" />}
                      </button>
                      <button
                        onClick={() => handleDeleteUser(user.id || user.user_id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        )}
      </div>

      {/* User Modal */}
      {showUserModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-screen overflow-y-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {isEditing ? 'Edit User' : 'Add New User'}
            </h3>
            <form onSubmit={handleCreateUser} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
                <input
                  type="text"
                  value={userForm.username}
                  onChange={(e) => setUserForm(prev => ({ ...prev, username: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                  disabled={isEditing}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <input
                  type="text"
                  value={userForm.full_name}
                  onChange={(e) => setUserForm(prev => ({ ...prev, full_name: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  value={userForm.email}
                  onChange={(e) => setUserForm(prev => ({ ...prev, email: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                <input
                  type="tel"
                  value={userForm.phone}
                  onChange={(e) => setUserForm(prev => ({ ...prev, phone: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                <select
                  value={userForm.role}
                  onChange={(e) => setUserForm(prev => ({ ...prev, role: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Select Role</option>
                  <option value="admin">Admin</option>
                  <option value="manager">Manager</option>
                  <option value="staff">Staff</option>
                  <option value="viewer">Viewer</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
                <input
                  type="text"
                  value={userForm.department}
                  onChange={(e) => setUserForm(prev => ({ ...prev, department: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={userForm.is_active}
                  onChange={(e) => setUserForm(prev => ({ ...prev, is_active: e.target.checked }))}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                  Active User
                </label>
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowUserModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                >
                  {isEditing ? 'Update User' : 'Create User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagement;
