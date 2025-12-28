/**
 * Admin Activity Log
 * Real-time system events
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    ArrowLeft, Activity, RefreshCw, Filter, Clock,
    User, AlertCircle, CheckCircle, PlusCircle, Trash2
} from 'lucide-react';
import toast from 'react-hot-toast';
import { adminApi } from '../../services/api';

import AdminHeader from '../../components/AdminHeader';
import BackButton from '../../components/BackButton';

interface ActivityLog {
    id: number;
    user_id: number;
    username: string;
    action_type: string;
    entity_type: string;
    description: string;
    details?: string;
    created_at: string;
}

export default function AdminActivity() {
    const navigate = useNavigate();
    const [logs, setLogs] = useState<ActivityLog[]>([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState<any>(null);
    const [refreshing, setRefreshing] = useState(false);

    useEffect(() => {
        loadData();
        // Poll every 30s
        const interval = setInterval(() => loadData(true), 30000);
        return () => clearInterval(interval);
    }, []);

    const loadData = async (silent = false) => {
        if (!silent) setLoading(true);
        setRefreshing(true);
        try {
            const [logsData, statsData] = await Promise.all([
                adminApi.getActivityFeed({ limit: 50 }),
                adminApi.getActivityStats()
            ]);
            setLogs(logsData);
            setStats(statsData);
        } catch (error) {
            if (!silent) toast.error('Failed to load activity log');
        } finally {
            if (!silent) setLoading(false);
            setRefreshing(false);
        }
    };

    const getActionIcon = (action: string) => {
        switch (action) {
            case 'CREATE': return <PlusCircle size={16} className="text-green-400" />;
            case 'DELETE': return <Trash2 size={16} className="text-red-400" />;
            case 'UPDATE': return <RefreshCw size={16} className="text-blue-400" />;
            case 'LOGIN': return <User size={16} className="text-purple-400" />;
            case 'REGISTER': return <User size={16} className="text-green-400" />;
            default: return <Activity size={16} className="text-gray-400" />;
        }
    };

    const getActionColor = (action: string) => {
        switch (action) {
            case 'CREATE': return 'bg-green-500/10 text-green-400 border-green-500/20';
            case 'DELETE': return 'bg-red-500/10 text-red-400 border-red-500/20';
            case 'UPDATE': return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
            case 'LOGIN':
            case 'REGISTER': return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
            default: return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
        }
    };

    return (
        <div className="min-h-screen bg-mesh-gradient noise-overlay py-8 px-4 md:px-8">
            <div className="max-w-7xl mx-auto">
                <BackButton to="/admin" label="Back to Admin" />
                <AdminHeader
                    title="System Activity Log"
                    description="Real-time tracking of user and system actions"
                >
                    <button
                        onClick={() => loadData()}
                        disabled={refreshing}
                        className={`p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors ${refreshing ? 'animate-spin' : ''}`}
                        title="Refresh"
                    >
                        <RefreshCw size={20} />
                    </button>
                </AdminHeader>

                {/* Stats Row */}
                {stats && (
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                        <div className="glass-card p-4">
                            <div className="text-gray-400 text-xs font-semibold uppercase tracking-wider mb-1">Total Events</div>
                            <div className="text-2xl font-bold">{stats.total_logs}</div>
                        </div>
                        <div className="glass-card p-4">
                            <div className="text-green-400 text-xs font-semibold uppercase tracking-wider mb-1">Last 24 Hours</div>
                            <div className="text-2xl font-bold">{stats.last_24_hours}</div>
                        </div>
                        <div className="glass-card p-4">
                            <div className="text-blue-400 text-xs font-semibold uppercase tracking-wider mb-1">Users Active</div>
                            <div className="text-2xl font-bold">{Object.keys(stats.by_entity || {}).length}</div>
                        </div>
                        <div className="glass-card p-4">
                            <div className="text-purple-400 text-xs font-semibold uppercase tracking-wider mb-1">Actions</div>
                            <div className="text-2xl font-bold">{Object.keys(stats.by_action || {}).length} types</div>
                        </div>
                    </div>
                )}

                <div className="glass-card overflow-hidden">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-white/10 bg-white/5">
                                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-400">Time</th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-400">User</th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-400">Action</th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-400">Description</th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-400">Details</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {loading ? (
                                <tr>
                                    <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                                        Loading activity...
                                    </td>
                                </tr>
                            ) : logs.length === 0 ? (
                                <tr>
                                    <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                                        No activity logs found.
                                    </td>
                                </tr>
                            ) : (
                                logs.map((log) => (
                                    <tr key={log.id} className="hover:bg-white/5 transition-colors">
                                        <td className="px-6 py-4 text-sm text-gray-400 text-nowrap">
                                            {new Date(log.created_at).toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-2">
                                                <div className="w-6 h-6 rounded-full bg-white/10 flex items-center justify-center text-xs">
                                                    {log.username[0]?.toUpperCase() || '?'}
                                                </div>
                                                <span className="text-sm font-medium">{log.username}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`px-2 py-1 rounded-full text-xs font-semibold border flex items-center gap-1 w-fit ${getActionColor(log.action_type)}`}>
                                                {getActionIcon(log.action_type)}
                                                {log.action_type}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-sm">
                                            {log.description}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-400 font-mono text-xs">
                                            {log.details || '-'}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
