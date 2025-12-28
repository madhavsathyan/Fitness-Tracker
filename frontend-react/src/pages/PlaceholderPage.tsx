import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Construction } from 'lucide-react';

export default function PlaceholderPage({ title, emoji }: { title: string; emoji: string }) {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-mesh-gradient noise-overlay p-6 flex flex-col items-center justify-center text-center relative overflow-hidden">
            {/* Gradient Orbs */}
            <div className="gradient-orb gradient-orb-indigo w-[500px] h-[500px] -top-20 -left-20" />
            <div className="gradient-orb gradient-orb-pink w-[300px] h-[300px] -bottom-10 -right-10" />

            <div className="relative z-10 glass-card p-12 max-w-lg w-full flex flex-col items-center">
                <div className="text-6xl mb-6">{emoji}</div>
                <h1 className="text-3xl font-bold mb-4 gradient-text">{title}</h1>
                <p className="text-gray-400 mb-8 text-lg">
                    This feature is currently under development. <br />
                    Check back soon for updates!
                </p>

                <div className="flex gap-4">
                    <button
                        onClick={() => navigate('/dashboard')}
                        className="btn-gradient px-6 py-3 flex items-center gap-2"
                    >
                        <ArrowLeft size={20} />
                        Back to Dashboard
                    </button>
                </div>
            </div>

            <div className="absolute bottom-6 flex items-center gap-2 text-gray-500 text-sm">
                <Construction size={16} />
                <span>Work in Progress</span>
            </div>
        </div>
    );
}
