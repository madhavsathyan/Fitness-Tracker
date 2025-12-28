import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Dumbbell, Trash2, Flame, Activity } from 'lucide-react';
import { workoutApi } from '../services/api';
import { useAuthStore } from '../store/authStore';
import { useData } from '../context/DataContext';
import WeeklyBarChart from '../components/charts/WeeklyBarChart';
import DonutChart from '../components/charts/DonutChart';
import BackButton from '../components/BackButton';
import HamburgerMenu from '../components/HamburgerMenu';
import ConfirmationModal from '../components/ConfirmationModal';
import toast from 'react-hot-toast';
import { getLocalDateString } from '../utils/dateUtils';

export default function Workouts() {
    const { user } = useAuthStore();
    const { triggerRefresh } = useData();
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<any>(null);
    const [weeklyData, setWeeklyData] = useState<any[]>([]);
    const [workouts, setWorkouts] = useState<any[]>([]);
    const [showLogModal, setShowLogModal] = useState(false);
    const [deleteId, setDeleteId] = useState<number | null>(null);

    const fetchData = async () => {
        try {
            const today = getLocalDateString();
            const [dailyRes, weeklyRes, recentWorkouts] = await Promise.all([
                workoutApi.getDailySummary(today, user?.id),
                workoutApi.getWeekly(user?.id),
                workoutApi.getAll({ user_id: user?.id, limit: 10 })
            ]);
            setData(dailyRes);
            setWeeklyData(weeklyRes);
            setWorkouts(recentWorkouts);
        } catch (error) {
            console.error('Failed to load workout data', error);
            toast.error('Failed to load data');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (user) fetchData();
    }, [user]);

    const today = getLocalDateString();
    const todaysWorkouts = workouts.filter(w => w.workout_date === today);
    const totalMinutes = todaysWorkouts.reduce((acc, w) => acc + w.duration_minutes, 0);
    const totalCalories = todaysWorkouts.reduce((acc, w) => acc + (w.calories_burned || 0), 0);
    const dailyGoal = 60;

    const confirmDelete = async () => {
        if (!deleteId) return;
        try {
            await workoutApi.delete(deleteId);
            toast.success('Workout deleted');
            fetchData();
            triggerRefresh();
        } catch (e) { toast.error('Failed to delete'); }
        setDeleteId(null);
    }

    if (loading) return <div className="p-8 text-center text-gray-400">Loading workout data...</div>;

    return (
        <div className="min-h-screen px-4 sm:px-6 lg:px-8 py-6 pb-20">
            <HamburgerMenu />

            <div className="max-w-7xl mx-auto space-y-6">
                <BackButton to="/dashboard" label="Back to Dashboard" />

                {/* Header */}
                <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div>
                        <h1 className="text-2xl font-bold gradient-text flex items-center gap-2">
                            <Dumbbell className="text-purple-400" /> Workouts
                        </h1>
                        <p className="text-gray-400 text-sm">Track your fitness journey.</p>
                    </div>
                    <button
                        onClick={() => setShowLogModal(true)}
                        className="bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                    >
                        + Log Workout
                    </button>
                </header>

                {/* Daily Summary */}
                <div className="glass-card p-6 flex flex-col md:flex-row items-center gap-8">
                    <div className="flex-1 w-full space-y-4">
                        <div className="flex justify-between items-end">
                            <div>
                                <div className="text-4xl font-bold">{totalMinutes}<span className="text-xl text-gray-400 font-normal">min</span></div>
                                <div className="text-sm text-gray-400">/ {dailyGoal} min goal</div>
                            </div>
                            <div className="text-right">
                                <div className="text-xl font-bold text-orange-400 flex items-center gap-1 justify-end">
                                    <Flame size={16} /> {Math.round(totalCalories)}
                                </div>
                                <div className="text-sm text-gray-400">kcal burned</div>
                            </div>
                        </div>
                        {/* Progress Bar */}
                        <div className="h-4 bg-white/10 rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${Math.min(100, (totalMinutes / dailyGoal) * 100)}%` }}
                                className="h-full bg-gradient-to-r from-purple-500 to-indigo-500"
                            />
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Workout List */}
                    <div className="lg:col-span-2 space-y-4">
                        <h3 className="font-bold text-gray-300">Recent Sessions</h3>
                        {workouts.length === 0 ? (
                            <div className="text-center py-8 text-gray-500 italic">No workouts logged recently. Get moving!</div>
                        ) : (
                            workouts.map(w => (
                                <motion.div
                                    key={w.id}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    className="glass-card p-4 flex justify-between items-center group"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className={`p-3 rounded-xl ${w.intensity === 'high' ? 'bg-red-500/20 text-red-500' :
                                            w.intensity === 'medium' ? 'bg-yellow-500/20 text-yellow-500' :
                                                'bg-blue-500/20 text-blue-500'
                                            }`}>
                                            <Activity size={20} />
                                        </div>
                                        <div>
                                            <div className="font-bold text-lg">{w.workout_name}</div>
                                            <div className="text-xs text-gray-400 flex gap-2">
                                                <span className="capitalize">{w.workout_type}</span> • {w.workout_date}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-6">
                                        <div className="text-right">
                                            <div className="font-bold">{w.duration_minutes} min</div>
                                            <div className="text-xs text-orange-400">{w.calories_burned} kcal</div>
                                        </div>
                                        <button onClick={() => setDeleteId(w.id)} className="p-2 hover:bg-white/10 rounded-lg text-gray-500 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100">
                                            <Trash2 size={16} />
                                        </button>
                                    </div>
                                </motion.div>
                            ))
                        )}
                    </div>

                    {/* Charts */}
                    <div className="space-y-6">
                        {/* Types Donut */}
                        <div className="glass-card p-6">
                            <h3 className="text-sm font-bold mb-4 uppercase text-gray-400">Workout Mix</h3>
                            <div className="h-48">
                                {workouts.length > 0 ? (
                                    <DonutChart
                                        data={(() => {
                                            const typeCount: Record<string, number> = {};
                                            workouts.forEach(w => {
                                                typeCount[w.workout_type] = (typeCount[w.workout_type] || 0) + 1;
                                            });
                                            return Object.entries(typeCount).map(([name, value]) => ({ name, value }));
                                        })()}
                                        colors={['#8b5cf6', '#ec4899', '#3b82f6', '#10b981']}
                                        height={180}
                                    />
                                ) : (
                                    <div className="h-full flex items-center justify-center text-gray-500 text-sm">No workout data yet</div>
                                )}
                            </div>
                        </div>

                        {/* Weekly Activity */}
                        <div className="glass-card p-6">
                            <h3 className="text-sm font-bold mb-4 uppercase text-gray-400">Weekly Activity</h3>
                            <div className="h-40">
                                <WeeklyBarChart
                                    data={weeklyData.map(d => ({ day: d.day, minutes: d.duration || 0 }))}
                                    dataKey="minutes"
                                    color="#8b5cf6"
                                    height={150}
                                />
                            </div>
                        </div>
                    </div>
                </div>

                <LogWorkoutModal
                    isOpen={showLogModal}
                    onClose={() => setShowLogModal(false)}
                    onAdd={() => { fetchData(); triggerRefresh(); setShowLogModal(false); }}
                />

                <ConfirmationModal
                    isOpen={!!deleteId}
                    onClose={() => setDeleteId(null)}
                    onConfirm={confirmDelete}
                    title="Delete Workout"
                    message="Are you sure you want to delete this workout? This action cannot be undone."
                    confirmLabel="Delete"
                    isDangerous={true}
                />
            </div>
        </div>
    );
}

