import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Moon, Clock, BedDouble, AlertCircle, Trash2 } from 'lucide-react';
import { sleepApi, dashboardApi } from '../services/api';
import { useAuthStore } from '../store/authStore';
import { useData } from '../context/DataContext';
import AreaTrendChart from '../components/charts/AreaTrendChart';
import BackButton from '../components/BackButton';
import HamburgerMenu from '../components/HamburgerMenu';
import ConfirmationModal from '../components/ConfirmationModal';
import toast from 'react-hot-toast';
import { getLocalDateString, getLocalDateStringDaysAgo } from '../utils/dateUtils';

export default function Sleep() {
    const { user } = useAuthStore();
    const { triggerRefresh } = useData();
    const [loading, setLoading] = useState(true);
    const [logs, setLogs] = useState<any[]>([]);
    const [weeklyData, setWeeklyData] = useState<any>(null); // Changed from chartData to weeklyData
    const [showLogModal, setShowLogModal] = useState(false);
    const [deleteId, setDeleteId] = useState<number | null>(null);

    // Fetch Data
    const fetchData = async () => {
        try {
            // Last night's sleep (approx today's date)
            const today = getLocalDateString();
            const [recentLogs, weeklyRes] = await Promise.all([
                sleepApi.getByDateRange(
                    getLocalDateStringDaysAgo(7),
                    today,
                    user?.id
                ),
                sleepApi.getWeekly(user?.id)
            ]);

            setLogs(recentLogs);
            setWeeklyData(weeklyRes); // Changed from setChartData to setWeeklyData
        } catch (error) {
            console.error('Failed to load sleep data', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (user) fetchData();
    }, [user]);

    const confirmDelete = async () => {
        if (!deleteId) return;
        try {
            await sleepApi.delete(deleteId);
            toast.success("Sleep log deleted");
            fetchData();
            triggerRefresh();
        } catch (error) {
            toast.error("Failed to delete sleep log");
        }
        setDeleteId(null);
    };

    if (loading) return <div className="p-8 text-center text-gray-400">Loading sleep analysis...</div>;

    const lastNight = logs.length > 0 ? logs[0] : null;
    const goal = 8; // Default goal
    const duration = lastNight?.total_hours || 0;
    const quality = lastNight?.sleep_quality || 0;

    return (
        <div className="min-h-screen px-4 sm:px-6 lg:px-8 py-6 pb-20">
            <HamburgerMenu />
            <div className="max-w-7xl mx-auto space-y-6">
                <BackButton to="/dashboard" label="Back to Dashboard" />
                {/* Header */}
                <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div>
                        <h1 className="text-2xl font-bold gradient-text flex items-center gap-2">
                            <Moon className="text-indigo-400" /> Sleep Tracker
                        </h1>
                        <p className="text-gray-400 text-sm">Monitor your rest and recovery.</p>
                    </div>
                    <button
                        onClick={() => setShowLogModal(true)}
                        className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                    >
                        + Log Sleep
                    </button>
                </header>

                {/* Main Sleep Card - Last Night */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="glass-card p-8 bg-gradient-to-br from-indigo-900/40 to-purple-900/40"
                >
                    <div className="flex flex-col md:flex-row justify-between items-center gap-8">
                        <div>
                            <h2 className="text-gray-400 uppercase text-xs tracking-wider mb-2">Last Night's Sleep</h2>
                            <div className="text-5xl font-bold mb-2 flex items-baseline gap-2">
                                {duration} <span className="text-xl font-normal text-gray-400">hours</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className={`px-2 py-0.5 rounded text-xs font-bold ${goal > duration ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'
                                    }`}>
                                    {Math.round((duration / goal) * 100)}% of goal
                                </span>
                            </div>
                        </div>

                        <div className="flex gap-8 text-center">
                            <div className="bg-black/20 p-4 rounded-xl min-w-[100px]">
                                <BedDouble size={24} className="mx-auto text-indigo-400 mb-2" />
                                <div className="text-lg font-bold">{lastNight?.bed_time?.slice(0, 5) || '--:--'}</div>
                                <div className="text-xs text-gray-500">Bedtime</div>
                            </div>
                            <div className="bg-black/20 p-4 rounded-xl min-w-[100px]">
                                <Clock size={24} className="mx-auto text-orange-400 mb-2" />
                                <div className="text-lg font-bold">{lastNight?.wake_time?.slice(0, 5) || '--:--'}</div>
                                <div className="text-xs text-gray-500">Wake Up</div>
                            </div>
                            <div className="bg-black/20 p-4 rounded-xl min-w-[100px]">
                                <div className="text-2xl mb-1">
                                    {quality >= 8 ? '😊' : quality >= 5 ? '😐' : '😫'}
                                </div>
                                <div className="text-lg font-bold">{quality}/10</div>
                                <div className="text-xs text-gray-500">Quality</div>
                            </div>
                        </div>
                    </div>
                </motion.div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Recent History */}
                    <div className="lg:col-span-1 space-y-4">
                        <h3 className="font-bold text-gray-300">Recent History</h3>
                        {logs.map((log) => (
                            <div key={log.id} className="glass-card p-4 flex justify-between items-center group">
                                <div>
                                    <div className="font-medium">{log.sleep_date}</div>
                                    <div className="text-xs text-gray-500">{log.bed_time?.slice(0, 5)} - {log.wake_time?.slice(0, 5)}</div>
                                </div>
                                <div className="flex items-center gap-4 text-right">
                                    <div>
                                        <div className="font-bold text-indigo-400">{log.total_hours}h</div>
                                        <div className="text-xs text-gray-500">Quality: {log.sleep_quality}</div>
                                    </div>
                                    <button
                                        onClick={() => setDeleteId(log.id)}
                                        className="p-2 hover:bg-white/10 rounded-lg text-gray-500 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
                                    >
                                        <Trash2 size={16} /> {/* Requires import, checking if available */}
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Trends Chart */}
                    <div className="lg:col-span-2 space-y-6">
                        <div className="glass-card p-6">
                            <h3 className="text-lg font-bold mb-4">Weekly Sleep Trend</h3>
                            <div className="h-64">
                                <div className="h-48">
                                    <AreaTrendChart
                                        data={weeklyData || []}
                                        dataKey="hours"
                                        color="#8b5cf6"
                                        height={180}
                                        gradientId="sleepWeekly"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <LogSleepModal
                    isOpen={showLogModal}
                    onClose={() => setShowLogModal(false)}
                    onAdd={() => { fetchData(); setShowLogModal(false); }}
                />

                <ConfirmationModal
                    isOpen={!!deleteId}
                    onClose={() => setDeleteId(null)}
                    onConfirm={confirmDelete}
                    title="Delete Sleep Log"
                    message="Are you sure you want to delete this sleep record?"
                    confirmLabel="Delete"
                    isDangerous={true}
                />
            </div>
        </div>
    );
}

function LogSleepModal({ isOpen, onClose, onAdd }: any) {
    const { user } = useAuthStore();
    const [bedTime, setBedTime] = useState('23:00');
    const [wakeTime, setWakeTime] = useState('07:00');
    const [quality, setQuality] = useState(7);
    const [date, setDate] = useState(getLocalDateString());

    const handleSubmit = async (e: any) => {
        e.preventDefault();
        // Calculate duration simply
        const start = new Date(`2000-01-01T${bedTime}`);
        const end = new Date(`2000-01-01T${wakeTime}`);
        if (end < start) end.setDate(end.getDate() + 1);
        const duration = (end.getTime() - start.getTime()) / (1000 * 60 * 60);

        try {
            await sleepApi.create({
                user_id: user?.id,
                sleep_date: date,
                bed_time: bedTime,
                wake_time: wakeTime,
                total_hours: parseFloat(duration.toFixed(1)),
                sleep_quality: quality
            });
            toast.success("Sleep logged");
            onAdd();
        } catch (error) {
            toast.error("Failed to log sleep");
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} className="glass-card p-6 w-full max-w-md">
                <h2 className="text-xl font-bold mb-6">Log Sleep</h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="text-sm text-gray-400">Date</label>
                        <input type="date" value={date} onChange={e => setDate(e.target.value)} className="w-full bg-black/20 border border-white/10 rounded-lg p-2" />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="text-sm text-gray-400">Bed Time</label>
                            <input type="time" value={bedTime} onChange={e => setBedTime(e.target.value)} className="w-full bg-black/20 border border-white/10 rounded-lg p-2" />
                        </div>
                        <div>
                            <label className="text-sm text-gray-400">Wake Time</label>
                            <input type="time" value={wakeTime} onChange={e => setWakeTime(e.target.value)} className="w-full bg-black/20 border border-white/10 rounded-lg p-2" />
                        </div>
                    </div>
                    <div>
                        <label className="text-sm text-gray-400 mb-2 block">Quality (1-10): {quality}</label>
                        <input type="range" min="1" max="10" value={quality} onChange={e => setQuality(parseInt(e.target.value))} className="w-full accent-indigo-500" />
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                            <span>Bad</span>
                            <span>Okay</span>
                            <span>Great</span>
                        </div>
                    </div>
                    <button className="w-full bg-indigo-600 py-3 rounded-lg font-bold mt-4">Save Sleep</button>
                    <button type="button" onClick={onClose} className="w-full mt-2 text-sm text-gray-400">Cancel</button>
                </form>
            </motion.div>
        </div>
    );
}
