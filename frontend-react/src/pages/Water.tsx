import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Droplets, Plus, Trash2, Calendar, Coffee, GlassWater, TrendingUp } from 'lucide-react';
import { waterApi, default as api } from '../services/api';
import { useAuthStore } from '../store/authStore';
import { useData } from '../context/DataContext';
import ProgressRing from '../components/charts/ProgressRing';
import WeeklyBarChart from '../components/charts/WeeklyBarChart';
import BackButton from '../components/BackButton';
import HamburgerMenu from '../components/HamburgerMenu';
import ConfirmationModal from '../components/ConfirmationModal';
import toast from 'react-hot-toast';
import { getLocalDateString } from '../utils/dateUtils';

export default function Water() {
    const { user } = useAuthStore();
    const { triggerRefresh } = useData();
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<any>(null);
    const [weeklyData, setWeeklyData] = useState<any[]>([]);
    const [customAmount, setCustomAmount] = useState('');
    const [drinkType, setDrinkType] = useState('water');
    const [showCustomInput, setShowCustomInput] = useState(false);
    const [logLoading, setLogLoading] = useState(false);
    const [deleteId, setDeleteId] = useState<number | null>(null);

    // Initial Fetch
    const fetchData = async () => {
        try {
            const today = getLocalDateString();
            const [dailyRes, chartRes] = await Promise.all([
                waterApi.getDailyTotal(today, user?.id),
                waterApi.getWeekly(user?.id)
            ]);

            setData(dailyRes);
            setWeeklyData(chartRes);
        } catch (error) {
            console.error('Failed to fetch water data', error);
            toast.error('Failed to load water data');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (user) fetchData();
    }, [user]);

    // Handle Add Water via Form/Buttons
    const logWater = async (amount: number, type: string = 'water') => {
        setLogLoading(true);
        try {
            await waterApi.create({
                user_id: user?.id,
                amount_ml: amount,
                beverage_type: type,
                intake_date: getLocalDateString(),
                intake_time: new Date().toLocaleTimeString('en-GB')
            });

            toast.success(`Logged ${amount}ml of ${type}`);
            fetchData();
            triggerRefresh(); // Trigger dashboard refresh
            setShowCustomInput(false);
            setCustomAmount('');
        } catch (error) {
            console.error('Failed to log water', error);
            toast.error('Failed to log water');
        } finally {
            setLogLoading(false);
        }
    };

    // Form Submit Handler
    const handleCustomSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (customAmount) {
            logWater(parseInt(customAmount), drinkType);
            setCustomAmount('');
            setDrinkType('water');
            setShowCustomInput(false);
        }
    };

    // Handle Delete
    const confirmDelete = async () => {
        if (!deleteId) return;
        try {
            await waterApi.delete(deleteId);
            toast.success('Log deleted');
            fetchData();
            triggerRefresh(); // Trigger dashboard refresh too
        } catch (error) {
            toast.error('Failed to delete log');
        }
        setDeleteId(null);
    };

    if (loading) return <div className="p-8 text-center text-gray-400">Loading hydration data...</div>;

    const dailyGoal = user?.daily_water_goal_ml || 2500;
    const currentAmount = data?.total_amount_ml || 0;
    const percentage = Math.round((currentAmount / dailyGoal) * 100);

    return (
        <div className="min-h-screen px-4 sm:px-6 lg:px-8 py-6 pb-20">
            <HamburgerMenu />
            <div className="max-w-7xl mx-auto space-y-6">
                <BackButton to="/dashboard" label="Back to Dashboard" />
                {/* Header */}
                <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div>
                        <h1 className="text-2xl font-bold gradient-text flex items-center gap-2">
                            <Droplets className="text-cyan-400" /> Hydration Tracker
                        </h1>
                        <p className="text-gray-400 text-sm">Stay hydrated, stay healthy.</p>
                    </div>
                    <div className="text-right">
                        <p className="text-xs text-gray-500 uppercase tracking-wider">Goal</p>
                        <p className="text-xl font-bold text-cyan-400">{dailyGoal} ml</p>
                    </div>
                </header>

                {/* Main Progress Card */}
                <motion.div
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    className="glass-card p-8 flex flex-col md:flex-row items-center justify-between gap-8"
                >
                    <div className="flex-1 text-center md:text-left">
                        <h2 className="text-3xl font-bold mb-2">{currentAmount} <span className="text-sm text-gray-400 font-normal">ml / {dailyGoal} ml</span></h2>
                        <div className="text-cyan-400 font-medium mb-4">{percentage}% of your daily goal</div>
                        <p className="text-sm text-gray-400">
                            {percentage >= 100 ? "🎉 Amazing job! You've hit your goal!" : "Keep drinking! You're doing great."}
                        </p>
                    </div>

                    <div className="relative">
                        <ProgressRing radius={80} stroke={12} progress={percentage} color="#06b6d4" />
                    </div>
                </motion.div>

                {/* Quick Add Actions */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[250, 500, 750, 1000].map((amount) => (
                        <motion.button
                            key={amount}
                            whileHover={{ y: -2 }}
                            whileTap={{ scale: 0.95 }}
                            disabled={logLoading}
                            onClick={() => logWater(amount)}
                            className="glass-card p-4 hover:bg-cyan-500/10 border-cyan-500/20 flex flex-col items-center justify-center gap-2 group transition-colors"
                        >
                            <div className="p-3 rounded-full bg-cyan-400/10 group-hover:bg-cyan-400/20 text-cyan-400 mb-1">
                                <Plus size={24} />
                            </div>
                            <span className="font-bold text-lg">{amount} ml</span>
                            <span className="text-xs text-gray-500">Quick Add</span>
                        </motion.button>
                    ))}
                </div>

                {/* Custom Add & List */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left Column: Today's Logs */}
                    <div className="lg:col-span-2 space-y-6">
                        <div className="glass-card p-6">
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-lg font-bold flex items-center gap-2">
                                    <Calendar size={18} className="text-gray-400" /> Today's Log
                                </h3>
                                <button
                                    onClick={() => setShowCustomInput(!showCustomInput)}
                                    className="text-xs bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg transition-colors"
                                >
                                    {showCustomInput ? 'Cancel' : '+ Custom Entry'}
                                </button>
                            </div>

                            {/* Custom Entry Form */}
                            <AnimatePresence>
                                {showCustomInput && (
                                    <motion.div
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: 'auto', opacity: 1 }}
                                        exit={{ height: 0, opacity: 0 }}
                                        className="overflow-hidden mb-6"
                                    >
                                        <form onSubmit={handleCustomSubmit} className="bg-white/5 p-4 rounded-xl flex gap-3">
                                            <input
                                                type="number"
                                                placeholder="Amount (ml)"
                                                value={customAmount}
                                                onChange={(e) => setCustomAmount(e.target.value)}
                                                className="bg-black/20 border border-white/10 rounded-lg px-4 py-2 w-full focus:outline-none focus:border-cyan-500/50"
                                                autoFocus
                                                min="1"
                                            />
                                            <select
                                                value={drinkType}
                                                onChange={(e) => setDrinkType(e.target.value)}
                                                className="bg-black/20 border border-white/10 rounded-lg px-4 py-2 focus:outline-none"
                                            >
                                                <option value="water">Water</option>
                                                <option value="coffee">Coffee</option>
                                                <option value="tea">Tea</option>
                                                <option value="juice">Juice</option>
                                                <option value="other">Other</option>
                                            </select>
                                            <button
                                                type="submit"
                                                disabled={logLoading || !customAmount}
                                                className="bg-cyan-600 hover:bg-cyan-500 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
                                            >
                                                Add
                                            </button>
                                        </form>
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            <div className="space-y-3">
                                {/* Logs Fetching Logic Rendered Directly */}
                                <WaterLogList userId={user?.id} refreshTrigger={data} onDelete={(id: number) => setDeleteId(id)} />
                            </div>
                        </div>
                    </div>

                    {/* Right Column: Weekly Chart */}
                    <div>
                        <div className="glass-card p-6 h-full">
                            <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                                <TrendingUp size={18} className="text-gray-400" /> Weekly Trend
                            </h3>
                            <div className="h-64">
                                <WeeklyBarChart data={weeklyData} dataKey="amount" color="#06b6d4" height={250} />
                            </div>
                        </div>
                    </div>
                    <ConfirmationModal
                        isOpen={!!deleteId}
                        onClose={() => setDeleteId(null)}
                        onConfirm={confirmDelete}
                        title="Delete Water Log"
                        message="Are you sure you want to delete this hydration entry?"
                        confirmLabel="Delete"
                        isDangerous={true}
                    />
                </div>
            </div>
        </div>
    );
}

