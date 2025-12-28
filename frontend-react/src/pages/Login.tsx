/**
 * Login Page - Premium FitTrack Pro
 * Beautiful glassmorphism login with animations
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate, Link } from 'react-router-dom';
import { Eye, EyeOff, Loader2, Mail, Lock, AlertCircle } from 'lucide-react';
import { useAuthStore } from '../store/authStore';

// Floating fitness emojis
const floatingEmojis = [
    { emoji: '🏃', size: 60, left: '10%', top: '20%', delay: 0 },
    { emoji: '💪', size: 70, left: '85%', top: '15%', delay: 0.5 },
    { emoji: '🥗', size: 55, left: '5%', top: '70%', delay: 1 },
    { emoji: '😴', size: 65, left: '90%', top: '75%', delay: 1.5 },
    { emoji: '💧', size: 50, left: '15%', top: '45%', delay: 2 },
    { emoji: '🎯', size: 60, left: '80%', top: '45%', delay: 2.5 },
    { emoji: '⚡', size: 55, left: '25%', top: '85%', delay: 3 },
    { emoji: '🏋️', size: 70, left: '70%', top: '80%', delay: 3.5 },
];

// Password strength checker
const checkPasswordStrength = (password: string): 'weak' | 'fair' | 'good' | 'strong' => {
    if (password.length === 0) return 'weak';
    let score = 0;
    if (password.length >= 8) score++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;

    if (score <= 1) return 'weak';
    if (score === 2) return 'fair';
    if (score === 3) return 'good';
    return 'strong';
};

export default function Login() {
    const navigate = useNavigate();
    const { login, isLoading, error, clearError, isAuthenticated, user } = useAuthStore();

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

    // Redirect if already authenticated
    useEffect(() => {
        if (isAuthenticated && user) {
            navigate(user.role === 'admin' ? '/admin' : '/dashboard');
        }
    }, [isAuthenticated, user, navigate]);

    // Track mouse for parallax
    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            setMousePosition({
                x: (e.clientX / window.innerWidth - 0.5) * 20,
                y: (e.clientY / window.innerHeight - 0.5) * 20,
            });
        };
        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        clearError();

        const success = await login({ username, password });
        if (success) {
            // Navigation handled by useEffect above
        }
    };

    const passwordStrength = checkPasswordStrength(password);

    return (
        <div className="min-h-screen bg-mesh-gradient noise-overlay relative overflow-hidden flex items-center justify-center px-4">
            {/* Gradient Orbs */}
            <div
                className="gradient-orb gradient-orb-indigo w-[500px] h-[500px] -top-40 -left-40"
                style={{ transform: `translate(${mousePosition.x * -1}px, ${mousePosition.y * -1}px)` }}
            />
            <div
                className="gradient-orb gradient-orb-pink w-[400px] h-[400px] -bottom-20 -right-20"
                style={{ transform: `translate(${mousePosition.x}px, ${mousePosition.y}px)` }}
            />

            {/* Floating Emojis with Parallax */}
            {floatingEmojis.map((item, index) => (
                <motion.div
                    key={index}
                    className="absolute pointer-events-none select-none z-0"
                    style={{
                        left: item.left,
                        top: item.top,
                        fontSize: item.size,
                        transform: `translate(${mousePosition.x * (index % 2 === 0 ? -1 : 1) * 0.5}px, ${mousePosition.y * (index % 2 === 0 ? 1 : -1) * 0.5}px)`,
                    }}
                    animate={{
                        y: [0, -20, 0],
                        rotate: [-5, 5, -5],
                    }}
                    transition={{
                        duration: 4 + index * 0.5,
                        repeat: Infinity,
                        delay: item.delay,
                        ease: 'easeInOut',
                    }}
                >
                    {item.emoji}
                </motion.div>
            ))}

            {/* Login Card */}
            <motion.div
                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                className="relative z-10 w-full max-w-md"
            >
                <div className="glass-card p-8 relative overflow-hidden">
                    {/* Animated border gradient */}
                    <div className="absolute inset-0 rounded-2xl overflow-hidden pointer-events-none">
                        <div
                            className="absolute inset-[-2px] rounded-2xl opacity-30"
                            style={{
                                background: 'linear-gradient(135deg, #6366f1, #ec4899, #6366f1)',
                                backgroundSize: '200% 200%',
                                animation: 'gradient-move 10s ease infinite',
                            }}
                        />
                    </div>

                    {/* Logo */}
                    <motion.div
                        className="text-center mb-8"
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        <div className="text-5xl mb-4">🏃‍♂️</div>
                        <h1 className="text-2xl font-bold gradient-text">FitTrack Pro</h1>
                        <p className="text-gray-400 mt-2">Welcome back! Sign in to continue</p>
                    </motion.div>

                    {/* Error Message */}
                    <AnimatePresence>
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-3 text-red-400"
                            >
                                <AlertCircle size={20} />
                                <span>{error}</span>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-5">
                        {/* Username Input */}
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.3 }}
                            className="relative"
                        >
                            <Mail className="input-icon" size={20} />
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                placeholder="Username or Email"
                                className="floating-input"
                                required
                            />
                        </motion.div>

                        {/* Password Input */}
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.4 }}
                            className="relative"
                        >
                            <Lock className="input-icon" size={20} />
                            <input
                                type={showPassword ? 'text' : 'password'}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Password"
                                className="floating-input pr-12"
                                required
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors z-10"
                            >
                                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                            </button>
                        </motion.div>

                        {/* Password Strength (shown when typing) */}
                        <AnimatePresence>
                            {password.length > 0 && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className={`strength-meter strength-${passwordStrength}`}
                                >
                                    <div className="strength-segment" />
                                    <div className="strength-segment" />
                                    <div className="strength-segment" />
                                    <div className="strength-segment" />
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Submit Button */}
                        <motion.button
                            type="submit"
                            disabled={isLoading}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.5 }}
                            whileTap={{ scale: 0.98 }}
                            className="btn-gradient w-full py-4 flex items-center justify-center gap-2 disabled:opacity-50"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="animate-spin" size={20} />
                                    Signing in...
                                </>
                            ) : (
                                'Sign In'
                            )}
                        </motion.button>
                    </form>

                    {/* Divider */}
                    <div className="flex items-center gap-4 my-6">
                        <div className="flex-1 h-px bg-white/10" />
                        <span className="text-gray-500 text-sm">or</span>
                        <div className="flex-1 h-px bg-white/10" />
                    </div>

                    {/* Register Link */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.6 }}
                        className="text-center"
                    >
                        <p className="text-gray-400">
                            Don't have an account?{' '}
                            <Link to="/register" className="text-indigo-400 hover:text-indigo-300 font-semibold transition-colors">
                                Sign up
                            </Link>
                        </p>
                    </motion.div>

                    {/* Demo Credentials */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.7 }}
                        className="mt-6 pt-6 border-t border-white/10 text-center"
                    >
                        <p className="text-gray-500 text-sm mb-2">Demo Credentials:</p>
                        <div className="flex justify-center gap-4 text-xs">
                            <span className="px-3 py-1 bg-indigo-500/10 rounded-full text-indigo-400">
                                admin@fittrack.com / admin123
                            </span>
                        </div>
                    </motion.div>
                </div>
            </motion.div>
        </div>
    );
}
