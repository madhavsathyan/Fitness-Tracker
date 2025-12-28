/**
 * Admin User Management
 * View, search, and manage all users
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Search, Trash2, ArrowLeft, MoreHorizontal,
    ChevronLeft, ChevronRight, Shield, User as UserIcon,
    X, CheckCircle, Ban, Activity, Calendar, FileText
} from 'lucide-react';
import toast from 'react-hot-toast';
import { adminApi, User } from '../../services/api';
import AdminHeader from '../../components/AdminHeader';
import BackButton from '../../components/BackButton';

export default function AdminUsers() {
    const navigate = useNavigate();
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [page, setPage] = useState(1);

    // Modals state
    const [activeDropdown, setActiveDropdown] = useState<number | null>(null);
    const [viewUser, setViewUser] = useState<any | null>(null);
    const [editUser, setEditUser] = useState<any | null>(null);
    const [deleteUser, setDeleteUser] = useState<number | null>(null);

    // Initial load
    useEffect(() => {
        loadUsers();
    }, []);

    // Search effect (debounce)
    useEffect(() => {
        const timeout = setTimeout(() => {
            if (searchQuery) {
                handleSearch();
            } else {
                loadUsers();
            }
        }, 500);
        return () => clearTimeout(timeout);
    }, [searchQuery]);

    const loadUsers = async () => {
        setLoading(true);
        try {
            const data = await adminApi.getAllUsers({ skip: (page - 1) * 20, limit: 20 });
            setUsers(data);
        } catch (error) {
            toast.error('Failed to load users');
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async () => {
        setLoading(true);
        try {
            const data = await adminApi.searchUsers(searchQuery);
            setUsers(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const fetchUserDetails = async (userId: number) => {
        try {
            const details = await adminApi.getUserDetails(userId);
            setViewUser(details);
        } catch (error) {
            toast.error('Failed to load user details');
        }
    };

    const handleSaveEdit = async () => {
        if (!editUser) return;
        try {
            // Update Role
            if (editUser.role !== editUser.originalRole) {
                await adminApi.updateUserRole(editUser.id, editUser.role);
            }
            // Update Blacklist
            if (editUser.is_blacklisted !== editUser.originalBlacklist) {
                await adminApi.toggleUserBlacklist(editUser.id, editUser.is_blacklisted, editUser.blacklist_reason);
            }
            toast.success('User updated successfully');
            setEditUser(null);
            loadUsers(); // Refresh list
        } catch (error) {
            toast.error('Failed to update user');
        }
    };

    const handleDelete = async () => {
        if (!deleteUser) return;
        try {
            await adminApi.deleteUser(deleteUser);
            toast.success('User deleted successfully');
            setUsers(users.filter(u => u.id !== deleteUser));
            setDeleteUser(null);
        } catch (error) {
            toast.error('Failed to delete user');
        }
    };

    return (
        <div className="min-h-screen bg-mesh-gradient noise-overlay py-8 px-4 md:px-8">
            <div className="max-w-7xl mx-auto">
                <BackButton to="/admin" label="Back to Admin" />
                <AdminHeader
                    title="User Management"
                    description="Search, view, and manage system users"
                >
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                        <input
                            type="text"
                            placeholder="Search by ID, name, or email..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:border-indigo-500 w-64 md:w-96"
                        />
                    </div>
                </AdminHeader>

                <div className="glass-card overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-white/10 bg-white/5">
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-400">User</th>
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-400">Role</th>
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-400">Status</th>
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-400">ID</th>
                                    <th className="px-6 py-4 text-right text-sm font-semibold text-gray-400">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {loading ? (
                                    <tr><td colSpan={5} className="px-6 py-8 text-center text-gray-500">Loading users...</td></tr>
                                ) : users.length === 0 ? (
                                    <tr><td colSpan={5} className="px-6 py-8 text-center text-gray-500">No users found.</td></tr>
                                ) : (
                                    users.map((user: any) => (
                                        <tr key={user.id} className="hover:bg-white/5 transition-colors">
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center font-bold">
                                                        {user.username[0].toUpperCase()}
                                                    </div>
                                                    <div>
                                                        <div className="font-medium text-white">{user.first_name ? `${user.first_name} ${user.last_name || ''}` : user.username}</div>
                                                        <div className="text-sm text-gray-400">{user.email}</div>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                {user.role === 'admin' ? (
                                                    <span className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded-lg text-xs font-semibold flex items-center gap-1 w-fit">
                                                        <Shield size={12} /> Admin
                                                    </span>
                                                ) : (
                                                    <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded-lg text-xs font-semibold flex items-center gap-1 w-fit">
                                                        <UserIcon size={12} /> User
                                                    </span>
                                                )}
                                            </td>
                                            <td className="px-6 py-4">
                                                {user.is_blacklisted ? (
                                                    <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded-lg text-xs font-semibold flex items-center gap-1 w-fit">
                                                        <Ban size={12} /> Blocked
                                                    </span>
                                                ) : (
                                                    <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded-lg text-xs font-semibold flex items-center gap-1 w-fit">
                                                        <CheckCircle size={12} /> Active
                                                    </span>
                                                )}
                                            </td>
                                            <td className="px-6 py-4 text-sm text-gray-400">
                                                #{user.unique_user_id || user.id}
                                            </td>
                                            <td className="px-6 py-4 text-right relative">
                                                <div className="flex items-center justify-end gap-2 relative">
                                                    <button
                                                        onClick={() => setActiveDropdown(activeDropdown === user.id ? null : user.id)}
                                                        className={`p-2 rounded-lg transition-colors ${activeDropdown === user.id ? 'bg-white/10 text-white' : 'text-gray-400 hover:text-white hover:bg-white/10'}`}
                                                    >
                                                        <MoreHorizontal size={18} />
                                                    </button>

                                                    {activeDropdown === user.id && (
                                                        <>
                                                            <div className="absolute right-0 top-full mt-2 w-48 bg-[#1a1b2e] border border-white/10 rounded-xl shadow-xl z-50 overflow-hidden backdrop-blur-xl text-left">
                                                                <button
                                                                    onClick={() => { fetchUserDetails(user.id); setActiveDropdown(null); }}
                                                                    className="w-full px-4 py-2 text-sm text-gray-300 hover:bg-white/5 flex items-center gap-2"
                                                                >
                                                                    <FileText size={14} /> View Details
                                                                </button>
                                                                <button
                                                                    onClick={() => { navigate(`/admin/users/${user.id}/activity`); setActiveDropdown(null); }}
                                                                    className="w-full px-4 py-2 text-sm text-gray-300 hover:bg-white/5 flex items-center gap-2"
                                                                >
                                                                    <Activity size={14} /> View Activity
                                                                </button>
                                                                <button
                                                                    onClick={() => {
                                                                        setEditUser({ ...user, originalRole: user.role, originalBlacklist: user.is_blacklisted });
                                                                        setActiveDropdown(null);
                                                                    }}
                                                                    className="w-full px-4 py-2 text-sm text-gray-300 hover:bg-white/5 flex items-center gap-2"
                                                                >
                                                                    <Shield size={14} /> Edit User
                                                                </button>
                                                                {user.role !== 'admin' && (
                                                                    <button
                                                                        onClick={() => { setDeleteUser(user.id); setActiveDropdown(null); }}
                                                                        className="w-full px-4 py-2 text-sm text-red-400 hover:bg-red-500/10 flex items-center gap-2 border-t border-white/5"
                                                                    >
                                                                        <Trash2 size={14} /> Delete User
                                                                    </button>
                                                                )}
                                                            </div>
                                                            <div className="fixed inset-0 z-40" onClick={() => setActiveDropdown(null)} />
                                                        </>
                                                    )}
                                                </div>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* View Details Modal */}
                {viewUser && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setViewUser(null)} />
                        <div className="relative w-full max-w-2xl bg-[#1e293b] border border-white/10 rounded-2xl shadow-2xl max-h-[85vh] overflow-y-auto">
                            <button onClick={() => setViewUser(null)} className="absolute right-4 top-4 text-gray-400 hover:text-white"><X size={20} /></button>

                            <div className="p-8">
                                <div className="flex items-center gap-4 mb-8">
                                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-2xl font-bold">
                                        {viewUser.username[0].toUpperCase()}
                                    </div>
                                    <div>
                                        <h2 className="text-2xl font-bold">{viewUser.username}</h2>
                                        <div className="flex items-center gap-2 text-gray-400">
                                            <span>{viewUser.email}</span>
                                            {viewUser.is_blacklisted && <span className="text-red-400 text-xs px-2 py-0.5 bg-red-500/10 rounded-full border border-red-500/20">Blocked</span>}
                                        </div>
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                                    <div className="space-y-4">
                                        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Account Info</h3>
                                        <div className="glass-card p-4 space-y-2">
                                            <div className="flex justify-between"><span className="text-gray-400">ID:</span> <span>#{viewUser.id}</span></div>
                                            <div className="flex justify-between"><span className="text-gray-400">Role:</span> <span className="capitalize">{viewUser.role}</span></div>
                                            <div className="flex justify-between"><span className="text-gray-400">Joined:</span> <span>{new Date(viewUser.created_at).toLocaleDateString()}</span></div>
                                        </div>
                                    </div>
                                    <div className="space-y-4">
                                        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Fitness Stats</h3>
                                        <div className="glass-card p-4 space-y-2">
                                            <div className="flex justify-between"><span className="text-gray-400">Age:</span> <span>{viewUser.age || '-'}</span></div>
                                            <div className="flex justify-between"><span className="text-gray-400">Weight:</span> <span>{viewUser.weight_kg ? `${viewUser.weight_kg}kg` : '-'}</span></div>
                                            <div className="flex justify-between"><span className="text-gray-400">BMI:</span> <span>{viewUser.bmi || '-'}</span></div>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex justify-end gap-3 mt-8 pt-6 border-t border-white/10">
                                    <button onClick={() => { setViewUser(null); navigate(`/admin/users/${viewUser.id}/activity`); }} className="px-4 py-2 bg-indigo-500 hover:bg-indigo-600 rounded-lg font-medium transition-colors">
                                        View Full Activity
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Edit User Modal */}
                {editUser && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setEditUser(null)} />
                        <div className="relative w-full max-w-md bg-[#1e293b] border border-white/10 rounded-2xl shadow-2xl p-6">
                            <h3 className="text-xl font-bold mb-6">Edit User: {editUser.username}</h3>

                            <div className="space-y-6">
                                <div>
                                    <label className="block text-sm font-medium text-gray-400 mb-2">User Role</label>
                                    <div className="grid grid-cols-2 gap-3">
                                        <button
                                            onClick={() => setEditUser({ ...editUser, role: 'user' })}
                                            className={`p-3 rounded-xl border flex items-center justify-center gap-2 transition-all ${editUser.role === 'user' ? 'bg-indigo-500/20 border-indigo-500 text-indigo-300' : 'border-white/10 hover:bg-white/5'}`}
                                        >
                                            <UserIcon size={18} /> User
                                        </button>
                                        <button
                                            onClick={() => setEditUser({ ...editUser, role: 'admin' })}
                                            className={`p-3 rounded-xl border flex items-center justify-center gap-2 transition-all ${editUser.role === 'admin' ? 'bg-purple-500/20 border-purple-500 text-purple-300' : 'border-white/10 hover:bg-white/5'}`}
                                        >
                                            <Shield size={18} /> Admin
                                        </button>
                                    </div>
                                    {editUser.role === 'admin' && <p className="text-xs text-orange-400 mt-2">⚠️ Warning: Admins have full access to the system.</p>}
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-400 mb-2">Account Status</label>
                                    <div className="space-y-3">
                                        <div className="flex items-center justify-between p-3 rounded-xl border border-white/10 bg-white/5">
                                            <div className="flex items-center gap-3">
                                                <Ban className={editUser.is_blacklisted ? "text-red-400" : "text-gray-400"} />
                                                <span>Blacklist User</span>
                                            </div>
                                            <div
                                                onClick={() => setEditUser({ ...editUser, is_blacklisted: !editUser.is_blacklisted })}
                                                className={`w-12 h-6 rounded-full p-1 cursor-pointer transition-colors ${editUser.is_blacklisted ? 'bg-red-500' : 'bg-gray-600'}`}
                                            >
                                                <div className={`w-4 h-4 bg-white rounded-full transition-transform ${editUser.is_blacklisted ? 'translate-x-6' : ''}`} />
                                            </div>
                                        </div>

                                        {editUser.is_blacklisted && (
                                            <input
                                                type="text"
                                                placeholder="Reason for blacklisting..."
                                                value={editUser.blacklist_reason || ''}
                                                onChange={(e) => setEditUser({ ...editUser, blacklist_reason: e.target.value })}
                                                className="w-full px-4 py-2 bg-black/20 border border-white/10 rounded-lg focus:outline-none focus:border-red-500"
                                            />
                                        )}
                                        {editUser.is_blacklisted && <p className="text-xs text-red-400">🚫 User will be blocked from logging in immediately.</p>}
                                    </div>
                                </div>
                            </div>

                            <div className="flex justify-end gap-3 mt-8">
                                <button onClick={() => setEditUser(null)} className="px-4 py-2 hover:bg-white/10 rounded-lg transition-colors">Cancel</button>
                                <button onClick={handleSaveEdit} className="px-4 py-2 bg-indigo-500 hover:bg-indigo-600 rounded-lg font-medium transition-colors">Save Changes</button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Delete Confirmation Modal */}
                {deleteUser && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setDeleteUser(null)} />
                        <div className="relative w-full max-w-sm bg-[#1e293b] border border-white/10 rounded-2xl shadow-2xl p-6 text-center">
                            <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4 text-red-500">
                                <Trash2 size={32} />
                            </div>
                            <h3 className="text-xl font-bold mb-2">Delete User?</h3>
                            <p className="text-gray-400 mb-6">Are you sure you want to delete this user? This action cannot be undone and will remove all their data.</p>

                            <div className="flex justify-center gap-3">
                                <button onClick={() => setDeleteUser(null)} className="px-4 py-2 hover:bg-white/10 rounded-lg transition-colors">Cancel</button>
                                <button onClick={handleDelete} className="px-4 py-2 bg-red-500 hover:bg-red-600 rounded-lg font-medium transition-colors">Delete Permanently</button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
