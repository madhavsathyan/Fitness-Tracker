import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Apple, Plus, Trash2, Edit2, Flame } from 'lucide-react';
import { nutritionApi, dashboardApi } from '../services/api';
import { useAuthStore } from '../store/authStore';
import { useData } from '../context/DataContext';
import AreaTrendChart from '../components/charts/AreaTrendChart';
import DonutChart from '../components/charts/DonutChart';
import BackButton from '../components/BackButton';
import HamburgerMenu from '../components/HamburgerMenu';
import ConfirmationModal from '../components/ConfirmationModal';
import toast from 'react-hot-toast';
import { getLocalDateString } from '../utils/dateUtils';

// Macros Progress Bar
function MacroBar({ label, current, target, color }: any) {
    const percent = Math.min(100, Math.round((current / target) * 100));
    return (
        <div className="space-y-1">
            <div className="flex justify-between text-xs text-gray-400">
                <span>{label}</span>
                <span>{current}/{target}g</span>
            </div>
            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${percent}%` }}
                    className={`h-full ${color}`}
                />
            </div>
        </div>
    );
}

export default function Nutrition() {
    const { user } = useAuthStore();
    const { triggerRefresh } = useData();
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<any>(null);
    const [chartData, setChartData] = useState<any>(null);
    const [showAddModal, setShowAddModal] = useState(false);
    const [activeMealType, setActiveMealType] = useState('breakfast');
    const [deleteId, setDeleteId] = useState<number | null>(null);

    // Fetch Data
    const fetchData = async () => {
        try {
            const today = getLocalDateString();
            const [dailyRes, weeklyRes] = await Promise.all([
                nutritionApi.getDailySummary(today, user?.id),
                nutritionApi.getWeekly(user?.id)
            ]);
            setData(dailyRes);
            setChartData({ weekly_trend: weeklyRes }); // AreaChart expects an object with specific key if logic persists, or we can just pass weeklyRes if tailored
        } catch (error) {
            console.error("Failed to load nutrition data", error);
            toast.error("Failed to load data");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (user) fetchData();
    }, [user]);

    // Handle Delete Meal
    const confirmDelete = async () => {
        if (!deleteId) return;
        try {
            await nutritionApi.delete(deleteId);
            toast.success("Meal deleted");
            fetchData();
            triggerRefresh(); // Trigger dashboard refresh
        } catch (error) {
            toast.error("Failed to delete meal");
        }
        setDeleteId(null);
    };

    if (loading) return <div className="p-8 text-center text-gray-400">Loading nutrition data...</div>;

    const calorieGoal = user?.daily_calorie_goal || 2000;
    const currentCals = data?.total_calories || 0;
    const remaining = calorieGoal - currentCals;
    const progress = Math.min(100, Math.round((currentCals / calorieGoal) * 100));

    // Group meals by type - Ensure all keys exist to prevent crashes
    const rawMeals = data?.meals_by_type || {};
    const mealsByType: any = {
        breakfast: rawMeals.breakfast || [],
        lunch: rawMeals.lunch || [],
        dinner: rawMeals.dinner || [],
        snack: rawMeals.snack || []
    };


    return (
        <div className="min-h-screen px-4 sm:px-6 lg:px-8 py-6 pb-20">
            <HamburgerMenu />
            <div className="max-w-7xl mx-auto space-y-6">
                <BackButton to="/dashboard" label="Back to Dashboard" />
                {/* Header */}
                <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div>
                        <h1 className="text-2xl font-bold gradient-text flex items-center gap-2">
                            <Apple className="text-orange-400" /> Nutrition Tracker
                        </h1>
                        <p className="text-gray-400 text-sm">Fuel your body right.</p>
                    </div>
                    <div className="text-right">
                        <p className="text-xs text-gray-500 uppercase tracking-wider">Goal</p>
                        <p className="text-xl font-bold text-orange-400">{calorieGoal} kcal</p>
                    </div>
                </header>

                {/* Main Stats Card */}
                <div className="glass-card p-6">
                    <div className="flex flex-col md:flex-row gap-8 items-center">
                        {/* Calorie Progress */}
                        <div className="flex-1 w-full space-y-4">
                            <div className="flex justify-between items-end">
                                <div>
                                    <div className="text-3xl font-bold">{currentCals}</div>
                                    <div className="text-sm text-gray-400">eaten</div>
                                </div>
                                <div className="text-right">
                                    <div className="text-xl font-bold text-gray-300">{remaining}</div>
                                    <div className="text-sm text-gray-400">remaining</div>
                                </div>
                            </div>
                            <div className="h-4 bg-white/10 rounded-full overflow-hidden relative">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${progress}%` }}
                                    className={`h-full ${progress > 100 ? 'bg-red-500' : 'bg-gradient-to-r from-orange-500 to-yellow-500'}`}
                                />
                            </div>
                        </div>

                        {/* Macros */}
                        <div className="w-full md:w-1/2 grid grid-cols-3 gap-4">
                            <MacroBar label="Protein" current={data?.total_protein || 0} target={150} color="bg-blue-500" />
                            <MacroBar label="Carbs" current={data?.total_carbs || 0} target={250} color="bg-green-500" />
                            <MacroBar label="Fats" current={data?.total_fat || 0} target={65} color="bg-yellow-500" />
                        </div>
                    </div>
                </div>

                {/* Quick Add Buttons */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {['Breakfast', 'Lunch', 'Dinner', 'Snack'].map((type) => (
                        <button
                            key={type}
                            onClick={() => {
                                setActiveMealType(type.toLowerCase());
                                setShowAddModal(true);
                            }}
                            className="glass-card p-4 hover:bg-orange-500/10 border-orange-500/20 flex items-center justify-center gap-2 transition-colors"
                        >
                            <Plus size={18} className="text-orange-400" />
                            <span className="font-medium">Add {type}</span>
                        </button>
                    ))}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Meals List */}
                    <div className="lg:col-span-2 space-y-6">
                        {['breakfast', 'lunch', 'dinner', 'snack'].map((type) => (
                            <div key={type} className="glass-card p-6">
                                <div className="flex justify-between items-center mb-4">
                                    <h3 className="text-lg font-bold capitalize flex items-center gap-2">
                                        {type === 'breakfast' && '🌅'}
                                        {type === 'lunch' && '☀️'}
                                        {type === 'dinner' && '🌙'}
                                        {type === 'snack' && '🍪'}
                                        {type}
                                    </h3>
                                    <div className="text-sm font-bold text-gray-400">
                                        {mealsByType[type].reduce((acc: number, m: any) => acc + m.calories, 0)} kcal
                                    </div>
                                </div>

                                {mealsByType[type].length === 0 ? (
                                    <div className="text-sm text-gray-600 italic">No food logged</div>
                                ) : (
                                    <div className="space-y-3">
                                        {mealsByType[type].map((meal: any) => (
                                            <div key={meal.id} className="flex justify-between items-center p-3 bg-white/5 rounded-lg group hover:bg-white/10 transition-colors">
                                                <div>
                                                    <div className="font-medium">{meal.meal_name}</div>
                                                    <div className="text-xs text-gray-500">
                                                        {meal.protein_g}p • {meal.carbs_g}c • {meal.fat_g}f
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-3">
                                                    <span className="font-bold">{meal.calories}</span>
                                                    <button
                                                        onClick={() => setDeleteId(meal.id)}
                                                        className="p-1 text-gray-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                                                    >
                                                        <Trash2 size={14} />
                                                    </button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>

                    {/* Charts */}
                    <div className="space-y-6">
                        <div className="glass-card p-6">
                            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                                <Flame size={18} className="text-orange-400" /> Weekly Trend
                            </h3>
                            <div className="h-48">
                                <AreaTrendChart
                                    data={chartData?.weekly_trend || []}
                                    dataKey="calories"
                                    color="#f97316"
                                    height={180}
                                    gradientId="nutWeekly"
                                />
                            </div>
                        </div>
                    </div>
                </div>

                <AddMealModal
                    isOpen={showAddModal}
                    onClose={() => setShowAddModal(false)}
                    type={activeMealType}
                    onAdd={() => {
                        fetchData();
                        setShowAddModal(false);
                    }}
                />

                <ConfirmationModal
                    isOpen={!!deleteId}
                    onClose={() => setDeleteId(null)}
                    onConfirm={confirmDelete}
                    title="Delete Meal"
                    message="Are you sure you want to delete this meal?"
                    confirmLabel="Delete"
                    isDangerous={true}
                />
            </div>
        </div>
    );
}

// Add Meal Modal Component
function AddMealModal({ isOpen, onClose, type, onAdd }: any) {
    const { user } = useAuthStore();
    const [name, setName] = useState('');
    const [cals, setCals] = useState('');
    const [protein, setProtein] = useState('');
    const [carbs, setCarbs] = useState('');
    const [fat, setFat] = useState('');

    const handleSubmit = async (e: any) => {
        e.preventDefault();
        try {
            await nutritionApi.create({
                user_id: user?.id,
                meal_type: type,
                meal_name: name,
                calories: parseFloat(cals),
                protein_g: parseFloat(protein) || 0,
                carbs_g: parseFloat(carbs) || 0,
                fat_g: parseFloat(fat) || 0,
                meal_date: getLocalDateString(),
                meal_time: new Date().toLocaleTimeString('en-GB')
            });
            toast.success("Meal added");
            setName(''); setCals(''); setProtein(''); setCarbs(''); setFat('');
            onAdd();
        } catch (error) {
            toast.error("Failed to add meal");
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="glass-card p-6 w-full max-w-md"
            >
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-bold capitalize">Add {type}</h2>
                    <button onClick={onClose}><Trash2 className="rotate-45" /></button>
                </div>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm text-gray-400 mb-1">Food Name</label>
                        <input value={name} onChange={e => setName(e.target.value)} required className="w-full bg-black/20 border border-white/10 rounded-lg p-2 focus:border-orange-500" placeholder="e.g. Oatmeal" />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm text-gray-400 mb-1">Calories</label>
                            <input type="number" value={cals} onChange={e => setCals(e.target.value)} required className="w-full bg-black/20 border border-white/10 rounded-lg p-2 focus:border-orange-500" />
                        </div>
                        <div>
                            <label className="block text-sm text-gray-400 mb-1">Protein (g)</label>
                            <input type="number" value={protein} onChange={e => setProtein(e.target.value)} className="w-full bg-black/20 border border-white/10 rounded-lg p-2 focus:border-orange-500" />
                        </div>
                        <div>
                            <label className="block text-sm text-gray-400 mb-1">Carbs (g)</label>
                            <input type="number" value={carbs} onChange={e => setCarbs(e.target.value)} className="w-full bg-black/20 border border-white/10 rounded-lg p-2 focus:border-orange-500" />
                        </div>
                        <div>
                            <label className="block text-sm text-gray-400 mb-1">Fat (g)</label>
                            <input type="number" value={fat} onChange={e => setFat(e.target.value)} className="w-full bg-black/20 border border-white/10 rounded-lg p-2 focus:border-orange-500" />
                        </div>
                    </div>
                    <button type="submit" className="w-full bg-orange-600 hover:bg-orange-500 py-3 rounded-lg font-bold mt-4">Log Meal</button>
                    <button type="button" onClick={onClose} className="w-full bg-white/5 hover:bg-white/10 py-2 rounded-lg text-sm text-gray-400">Cancel</button>
                </form>
            </motion.div>
        </div>
    );
}
