import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
    Flame, Dumbbell, Moon, Droplets, TrendingUp,
    Activity, Target, X, Calendar, Clock, ChevronRight
} from 'lucide-react';
import { useAuthStore, useIsAdmin } from '../store/authStore';
import { useData } from '../context/DataContext';
import { dashboardApi, waterApi, sleepApi, workoutApi, nutritionApi, goalsApi } from '../services/api';
import HamburgerMenu from '../components/HamburgerMenu';
import { useTheme } from '../context/ThemeContext';
import toast from 'react-hot-toast';

// Charts
import ProgressRing from '../components/charts/ProgressRing';
import WeeklyBarChart from '../components/charts/WeeklyBarChart';
import AreaTrendChart from '../components/charts/AreaTrendChart';
import DonutChart from '../components/charts/DonutChart';
import { getLocalDateString } from '../utils/dateUtils';

// ============ MODALS ============

// Water Modal
function WaterModal({ isOpen, onClose, onSuccess, userId }: { isOpen: boolean; onClose: () => void; onSuccess: () => void; userId?: number }) {
    const [amount, setAmount] = useState('');
    const [loading, setLoading] = useState(false);

    const handleQuickAdd = async (ml: number) => {
        setLoading(true);
        try {
            await waterApi.create({
                user_id: userId,
                amount_ml: ml,
                beverage_type: 'water',
                intake_date: getLocalDateString(),
                intake_time: new Date().toLocaleTimeString('en-GB')
            });
            toast.success(`Added ${ml}ml water!`);
            onSuccess();
            onClose();
        } catch (e) {
            toast.error('Failed to add water');
        } finally {
            setLoading(false);
        }
    };

    const handleCustomSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!amount) return;
        await handleQuickAdd(parseInt(amount));
        setAmount('');
    };

    if (!isOpen) return null;

    return (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={onClose}>
            <motion.div initial={{ scale: 0.9, y: 20 }} animate={{ scale: 1, y: 0 }}
                className="glass-card p-6 w-full max-w-sm" onClick={e => e.stopPropagation()}>
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-2">
                        <span className="text-2xl">💧</span>
                        <h3 className="text-lg font-semibold">Add Water</h3>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg"><X size={20} /></button>
                </div>
                <div className="grid grid-cols-3 gap-3 mb-4">
                    {[250, 500, 1000].map((ml) => (
                        <button key={ml} disabled={loading} onClick={() => handleQuickAdd(ml)}
                            className="p-4 bg-cyan-500/20 border border-cyan-500/30 rounded-xl text-center hover:bg-cyan-500/30 transition-colors disabled:opacity-50">
                            <div className="font-semibold">{ml === 1000 ? '1L' : `${ml}ml`}</div>
                        </button>
                    ))}
                </div>
                <form onSubmit={handleCustomSubmit} className="flex gap-2">
                    <input type="number" placeholder="Custom amount (ml)" value={amount} onChange={(e) => setAmount(e.target.value)}
                        className="flex-1 bg-white/10 border border-white/20 rounded-lg px-4 py-2 focus:outline-none focus:border-cyan-500" />
                    <button type="submit" disabled={loading || !amount} className="btn-gradient px-4">Add</button>
                </form>
            </motion.div>
        </motion.div>
    );
}

