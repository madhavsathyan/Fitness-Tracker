import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Target, Plus, Check, Edit2, Trash2 } from 'lucide-react';
import { goalsApi } from '../services/api';
import { useAuthStore } from '../store/authStore';
import { useData } from '../context/DataContext';
import BackButton from '../components/BackButton';
import HamburgerMenu from '../components/HamburgerMenu';
import ConfirmationModal from '../components/ConfirmationModal';
import toast from 'react-hot-toast';
import { getLocalDateString } from '../utils/dateUtils';

export default function Goals() {
    const { user } = useAuthStore();
    const { triggerRefresh } = useData();
    const [goals, setGoals] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [deleteId, setDeleteId] = useState<number | null>(null);

    const fetchGoals = async () => {
        try {
            const data = await goalsApi.getAll({ user_id: user?.id, is_active: true });
            setGoals(data);
        } catch (error) {
            console.error("Failed to fetch goals", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (user) fetchGoals();
    }, [user]);

    const confirmDelete = async () => {
        if (!deleteId) return;
        try {
            await goalsApi.delete(deleteId);
            toast.success("Goal deleted");
            fetchGoals();
            triggerRefresh(); // Trigger dashboard refresh
        } catch (error) {
            toast.error("Failed to delete goal");
        }
        setDeleteId(null);
    };

    const groupedGoals = {
        daily: goals.filter(g => g.goal_type === 'daily'),
        weekly: goals.filter(g => g.goal_type === 'weekly'),
        monthly: goals.filter(g => g.goal_type === 'monthly'),
        yearly: goals.filter(g => g.goal_type === 'yearly'),
    };

    if (loading) return <div className="p-8 text-center text-gray-400">Loading goals...</div>;

    return (
        <div className="min-h-screen px-4 sm:px-6 lg:px-8 py-6 pb-20">
            <HamburgerMenu />
            <div className="max-w-7xl mx-auto space-y-6">
                <BackButton to="/dashboard" label="Back to Dashboard" />
                <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div>
                        <h1 className="text-2xl font-bold gradient-text flex items-center gap-2">
                            <Target className="text-red-400" /> My Goals
                        </h1>
                        <p className="text-gray-400 text-sm">Set targets, smash them.</p>
                    </div>
                    <button
                        onClick={() => setShowModal(true)}
                        className="bg-white/10 hover:bg-white/20 border border-white/10 px-4 py-2 rounded-lg text-sm transition-colors"
                    >
                        + Set New Goal
                    </button>
                </header>

                {/* Goal Sections */}
                {['daily', 'weekly', 'monthly', 'yearly'].map((type) => {
                    const typeGoals = groupedGoals[type as keyof typeof groupedGoals];
                    if (typeGoals.length === 0) return null;

                    return (
                        <div key={type} className="space-y-3">
                            <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">{type} Goals</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {typeGoals.map((goal) => (
                                    <div key={goal.id} className="glass-card p-4 flex justify-between items-center group">
                                        <div className="flex items-center gap-4">
                                            <div className="p-3 bg-white/5 rounded-lg text-2xl">
                                                {goal.category === 'water' ? '💧' :
                                                    goal.category === 'calories' ? '🍎' :
                                                        goal.category === 'workout' ? '🏋️' :
                                                            goal.category === 'sleep' ? '😴' : '⚖️'}
                                            </div>
                                            <div>
                                                <div className="font-bold capitalize">{goal.category}</div>
                                                <div className="text-sm text-gray-400">Target: {goal.target_value} {goal.unit}</div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            {/* Progress bar placeholder - fully functional progress requires calculating current values from logs, which is complex. Showing static target for now as per "Part 2" layout */}
                                            <button
                                                onClick={() => setDeleteId(goal.id)}
                                                className="p-2 hover:bg-red-500/20 text-gray-500 hover:text-red-400 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                                            >
                                                <Trash2 size={16} />
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    );
                })}

                {goals.length === 0 && (
                    <div className="text-center py-12 glass-card">
                        <Target size={48} className="mx-auto text-gray-600 mb-4" />
                        <h3 className="text-xl font-bold mb-2">No Goals Set</h3>
                        <p className="text-gray-400 mb-6">Start your journey by setting a daily goal.</p>
                        <button
                            onClick={() => setShowModal(true)}
                            className="bg-indigo-600 px-6 py-2 rounded-lg font-bold"
                        >
                            Set Goal
                        </button>
                    </div>
                )}

                <SetGoalModal
                    isOpen={showModal}
                    onClose={() => setShowModal(false)}
                    onAdd={() => { fetchGoals(); setShowModal(false); }}
                />

                <ConfirmationModal
                    isOpen={!!deleteId}
                    onClose={() => setDeleteId(null)}
                    onConfirm={confirmDelete}
                    title="Delete Goal"
                    message="Are you sure you want to delete this goal?"
                    confirmLabel="Delete"
                    isDangerous={true}
                />
            </div>
        </div>
    );
}

function SetGoalModal({ isOpen, onClose, onAdd }: any) {
    const { user } = useAuthStore();
    const [category, setCategory] = useState('water');
    const [type, setType] = useState('daily');
    const [target, setTarget] = useState('');
    const [unit, setUnit] = useState('ml');

    const units: any = { water: 'ml', calories: 'kcal', workout: 'min', sleep: 'hours', weight: 'kg' };

    useEffect(() => {
        setUnit(units[category] || '');
    }, [category]);

    const handleSubmit = async (e: any) => {
        e.preventDefault();
        try {
            await goalsApi.create({
                user_id: user?.id,
                category,
                goal_type: type,
                target_value: parseFloat(target),
                unit,
                start_date: getLocalDateString(),
                is_active: true
            });
            toast.success("Goal set!");
            onAdd();
        } catch (e) { toast.error("Failed to set goal"); }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} className="glass-card p-6 w-full max-w-md">
                <h2 className="text-xl font-bold mb-6">Set New Goal</h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="text-sm text-gray-400">Category</label>
                        <div className="grid grid-cols-5 gap-2 mt-1">
                            {['water', 'calories', 'workout', 'sleep', 'weight'].map(c => (
                                <button
                                    key={c} type="button"
                                    onClick={() => setCategory(c)}
                                    className={`p-2 rounded-lg text-2xl transition-colors ${category === c ? 'bg-indigo-600' : 'bg-white/5 hover:bg-white/10'}`}
                                >
                                    {c === 'water' ? '💧' : c === 'calories' ? '🍎' : c === 'workout' ? '🏋️' : c === 'sleep' ? '😴' : '⚖️'}
                                </button>
                            ))}
                        </div>
                        <div className="text-center text-sm mt-1 capitalize text-indigo-400">{category}</div>
                    </div>

                    <div>
                        <label className="text-sm text-gray-400">Frequency</label>
                        <select value={type} onChange={e => setType(e.target.value)} className="w-full bg-black/20 border border-white/10 rounded-lg p-2 mt-1">
                            <option value="daily">Daily</option>
                            <option value="weekly">Weekly</option>
                            <option value="monthly">Monthly</option>
                            <option value="yearly">Yearly</option>
                        </select>
                    </div>

                    <div>
                        <label className="text-sm text-gray-400">Target Value</label>
                        <div className="flex gap-2">
                            <input type="number" value={target} onChange={e => setTarget(e.target.value)} className="flex-1 bg-black/20 border border-white/10 rounded-lg p-2" required placeholder="e.g. 3000" />
                            <div className="bg-white/5 px-4 py-2 rounded-lg flex items-center text-gray-400">{unit}</div>
                        </div>
                    </div>

                    <button className="w-full bg-indigo-600 py-3 rounded-lg font-bold mt-4">Save Goal</button>
                    <button type="button" onClick={onClose} className="w-full mt-2 text-sm text-gray-400">Cancel</button>
                </form>
            </motion.div>
        </div>
    );
}