function LogWorkoutModal({ isOpen, onClose, onAdd }: any) {
    const { user } = useAuthStore();
    const [name, setName] = useState('');
    const [type, setType] = useState('cardio');
    const [duration, setDuration] = useState('');
    const [cals, setCals] = useState('');
    const [intensity, setIntensity] = useState('medium');

    const handleSubmit = async (e: any) => {
        e.preventDefault();
        try {
            await workoutApi.create({
                user_id: user?.id,
                workout_name: name,
                workout_type: type,
                duration_minutes: parseInt(duration),
                calories_burned: parseInt(cals),
                intensity,
                workout_date: getLocalDateString(),
                start_time: new Date().toLocaleTimeString('en-GB')
            });
            toast.success("Workout logged!");
            setName('');
            setDuration('');
            setCals('');
            setType('cardio');
            setIntensity('medium');
            onAdd();
        } catch (e) { toast.error("Failed to log workout"); }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} className="glass-card p-6 w-full max-w-md">
                <h2 className="text-xl font-bold mb-6">Log Workout</h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="text-sm text-gray-400">Activity Name</label>
                        <input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Morning Run" className="w-full bg-black/20 border border-white/10 rounded-lg p-2" required />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="text-sm text-gray-400">Type</label>
                            <select value={type} onChange={e => setType(e.target.value)} className="w-full bg-black/20 border border-white/10 rounded-lg p-2" >
                                <option value="cardio">Cardio</option>
                                <option value="strength">Strength</option>
                                <option value="flexibility">Flexibility</option>
                                <option value="sports">Sports</option>
                            </select>
                        </div>
                        <div>
                            <label className="text-sm text-gray-400">Intensity</label>
                            <select value={intensity} onChange={e => setIntensity(e.target.value)} className="w-full bg-black/20 border border-white/10 rounded-lg p-2" >
                                <option value="low">Low</option>
                                <option value="medium">Medium</option>
                                <option value="high">High</option>
                            </select>
                        </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="text-sm text-gray-400">Duration (min)</label>
                            <input type="number" value={duration} onChange={e => setDuration(e.target.value)} className="w-full bg-black/20 border border-white/10 rounded-lg p-2" required />
                        </div>
                        <div>
                            <label className="text-sm text-gray-400">Calories</label>
                            <input type="number" value={cals} onChange={e => setCals(e.target.value)} className="w-full bg-black/20 border border-white/10 rounded-lg p-2" required />
                        </div>
                    </div>
                    <button className="w-full bg-purple-600 py-3 rounded-lg font-bold mt-4">Log Workout</button>
                    <button type="button" onClick={onClose} className="w-full mt-2 text-sm text-gray-400">Cancel</button>
                </form>
            </motion.div>
        </div>
    );
}