// Sleep Modal
function SleepModal({ isOpen, onClose, onSuccess, userId }: { isOpen: boolean; onClose: () => void; onSuccess: () => void; userId?: number }) {
    const [date, setDate] = useState(getLocalDateString());
    const [bedTime, setBedTime] = useState('23:00');
    const [wakeTime, setWakeTime] = useState('07:00');
    const [quality, setQuality] = useState(7);
    const [loading, setLoading] = useState(false);

    const qualityOptions = [
        { label: '😫', value: 3, text: 'Poor' },
        { label: '😐', value: 5, text: 'Fair' },
        { label: '🙂', value: 7, text: 'Good' },
        { label: '😴', value: 9, text: 'Great' },
    ];

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            await sleepApi.create({
                user_id: userId,
                sleep_date: date,
                bedtime: bedTime,
                wake_time: wakeTime,
                quality_score: quality
            });
            toast.success('Sleep logged!');
            onSuccess();
            onClose();
        } catch (e) {
            toast.error('Failed to log sleep');
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={onClose}>
            <motion.div initial={{ scale: 0.9, y: 20 }} animate={{ scale: 1, y: 0 }}
                className="glass-card p-6 w-full max-w-sm" onClick={e => e.stopPropagation()}>
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-2">
                        <span className="text-2xl">😴</span>
                        <h3 className="text-lg font-semibold">Log Sleep</h3>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg"><X size={20} /></button>
                </div>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="text-sm text-gray-400 block mb-1">Date</label>
                        <input type="date" value={date} onChange={(e) => setDate(e.target.value)}
                            className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2" />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="text-sm text-gray-400 block mb-1">Bedtime</label>
                            <input type="time" value={bedTime} onChange={(e) => setBedTime(e.target.value)}
                                className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2" />
                        </div>
                        <div>
                            <label className="text-sm text-gray-400 block mb-1">Wake Time</label>
                            <input type="time" value={wakeTime} onChange={(e) => setWakeTime(e.target.value)}
                                className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2" />
                        </div>
                    </div>
                    <div>
                        <label className="text-sm text-gray-400 block mb-2">Quality</label>
                        <div className="grid grid-cols-4 gap-2">
                            {qualityOptions.map((opt) => (
                                <button key={opt.value} type="button" onClick={() => setQuality(opt.value)}
                                    className={`p-3 rounded-xl text-center transition-colors ${quality === opt.value ? 'bg-indigo-500 text-white' : 'bg-white/10'}`}>
                                    <div className="text-xl">{opt.label}</div>
                                    <div className="text-xs">{opt.text}</div>
                                </button>
                            ))}
                        </div>
                    </div>
                    <button type="submit" disabled={loading} className="btn-gradient w-full py-3">Save Sleep</button>
                </form>
            </motion.div>
        </motion.div>
    );
}

// Workout Modal
function WorkoutModal({ isOpen, onClose, onSuccess, userId }: { isOpen: boolean; onClose: () => void; onSuccess: () => void; userId?: number }) {
    const [name, setName] = useState('');
    const [type, setType] = useState('cardio');
    const [duration, setDuration] = useState('30');
    const [intensity, setIntensity] = useState('medium');
    const [calories, setCalories] = useState('');
    const [loading, setLoading] = useState(false);

    const types = [
        { value: 'cardio', label: '🏃 Cardio' },
        { value: 'strength', label: '💪 Strength' },
        { value: 'yoga', label: '🧘 Yoga' },
        { value: 'cycling', label: '🚴 Cycling' },
        { value: 'swimming', label: '🏊 Swimming' },
        { value: 'sports', label: '⚽ Sports' },
    ];

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            await workoutApi.create({
                user_id: userId,
                workout_name: name || `${type} workout`,
                workout_type: type,
                duration_minutes: parseInt(duration),
                calories_burned: calories ? parseInt(calories) : Math.round(parseInt(duration) * 8),
                intensity,
                workout_date: getLocalDateString(),
                start_time: new Date().toLocaleTimeString('en-GB')
            });
            toast.success('Workout logged!');
            setName(''); setDuration('30'); setCalories('');
            onSuccess();
            onClose();
        } catch (e) {
            toast.error('Failed to log workout');
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={onClose}>
            <motion.div initial={{ scale: 0.9, y: 20 }} animate={{ scale: 1, y: 0 }}
                className="glass-card p-6 w-full max-w-md" onClick={e => e.stopPropagation()}>
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-2">
                        <span className="text-2xl">🏋️</span>
                        <h3 className="text-lg font-semibold">Log Workout</h3>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg"><X size={20} /></button>
                </div>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="text-sm text-gray-400 block mb-2">Type</label>
                        <div className="grid grid-cols-3 gap-2">
                            {types.map((t) => (
                                <button key={t.value} type="button" onClick={() => setType(t.value)}
                                    className={`p-2 rounded-lg text-sm transition-colors ${type === t.value ? 'bg-purple-500 text-white' : 'bg-white/10'}`}>
                                    {t.label}
                                </button>
                            ))}
                        </div>
                    </div>
                    <div>
                        <label className="text-sm text-gray-400 block mb-1">Workout Name (optional)</label>
                        <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Morning Run"
                            className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2" />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="text-sm text-gray-400 block mb-1">Duration (min)</label>
                            <input type="number" value={duration} onChange={(e) => setDuration(e.target.value)}
                                className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2" />
                        </div>
                        <div>
                            <label className="text-sm text-gray-400 block mb-1">Calories (optional)</label>
                            <input type="number" value={calories} onChange={(e) => setCalories(e.target.value)} placeholder="Auto"
                                className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2" />
                        </div>
                    </div>
                    <div>
                        <label className="text-sm text-gray-400 block mb-2">Intensity</label>
                        <div className="flex gap-2">
                            {['low', 'medium', 'high'].map((i) => (
                                <button key={i} type="button" onClick={() => setIntensity(i)}
                                    className={`flex-1 py-2 rounded-lg transition-colors ${intensity === i ?
                                        (i === 'low' ? 'bg-green-500' : i === 'medium' ? 'bg-yellow-500' : 'bg-red-500') + ' text-white' : 'bg-white/10'}`}>
                                    {i === 'low' ? '🟢' : i === 'medium' ? '🟡' : '🔴'} {i.charAt(0).toUpperCase() + i.slice(1)}
                                </button>
                            ))}
                        </div>
                    </div>
                    <button type="submit" disabled={loading} className="btn-gradient w-full py-3">Log Workout</button>
                </form>
            </motion.div>
        </motion.div>
    );
}

