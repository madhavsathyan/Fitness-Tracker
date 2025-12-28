/**
 * Admin Panel Home
 * Landing page with 4 main feature cards
 */

import { useNavigate } from 'react-router-dom';
import {
    Users, Activity, FileText, BarChart3,
    Shield, ChevronRight
} from 'lucide-react';
import AdminHeader from '../../components/AdminHeader';

export default function AdminHome() {
    const navigate = useNavigate();

    const cards = [
        {
            title: "User Management",
            description: "View all registered users with unique IDs, manage accounts.",
            features: ["View users", "Unique IDs", "Delete accounts"],
            icon: Users,
            color: "from-blue-500 to-cyan-500",
            path: "/admin/users",
            btnText: "View Users"
        },
        {
            title: "Activity Log",
            description: "Track all data entries in real-time. See who entered what and when.",
            features: ["Live feed", "Timestamps", "User actions"],
            icon: Activity,
            color: "from-orange-500 to-red-500",
            path: "/admin/activity",
            btnText: "View Activity"
        },
        {
            title: "API Documentation",
            description: "View all REST API endpoints, methods, and how to use them.",
            features: ["Endpoints list", "Swagger link", "Examples"],
            icon: FileText,
            color: "from-gray-500 to-slate-500",
            path: "/admin/api",
            btnText: "View APIs"
        },
        {
            title: "Overview Dashboard",
            description: "View aggregated statistics and charts for ALL users in the system.",
            features: ["System-wide stats", "Charts", "User counts"],
            icon: BarChart3,
            color: "from-green-500 to-emerald-500",
            path: "/admin/overview",
            btnText: "View Overview"
        }
    ];

    return (
        <div className="min-h-screen bg-mesh-gradient noise-overlay py-12 px-4 md:px-8">
            <div className="max-w-6xl mx-auto">
                <AdminHeader
                    title="Admin Control Panel"
                    description="System management and global statistics"
                    showBack={false}
                />

                {/* 4 Feature Cards Grid */}
                <div className="grid md:grid-cols-2 gap-8">
                    {cards.map((card, index) => (
                        <div
                            key={index}
                            onClick={() => navigate(card.path)}
                            className="glass-card p-8 cursor-pointer group hover:bg-white/5 transition-all hover:-translate-y-1 hover:shadow-2xl hover:shadow-indigo-500/10 relative overflow-hidden"
                        >
                            {/* Glow Effect */}
                            <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${card.color} opacity-10 blur-2xl rounded-full -mr-10 -mt-10 transition-opacity group-hover:opacity-20`} />

                            <div className="flex items-start justify-between mb-6 relative">
                                <div className={`p-3 rounded-xl bg-gradient-to-br ${card.color} text-white shadow-lg`}>
                                    <card.icon size={28} />
                                </div>
                                <ChevronRight className="text-gray-500 group-hover:text-white group-hover:translate-x-1 transition-all" size={24} />
                            </div>

                            <h3 className="text-2xl font-bold mb-3 group-hover:text-white transition-colors">{card.title}</h3>
                            <p className="text-gray-400 mb-6 h-12">{card.description}</p>

                            <div className="mb-8 space-y-2">
                                {card.features.map((feat, i) => (
                                    <div key={i} className="flex items-center gap-2 text-sm text-gray-500 group-hover:text-gray-400">
                                        <div className="w-1 h-1 rounded-full bg-indigo-500" />
                                        {feat}
                                    </div>
                                ))}
                            </div>

                            <button className={`w-full py-3 rounded-xl bg-gradient-to-r ${card.color} text-white font-semibold opacity-90 hover:opacity-100 transition-opacity shadow-lg`}>
                                {card.btnText}
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
