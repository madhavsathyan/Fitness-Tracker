/**
 * Admin Header Component
 * Standardized header for all admin pages with Profile/Logout
 */

import { useNavigate } from 'react-router-dom';
import { ArrowLeft, LogOut, Shield } from 'lucide-react';
import { useAuthStore } from '../store/authStore';

interface AdminHeaderProps {
    title: string;
    description: string;
    showBack?: boolean;
    children?: React.ReactNode;
}

export default function AdminHeader({ title, description, showBack = true, children }: AdminHeaderProps) {
    const navigate = useNavigate();
    const { user, logout } = useAuthStore();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-6 mb-8">
            <div className="flex items-center gap-4">
                {showBack && (
                    <button
                        onClick={() => navigate('/admin')}
                        className="p-2 hover:bg-white/10 rounded-lg transition-colors border border-transparent hover:border-white/10"
                    >
                        <ArrowLeft size={24} />
                    </button>
                )}
                {!showBack && (
                    <div className="p-3 bg-indigo-500/20 rounded-xl border border-indigo-500/30 text-indigo-400">
                        <Shield size={32} />
                    </div>
                )}
                <div>
                    <h1 className="text-3xl font-bold gradient-text">{title}</h1>
                    <p className="text-gray-400">{description}</p>
                </div>
            </div>

            {/* Actions & Profile */}
            <div className="flex flex-col-reverse md:flex-row md:items-center gap-4">
                {children}

                {/* Admin Profile Pill */}
                <div className="flex items-center gap-2">
                    <div className="flex items-center gap-3 px-4 py-2 bg-white/5 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                        <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full 
                                  flex items-center justify-center font-bold text-shadow-sm">
                            {user?.username?.[0]?.toUpperCase() || 'A'}
                        </div>
                        <span className="font-medium hidden sm:block">{user?.username || 'Admin'}</span>
                        <span className="px-2 py-0.5 bg-purple-500/20 text-purple-400 text-xs rounded-full font-medium border border-purple-500/20">
                            Admin
                        </span>
                    </div>

                    <button
                        onClick={handleLogout}
                        className="p-3 hover:bg-red-500/10 text-gray-400 hover:text-red-400 rounded-xl transition-all border border-transparent hover:border-red-500/20"
                        title="Logout"
                    >
                        <LogOut size={20} />
                    </button>
                </div>
            </div>
        </div>
    );
}
