import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Menu, X, Home, Dumbbell, Apple, Moon, Droplets,
    Target, LayoutDashboard, ChevronRight
} from 'lucide-react';

const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/workouts', icon: Dumbbell, label: 'Workouts' },
    { path: '/nutrition', icon: Apple, label: 'Nutrition' },
    { path: '/sleep', icon: Moon, label: 'Sleep' },
    { path: '/water', icon: Droplets, label: 'Water' },
    { path: '/goals', icon: Target, label: 'Goals' },
];

export default function HamburgerMenu() {
    const [isOpen, setIsOpen] = useState(false);
    const location = useLocation();

    return (
        <>
            {/* Hamburger Button */}
            <motion.button
                onClick={() => setIsOpen(!isOpen)}
                className="fixed top-4 left-4 z-50 p-3 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 hover:bg-white/20 transition-all"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
            >
                <motion.div
                    animate={{ rotate: isOpen ? 90 : 0 }}
                    transition={{ duration: 0.2 }}
                >
                    {isOpen ? <X size={24} /> : <Menu size={24} />}
                </motion.div>
            </motion.button>

            {/* Overlay */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setIsOpen(false)}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
                    />
                )}
            </AnimatePresence>

            {/* Slide-out Menu */}
            <AnimatePresence>
                {isOpen && (
                    <motion.nav
                        initial={{ x: '-100%' }}
                        animate={{ x: 0 }}
                        exit={{ x: '-100%' }}
                        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                        className="fixed top-0 left-0 h-full w-72 bg-slate-900/95 backdrop-blur-xl border-r border-white/10 z-50 p-6"
                    >
                        {/* Logo */}
                        <div className="flex items-center gap-3 mb-8 mt-12">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                                <Dumbbell size={20} className="text-white" />
                            </div>
                            <span className="text-xl font-bold gradient-text">FitTrack Pro</span>
                        </div>

                        {/* Nav Items */}
                        <div className="space-y-2">
                            {navItems.map((item) => {
                                const isActive = location.pathname === item.path;
                                return (
                                    <Link
                                        key={item.path}
                                        to={item.path}
                                        onClick={() => setIsOpen(false)}
                                        className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${isActive
                                                ? 'bg-purple-600/30 text-purple-300 border border-purple-500/30'
                                                : 'hover:bg-white/10 text-gray-400 hover:text-white'
                                            }`}
                                    >
                                        <item.icon size={20} />
                                        <span className="font-medium">{item.label}</span>
                                        {isActive && (
                                            <ChevronRight size={16} className="ml-auto text-purple-400" />
                                        )}
                                    </Link>
                                );
                            })}
                        </div>

                        {/* Close hint */}
                        <div className="absolute bottom-6 left-6 right-6 text-center">
                            <p className="text-xs text-gray-500">Press ESC or click outside to close</p>
                        </div>
                    </motion.nav>
                )}
            </AnimatePresence>
        </>
    );
}