// Meal Modal
function MealModal({ isOpen, onClose, onSuccess, userId }: { isOpen: boolean; onClose: () => void; onSuccess: () => void; userId?: number }) {
    const [mealType, setMealType] = useState('lunch');
    const [name, setName] = useState('');
    const [calories, setCalories] = useState('');
    const [protein, setProtein] = useState('');
    const [carbs, setCarbs] = useState('');
    const [fats, setFats] = useState('');
    const [loading, setLoading] = useState(false);

    const mealTypes = [
        { value: 'breakfast', label: '🌅 Breakfast' },
        { value: 'lunch', label: '☀️ Lunch' },
        { value: 'dinner', label: '🌙 Dinner' },
        { value: 'snack', label: '🍪 Snack' },
    ];

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            await nutritionApi.create({
                user_id: userId,
                meal_type: mealType,
                food_name: name || mealType,
                calories: parseInt(calories) || 0,
                protein_g: parseFloat(protein) || 0,
                carbs_g: parseFloat(carbs) || 0,
                fat_g: parseFloat(fats) || 0,
                meal_date: getLocalDateString(),
                meal_time: new Date().toLocaleTimeString('en-GB')
            });
            toast.success('Meal logged!');
            setName(''); setCalories(''); setProtein(''); setCarbs(''); setFats('');
            onSuccess();
            onClose();
        } catch (e) {
            toast.error('Failed to log meal');
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={onClose}>
            <motion.div initial={{ scale: 0.9, y: 20 }} animate={{ scale: 1, y: 0 }}
                className="glass-card p-6 w-full max-w-md" onClick={e => e.stopPropagation()}>
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-2">
                        <span className="text-2xl">🍎</span>
                        <h3 className="text-lg font-semibold">Log Meal</h3>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg"><X size={20} /></button>
                </div>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="text-sm text-gray-400 block mb-2">Meal Type</label>
                        <div className="grid grid-cols-4 gap-2">
                            {mealTypes.map((t) => (
                                <button key={t.value} type="button" onClick={() => setMealType(t.value)}
                                    className={`p-2 rounded-lg text-xs transition-colors ${mealType === t.value ? 'bg-orange-500 text-white' : 'bg-white/10'}`}>
                                    {t.label}
                                </button>
                            ))}
                        </div>
                    </div>
                    <div>
                        <label className="text-sm text-gray-400 block mb-1">Food Name</label>
                        <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Grilled Chicken"
                            className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2" />
                    </div>
                    <div>
                        <label className="text-sm text-gray-400 block mb-1">Calories</label>
                        <input type="number" value={calories} onChange={(e) => setCalories(e.target.value)} placeholder="kcal"
                            className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2" />
                    </div>
                    <div className="grid grid-cols-3 gap-3">
                        <div>
                            <label className="text-sm text-gray-400 block mb-1">Protein (g)</label>
                            <input type="number" value={protein} onChange={(e) => setProtein(e.target.value)}
                                className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2" />
                        </div>
                        <div>
                            <label className="text-sm text-gray-400 block mb-1">Carbs (g)</label>
                            <input type="number" value={carbs} onChange={(e) => setCarbs(e.target.value)}
                                className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2" />
                        </div>
                        <div>
                            <label className="text-sm text-gray-400 block mb-1">Fats (g)</label>
                            <input type="number" value={fats} onChange={(e) => setFats(e.target.value)}
                                className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-2" />
                        </div>
                    </div>
                    <button type="submit" disabled={loading} className="btn-gradient w-full py-3">Log Meal</button>
                </form>
            </motion.div>
        </motion.div>
    );
}

