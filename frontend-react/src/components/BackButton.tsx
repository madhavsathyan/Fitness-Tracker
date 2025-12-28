import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Home } from 'lucide-react';

interface BackButtonProps {
    to?: string;
    label?: string;
}

export default function BackButton({ to, label = 'Back' }: BackButtonProps) {
    const navigate = useNavigate();
    const isDashboard = to === '/dashboard';
    const isAdmin = to === '/admin';

    const handleClick = () => {
        if (to) {
            navigate(to);
        } else {
            navigate(-1);
        }
    };

    return (
        <motion.button
            onClick={handleClick}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            whileHover={{ x: -4 }}
            whileTap={{ scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl 
                       bg-white/5 hover:bg-white/10 
                       border border-white/10 hover:border-indigo-500/30
                       text-gray-400 hover:text-white
                       transition-all duration-200 mb-4 group"
        >
            {/* Animated Arrow Container */}
            <motion.div
                className="relative flex items-center justify-center w-6 h-6 rounded-lg bg-indigo-500/20 group-hover:bg-indigo-500/30 transition-colors"
                whileHover={{ scale: 1.1 }}
            >
                <motion.div
                    animate={{ x: [0, -2, 0] }}
                    transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                >
                    <ArrowLeft size={14} className="text-indigo-400" />
                </motion.div>
            </motion.div>

            {/* Label with subtle gradient on hover */}
            <span className="text-sm font-medium tracking-wide">
                {label}
            </span>

            {/* Home icon for dashboard */}
            {(isDashboard || isAdmin) && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.1 }}
                    className="ml-1"
                >
                    <Home size={14} className="text-gray-500 group-hover:text-indigo-400 transition-colors" />
                </motion.div>
            )}
        </motion.button>
    );
}
