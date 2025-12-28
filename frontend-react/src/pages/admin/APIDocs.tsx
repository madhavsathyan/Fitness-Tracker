/**
 * Admin API Docs
 * Documentation and endpoints reference
 */

import { useNavigate } from 'react-router-dom';
import {
    ArrowLeft, FileText, Server, Code, ExternalLink,
    Shield, Lock, Globe
} from 'lucide-react';

import AdminHeader from '../../components/AdminHeader';
import BackButton from '../../components/BackButton';

export default function AdminAPIDocs() {
    const navigate = useNavigate();

    const endpoints = [
        { method: 'GET', path: '/api/users/', desc: 'List all users (paginated)', access: 'Admin' },
        { method: 'POST', path: '/api/auth/register', desc: 'Register new user', access: 'Public' },
        { method: 'POST', path: '/api/auth/login', desc: 'Authenticate user', access: 'Public' },
        { method: 'GET', path: '/api/workouts/', desc: 'Get user workouts', access: 'User' },
        { method: 'POST', path: '/api/workouts/', desc: 'Log new workout', access: 'User' },
        { method: 'GET', path: '/api/activity/', desc: 'View system activity', access: 'Admin' },
        { method: 'GET', path: '/api/admin/stats', desc: 'Get system statistics', access: 'Admin' },
    ];

    const getMethodColor = (method: string) => {
        switch (method) {
            case 'GET': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
            case 'POST': return 'bg-green-500/20 text-green-400 border-green-500/30';
            case 'PUT': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
            case 'DELETE': return 'bg-red-500/20 text-red-400 border-red-500/30';
            default: return 'bg-gray-500/20 text-gray-400';
        }
    };

    return (
        <div className="min-h-screen bg-mesh-gradient noise-overlay py-8 px-4 md:px-8">
            <div className="max-w-7xl mx-auto">
                <BackButton to="/admin" label="Back to Admin" />
                <AdminHeader
                    title="API Documentation"
                    description="Backend resources and endpoints"
                />

                {/* Resource Cards */}
                <div className="grid md:grid-cols-3 gap-6 mb-12">
                    <a
                        href="http://localhost:8000/docs"
                        target="_blank"
                        rel="noreferrer"
                        className="glass-card p-6 group hover:scale-[1.02] transition-transform"
                    >
                        <div className="w-12 h-12 bg-green-500/20 text-green-400 rounded-xl flex items-center justify-center mb-4">
                            <FileText size={24} />
                        </div>
                        <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
                            Swagger UI <ExternalLink size={16} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                        </h3>
                        <p className="text-gray-400 text-sm">Interactive API documentation to test endpoints directly.</p>
                    </a>

                    <a
                        href="http://localhost:8000/redoc"
                        target="_blank"
                        rel="noreferrer"
                        className="glass-card p-6 group hover:scale-[1.02] transition-transform"
                    >
                        <div className="w-12 h-12 bg-red-500/20 text-red-400 rounded-xl flex items-center justify-center mb-4">
                            <Code size={24} />
                        </div>
                        <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
                            ReDoc <ExternalLink size={16} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                        </h3>
                        <p className="text-gray-400 text-sm">Clean, organized API reference documentation.</p>
                    </a>

                    <div className="glass-card p-6">
                        <div className="w-12 h-12 bg-blue-500/20 text-blue-400 rounded-xl flex items-center justify-center mb-4">
                            <Server size={24} />
                        </div>
                        <h3 className="text-xl font-bold mb-2">Server Status</h3>
                        <div className="flex items-center gap-2 text-green-400 text-sm font-medium">
                            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                            Online (v1.0.0)
                        </div>
                        <p className="text-gray-400 text-xs mt-2 font-mono">http://localhost:8000</p>
                    </div>
                </div>

                {/* Endpoints Table */}
                <div className="glass-card overflow-hidden">
                    <div className="p-6 border-b border-white/10">
                        <h3 className="text-lg font-bold flex items-center gap-2">
                            <Globe size={20} className="text-indigo-400" />
                            Key Endpoints
                        </h3>
                    </div>
                    <table className="w-full">
                        <thead>
                            <tr className="bg-white/5">
                                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-400">Method</th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-400">Endpoint</th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-400">Access</th>
                                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-400">Description</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {endpoints.map((ep, i) => (
                                <tr key={i} className="hover:bg-white/5 transition-colors">
                                    <td className="px-6 py-4">
                                        <span className={`px-2 py-1 rounded-md text-xs font-bold border ${getMethodColor(ep.method)}`}>
                                            {ep.method}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 font-mono text-sm text-gray-300">
                                        {ep.path}
                                    </td>
                                    <td className="px-6 py-4">
                                        {ep.access === 'Admin' ? (
                                            <span className="flex items-center gap-1 text-xs text-purple-400 bg-purple-500/10 px-2 py-1 rounded-full w-fit border border-purple-500/20">
                                                <Shield size={10} /> Admin
                                            </span>
                                        ) : ep.access === 'User' ? (
                                            <span className="flex items-center gap-1 text-xs text-blue-400 bg-blue-500/10 px-2 py-1 rounded-full w-fit border border-blue-500/20">
                                                <Lock size={10} /> User
                                            </span>
                                        ) : (
                                            <span className="flex items-center gap-1 text-xs text-green-400 bg-green-500/10 px-2 py-1 rounded-full w-fit border border-green-500/20">
                                                <Globe size={10} /> Public
                                            </span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-400">
                                        {ep.desc}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