// ============ MAIN DASHBOARD ============

export default function Dashboard() {
    const navigate = useNavigate();
    const { user, logout } = useAuthStore();
    const { refreshTrigger } = useData();
    const isAdmin = useIsAdmin();
    const [chartData, setChartData] = useState<any>(null);
    const [dashboardStats, setDashboardStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [menuOpen, setMenuOpen] = useState(false);
    const [profileOpen, setProfileOpen] = useState(false);

    const { theme, toggleTheme } = useTheme();

    // Modal states
    const [waterModalOpen, setWaterModalOpen] = useState(false);
    const [sleepModalOpen, setSleepModalOpen] = useState(false);
    const [workoutModalOpen, setWorkoutModalOpen] = useState(false);
    const [mealModalOpen, setMealModalOpen] = useState(false);

    // Data states
    const [todayProgress, setTodayProgress] = useState<any>(null);
    const [weeklyOverview, setWeeklyOverview] = useState<any>(null);
    const [workoutsChartData, setWorkoutsChartData] = useState<any[]>([]);
    const [goals, setGoals] = useState<any[]>([]);

    // Time state for greeting
    const [now, setNow] = useState(new Date());

    useEffect(() => {
        const timer = setInterval(() => setNow(new Date()), 60000);
        return () => clearInterval(timer);
    }, []);

    // Random Quote Logic
    const [quote, setQuote] = useState('');
    useEffect(() => {
        const quotes = [
            "The only bad workout is the one that didn't happen. 🏃‍♂️",
            "Discipline is doing what needs to be done. 💪",
            "Your health is an investment, not an expense. 💎",
            "Don't stop when you're tired. Stop when you're done. 🔥",
            "You don't have to be great to start, but you have to start to be great. 🚀",
            "Motivation is what gets you started. Habit is what keeps you going. 🔄",
            "Small steps every day add up to big results. 📈",
            "Sweat is magic. Cover yourself in it daily to grant your wishes. ✨"
        ];
        setQuote(quotes[Math.floor(Math.random() * quotes.length)]);
    }, []);

    // Redirect admins
    useEffect(() => {
        if (isAdmin) navigate('/admin');
    }, [isAdmin, navigate]);

    const fetchData = async () => {
        if (isAdmin || !user?.id) return;
        try {
            const [todayData, weeklyData, workoutsData, charts, goalsData] = await Promise.all([
                dashboardApi.getTodayProgress(user.id),
                dashboardApi.getWeeklyOverview(user.id),
                dashboardApi.getWorkoutsChartData(user.id),
                dashboardApi.getDashboardCharts(),
                goalsApi.getAll({ user_id: user.id, is_active: true })
            ]);

            setTodayProgress(todayData);
            setWeeklyOverview(weeklyData);

            // Backend already provides data in correct format with day names
            const formattedWorkouts = Array.isArray(workoutsData) ? workoutsData : [];
            setWorkoutsChartData(formattedWorkouts);

            setChartData(charts);
            setGoals(goalsData?.slice(0, 3) || []);
        } catch (error) {
            console.error('Failed to fetch dashboard:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [user?.id, refreshTrigger]); // Re-fetch when refreshTrigger changes

    const handleLogout = (e?: React.MouseEvent) => {
        e?.stopPropagation();
        setProfileOpen(false);

        // Clear auth state
        logout();
        localStorage.clear();

        // Navigate to login
        navigate('/login', { replace: true });
    };

    // Dynamic Greeting
    const getGreeting = () => {
        const hour = now.getHours();
        if (hour < 5) return { text: 'Good night', emoji: '🌙' };
        if (hour < 12) return { text: 'Good morning', emoji: '☀️' };
        if (hour < 17) return { text: 'Good afternoon', emoji: '🌤️' };
        if (hour < 21) return { text: 'Good evening', emoji: '🌅' };
        return { text: 'Good night', emoji: '🌙' };
    };

    const greeting = getGreeting();
    const currentDate = now.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' });
    const currentTime = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });

    // Goals
    const userGoals = {
        water: user?.daily_water_goal_ml || 3000,
        sleep: 8,
        workout: (user as any)?.daily_workout_goal_minutes || 60,
        calories: user?.daily_calorie_goal || 2000
    };

    if (loading) return <div className="h-screen flex items-center justify-center text-white">Loading...</div>;

    return (
        <div className="min-h-screen bg-mesh-gradient noise-overlay">
            {/* Gradient Orbs */}
            <div className="gradient-orb gradient-orb-indigo w-[600px] h-[600px] -top-60 -left-60 fixed" />
            <div className="gradient-orb gradient-orb-pink w-[400px] h-[400px] -bottom-40 -right-40 fixed" />

            <div className="relative z-10">
                {/* Header */}
                <header className="border-b border-white/10 backdrop-blur-xl sticky top-0 z-20">
                    <div className="w-full px-4 md:w-[98%] xl:w-[95%] max-w-[1600px] mx-auto py-4 flex items-center justify-between">
                        <div className="flex items-center gap-3 ml-12"> {/* Added ml-12 for hamburger button space */}
                            <span className="text-2xl">🏃‍♂️</span>
                            <h1 className="text-xl font-bold gradient-text">FitTrack Pro</h1>
                        </div>
                        <div className="flex items-center gap-4">

                            <div className="relative">
                                <button onClick={() => setProfileOpen(!profileOpen)} className="flex items-center gap-3 px-2 py-1.5 hover:bg-white/5 rounded-xl transition-all">
                                    <div className="w-9 h-9 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-full flex items-center justify-center font-bold">
                                        {user?.username?.[0]?.toUpperCase() || 'U'}
                                    </div>
                                    <div className="hidden sm:block text-left">
                                        <div className="text-sm font-semibold">{user?.username}</div>
                                    </div>
                                </button>
                                {profileOpen && (
                                    <div className="absolute right-0 top-full mt-2 w-64 bg-[#1a1b2e] border border-white/10 rounded-xl shadow-2xl z-50 p-2">
                                        <button onClick={handleLogout} className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-red-400 hover:bg-red-500/10">Logout</button>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </header>

                <HamburgerMenu />

                <main className="w-full px-4 md:w-[98%] xl:w-[95%] max-w-[1600px] mx-auto py-8">
                    {/* Welcome Section */}
                    <div className="glass-card mb-8 p-8 flex flex-col md:flex-row md:items-end justify-between gap-6 relative overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/10 via-purple-500/5 to-transparent opacity-50" />
                        <div className="relative z-10">
                            <h2 className="text-4xl md:text-5xl font-bold mb-4 gradient-text tracking-tight">
                                {greeting.text}, {user?.first_name || 'Champion'}! {greeting.emoji}
                            </h2>
                            <div className="text-lg text-gray-400 font-medium mb-2 flex items-center gap-4">
                                <span className="flex items-center gap-2"><Calendar size={16} /> {currentDate}</span>
                                <span className="flex items-center gap-2"><Clock size={16} /> {currentTime}</span>
                            </div>
                            <p className="text-gray-300 max-w-2xl text-lg italic opacity-90">"{quote}"</p>
                        </div>
                        {/* Streak card removed as requested */}
                    </div>

                    {/* Today's Progress Cards */}
                    <h3 className="text-xl font-bold mb-4 flex items-center gap-2"><Activity size={20} /> Today's Progress</h3>
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                        {/* Water Card */}
                        <div className="glass-card p-5">
                            <div className="flex justify-between items-start mb-3">
                                <div className="p-2 bg-cyan-500/20 rounded-lg"><Droplets size={20} className="text-cyan-400" /></div>
                                <button onClick={() => setWaterModalOpen(true)} className="p-2 bg-cyan-500/20 text-cyan-400 rounded-lg hover:bg-cyan-500/30 text-sm">+ Add</button>
                            </div>
                            <div className="text-2xl font-bold">{((todayProgress?.water?.total_ml || 0) / 1000).toFixed(1)}<span className="text-sm font-normal text-gray-400">/{(todayProgress?.water?.goal_ml || 3000) / 1000}L</span></div>
                            <div className="text-sm text-gray-400 mb-2">Water</div>
                            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                                <div className="h-full bg-cyan-400 rounded-full transition-all" style={{ width: `${Math.min(100, todayProgress?.water?.percentage || 0)}%` }} />
                            </div>
                            <div className="text-xs text-gray-500 mt-1">{todayProgress?.water?.percentage || 0}%</div>
                        </div>

                        {/* Sleep Card */}
                        <div className="glass-card p-5">
                            <div className="flex justify-between items-start mb-3">
                                <div className="p-2 bg-indigo-500/20 rounded-lg"><Moon size={20} className="text-indigo-400" /></div>
                                <button onClick={() => setSleepModalOpen(true)} className="p-2 bg-indigo-500/20 text-indigo-400 rounded-lg hover:bg-indigo-500/30 text-sm">+ Log</button>
                            </div>
                            <div className="text-2xl font-bold">{todayProgress?.sleep?.hours || 0}<span className="text-sm font-normal text-gray-400">/{todayProgress?.sleep?.goal_hours || 8} hrs</span></div>
                            <div className="text-sm text-gray-400 mb-2">Sleep</div>
                            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                                <div className="h-full bg-indigo-400 rounded-full transition-all" style={{ width: `${Math.min(100, todayProgress?.sleep?.percentage || 0)}%` }} />
                            </div>
                            <div className="text-xs text-gray-500 mt-1">{todayProgress?.sleep?.percentage || 0}%</div>
                        </div>

                        {/* Workout Card */}
                        <div className="glass-card p-5">
                            <div className="flex justify-between items-start mb-3">
                                <div className="p-2 bg-purple-500/20 rounded-lg"><Dumbbell size={20} className="text-purple-400" /></div>
                                <button onClick={() => setWorkoutModalOpen(true)} className="p-2 bg-purple-500/20 text-purple-400 rounded-lg hover:bg-purple-500/30 text-sm">+ Log</button>
                            </div>
                            <div className="text-2xl font-bold">{todayProgress?.workouts?.minutes || 0}<span className="text-sm font-normal text-gray-400">/{todayProgress?.workouts?.goal_minutes || 60} min</span></div>
                            <div className="text-sm text-gray-400 mb-2">Workout</div>
                            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                                <div className="h-full bg-purple-400 rounded-full transition-all" style={{ width: `${Math.min(100, todayProgress?.workouts?.percentage || 0)}%` }} />
                            </div>
                            <div className="text-xs text-gray-500 mt-1">{todayProgress?.workouts?.percentage || 0}%</div>
                        </div>

                        {/* Calories Card */}
                        <div className="glass-card p-5">
                            <div className="flex justify-between items-start mb-3">
                                <div className="p-2 bg-orange-500/20 rounded-lg"><Flame size={20} className="text-orange-400" /></div>
                                <button onClick={() => setMealModalOpen(true)} className="p-2 bg-orange-500/20 text-orange-400 rounded-lg hover:bg-orange-500/30 text-sm">+ Log</button>
                            </div>
                            <div className="text-2xl font-bold">{todayProgress?.nutrition?.calories || 0}<span className="text-sm font-normal text-gray-400">/{todayProgress?.nutrition?.goal || 2000}</span></div>
                            <div className="text-sm text-gray-400 mb-2">Calories</div>
                            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                                <div className="h-full bg-orange-400 rounded-full transition-all" style={{ width: `${Math.min(100, todayProgress?.nutrition?.percentage || 0)}%` }} />
                            </div>
                            <div className="text-xs text-gray-500 mt-1">{todayProgress?.nutrition?.percentage || 0}%</div>
                        </div>
                    </div>

                    {/* Weekly Overview */}
                    <h3 className="text-xl font-bold mb-4 flex items-center gap-2"><TrendingUp size={20} /> Weekly Overview</h3>
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                        <div className="glass-card p-5">
                            <div className="text-3xl font-bold text-orange-400">{weeklyOverview?.current?.calories_burned?.toLocaleString() || '0'}</div>
                            <div className="text-sm text-gray-400">kcal burned</div>
                            {/* Simple comparison logic */}
                            <div className={`text-xs mt-1 ${(weeklyOverview?.current?.calories_burned || 0) >= (weeklyOverview?.previous?.calories_burned || 0)
                                ? 'text-green-400' : 'text-red-400'
                                }`}>
                                {((weeklyOverview?.current?.calories_burned || 1) / (weeklyOverview?.previous?.calories_burned || 1) * 100 - 100).toFixed(0)}% vs last week
                            </div>
                        </div>
                        <div className="glass-card p-5">
                            <div className="text-3xl font-bold text-purple-400">{weeklyOverview?.current?.workout_sessions || '0'}</div>
                            <div className="text-sm text-gray-400">workout sessions</div>
                            <div className={`text-xs mt-1 ${(weeklyOverview?.current?.workout_sessions || 0) >= (weeklyOverview?.previous?.workout_sessions || 0)
                                ? 'text-green-400' : 'text-gray-400'
                                }`}>
                                {weeklyOverview?.previous?.workout_sessions
                                    ? `${weeklyOverview.current.workout_sessions - weeklyOverview.previous.workout_sessions} difference`
                                    : 'No prev data'}
                            </div>
                        </div>
                        <div className="glass-card p-5">
                            <div className="text-3xl font-bold text-indigo-400">{(weeklyOverview?.current?.avg_sleep || 0).toFixed(1)}</div>
                            <div className="text-sm text-gray-400">hrs avg sleep</div>
                            <div className="text-xs text-gray-400 mt-1">vs {(weeklyOverview?.previous?.avg_sleep || 0).toFixed(1)} prev week</div>
                        </div>
                        <div className="glass-card p-5">
                            <div className="text-3xl font-bold text-cyan-400">{((weeklyOverview?.current?.total_water || 0) / 1000).toFixed(1)}</div>
                            <div className="text-sm text-gray-400">liters water</div>
                            <div className={`text-xs mt-1 ${(weeklyOverview?.current?.total_water || 0) >= (weeklyOverview?.previous?.total_water || 0)
                                ? 'text-green-400' : 'text-red-400'
                                }`}>
                                {((weeklyOverview?.current?.total_water || 1) / (weeklyOverview?.previous?.total_water || 1) * 100 - 100).toFixed(0)}% vs last week
                            </div>
                        </div>
                    </div>

                    {/* Goals Progress */}
                    <div className="glass-card p-6 mb-8">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-xl font-bold flex items-center gap-2"><Target size={20} /> Goals Progress</h3>
                            <button onClick={() => navigate('/goals')} className="text-sm text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                                View All <ChevronRight size={16} />
                            </button>
                        </div>
                        {goals.length > 0 ? (
                            <div className="space-y-4">
                                {goals.map((goal: any) => (
                                    <div key={goal.id} className="flex items-center gap-4">
                                        <div className="flex-1">
                                            <div className="flex justify-between mb-1">
                                                <span className="text-sm font-medium">{goal.goal_type} Goal</span>
                                                <span className="text-sm text-gray-400">{goal.current_value || 0}/{goal.target_value} {goal.unit}</span>
                                            </div>
                                            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                                                <div className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"
                                                    style={{ width: `${Math.min(100, ((goal.current_value || 0) / goal.target_value) * 100)}%` }} />
                                            </div>
                                        </div>
                                        <span className="text-sm font-bold text-indigo-400">{Math.round(((goal.current_value || 0) / goal.target_value) * 100)}%</span>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-gray-400 text-center py-4">No active goals. <button onClick={() => navigate('/goals')} className="text-indigo-400">Create one!</button></p>
                        )}
                    </div>

                    {/* Charts Row */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                        {/* Calories Chart */}
                        <div className="glass-card p-6">
                            <h3 className="text-lg font-bold flex items-center gap-2 text-orange-400 mb-4"><Flame size={20} /> Calories This Week</h3>
                            <div className="h-48">
                                <AreaTrendChart data={chartData?.calories?.weekly_trend || []} dataKey="calories" color="#f97316" height={180} gradientId="calGrad" />
                            </div>
                        </div>
                        {/* Workouts Chart */}
                        <div className="glass-card p-6">
                            <h3 className="text-lg font-bold flex items-center gap-2 text-purple-400 mb-4"><Dumbbell size={20} /> Workouts This Week</h3>
                            <div className="h-48">
                                <WeeklyBarChart data={workoutsChartData} dataKey="minutes" color="#8b5cf6" height={180} />
                            </div>
                        </div>
                    </div>

                    {/* Water & Sleep Row */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Water */}
                        <div className="glass-card p-6">
                            <div className="flex justify-between items-start mb-4">
                                <h3 className="text-lg font-bold flex items-center gap-2 text-cyan-400"><Droplets size={20} /> Water Intake</h3>
                            </div>
                            <div className="flex justify-center mb-4">
                                <ProgressRing radius={70} stroke={10} progress={todayProgress?.water?.percentage || 0} color="#06b6d4" />
                            </div>
                            <div className="h-32">
                                <WeeklyBarChart data={chartData?.water?.weekly || []} dataKey="amount" color="#06b6d4" height={120} />
                            </div>
                        </div>

                        {/* Sleep */}
                        <div className="glass-card p-6">
                            <h3 className="text-lg font-bold flex items-center gap-2 text-indigo-400 mb-4"><Moon size={20} /> Sleep Analysis</h3>
                            <div className="mb-4">
                                <div className="flex justify-between text-sm text-gray-400 mb-2">
                                    <span>Last Night</span>
                                    <span className="text-white font-bold">{todayProgress?.sleep?.hours || 0} hours</span>
                                </div>
                                <div className="h-4 w-full rounded-full flex overflow-hidden">
                                    <div className="bg-indigo-800 w-[20%]" title="Deep" />
                                    <div className="bg-indigo-500 w-[55%]" title="Light" />
                                    <div className="bg-purple-400 w-[25%]" title="REM" />
                                </div>
                                <div className="flex justify-between text-xs text-gray-500 mt-1">
                                    <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-indigo-800" /> Deep</div>
                                    <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-indigo-500" /> Light</div>
                                    <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-purple-400" /> REM</div>
                                </div>
                            </div>
                            <div className="h-32">
                                <AreaTrendChart data={chartData?.sleep?.weekly_trend || []} dataKey="hours" color="#6366f1" height={120} gradientId="sleepGrad" />
                            </div>
                        </div>
                    </div>
                </main>
            </div>

            {/* Modals */}
            <AnimatePresence>
                {waterModalOpen && <WaterModal isOpen={waterModalOpen} onClose={() => setWaterModalOpen(false)} onSuccess={fetchData} userId={user?.id} />}
                {sleepModalOpen && <SleepModal isOpen={sleepModalOpen} onClose={() => setSleepModalOpen(false)} onSuccess={fetchData} userId={user?.id} />}
                {workoutModalOpen && <WorkoutModal isOpen={workoutModalOpen} onClose={() => setWorkoutModalOpen(false)} onSuccess={fetchData} userId={user?.id} />}
                {mealModalOpen && <MealModal isOpen={mealModalOpen} onClose={() => setMealModalOpen(false)} onSuccess={fetchData} userId={user?.id} />}
            </AnimatePresence>
        </div>
    );
}