function WaterLogList({ userId, refreshTrigger, onDelete }: any) {
    const [logs, setLogs] = useState<any[]>([]);

    useEffect(() => {
        const fetchLogs = async () => {
            if (!userId) return;
            const today = getLocalDateString();
            try {
                const response = await api.get('/water/', {
                    params: {
                        user_id: userId,
                        start_date: today,
                        end_date: today
                    }
                });
                setLogs(response.data);
            } catch (error) {
                console.error("Failed to fetch logs", error);
            }
        };
        fetchLogs();
    }, [userId, refreshTrigger]);

    if (logs.length === 0) {
        return <div className="text-center py-8 text-gray-500 text-sm">No water logged today yet.</div>;
    }

    return (
        <>
            {logs.map((log) => (
                <LogItem key={log.id} log={log} onDelete={onDelete} />
            ))}
        </>
    );
}

// Correcting the component to fetch logs properly
// LogItem component defined below



function LogItem({ log, onDelete }: any) {
    return (
        <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl hover:bg-white/10 transition-colors group">
            <div className="flex items-center gap-4">
                <div className={`p-2 rounded-full ${log.beverage_type === 'coffee' ? 'bg-amber-500/20 text-amber-500' :
                    log.beverage_type === 'tea' ? 'bg-green-500/20 text-green-500' :
                        'bg-cyan-500/20 text-cyan-500'
                    }`}>
                    {log.beverage_type === 'coffee' ? <Coffee size={18} /> :
                        log.beverage_type === 'tea' ? <Coffee size={18} /> :
                            <GlassWater size={18} />}
                </div>
                <div>
                    <div className="font-semibold">{log.amount_ml} ml <span className="text-gray-400 font-normal text-sm capitalize">{log.beverage_type}</span></div>
                    <div className="text-xs text-gray-500">{log.intake_time?.slice(0, 5)}</div>
                </div>
            </div>
            <button
                onClick={() => onDelete(log.id)}
                className="p-2 text-gray-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all"
            >
                <Trash2 size={16} />
            </button>
        </div>
    );
}
