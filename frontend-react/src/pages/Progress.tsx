import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
    TrendingUp, Scale, Flame, Dumbbell, Moon, Droplets,
    Calendar, ChevronLeft, ChevronRight, Activity
} from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { waterApi, workoutApi, sleepApi, nutritionApi } from '../services/api';
import { getLocalDateString, getLocalDateStringDaysAgo } from '../utils/dateUtils';
import BackButton from '../components/BackButton';

// Charts
import {
    LineChart, Line, AreaChart, Area, BarChart, Bar,
    XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, CartesianGrid
} from 'recharts';

export default function Progress() {
    const { user } = useAuthStore();
    const [period, setPeriod] = useState(7);
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<any>({
        water: [],
        workouts: [],
        sleep: [],
        calories: [],
        summary: {}
    });

    // Generate activity calendar data
    const generateCalendarData = () => {
        const today = new Date();
        const data = [];
        for (let i = 29; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            data.push({
                date: date.toISOString().split('T')[0],
                day: date.getDate(),
                active: Math.random() > 0.3, // Mock - would come from real data
                isToday: i === 0
            });
        }
        return data;
    };

    const [calendar, setCalendar] = useState(generateCalendarData());

    useEffect(() => {
        const fetchData = async () => {
            if (!user?.id) return;
            setLoading(true);
            try {
                const [waterRes, workoutRes, sleepRes, nutritionRes] = await Promise.all([
                    waterApi.getWeekly(user.id),
                    workoutApi.getWeekly(user.id),
                    sleepApi.getWeekly(user.id),
                    nutritionApi.getWeekly(user.id)
                ]);

                // Calculate summary stats
                const totalWater = waterRes?.reduce((sum: number, d: any) => sum + (d.amount || 0), 0) || 0;
                const totalWorkouts = workoutRes?.filter((d: any) => d.duration > 0).length || 0;
                const avgSleep = sleepRes?.length > 0
                    ? sleepRes.reduce((sum: number, d: any) => sum + (d.hours || 0), 0) / sleepRes.length
                    : 0;
                const totalCalories = nutritionRes?.reduce((sum: number, d: any) => sum + (d.calories || 0), 0) || 0;

                setData({
                    water: waterRes || [],
                    workouts: workoutRes || [],
                    sleep: sleepRes || [],
                    calories: nutritionRes || [],
                    summary: {
                        totalWater,
                        totalWorkouts,
                        avgSleep,
                        totalCalories,
                        weightChange: -1.2 // Mock for now
                    }
                });
            } catch (error) {
                console.error('Failed to fetch progress data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [user?.id, period]);

    const periodButtons = [
        { label: '7D', value: 7 },
        { label: '30D', value: 30 },
        { label: '90D', value: 90 },
        { label: '1Y', value: 365 },
    ];

    if (loading) {
        return (
            <div className="p-8 text-center">
                <div className="animate-spin w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full mx-auto"></div>
                <p className="text-gray-400 mt-4">Loading progress data...</p>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 py-8 pb-20">
            <BackButton to="/dashboard" label="Back to Dashboard" />
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-3xl font-bold gradient-text flex items-center gap-3">
                        <TrendingUp className="text-green-400" /> My Progress
                    </h1>
                    <p className="text-gray-400 mt-1">Track your long-term health and fitness journey</p>
                </div>
                <div className="flex gap-2">
                    {periodButtons.map((btn) => (
                        <button
                            key={btn.value}
                            onClick={() => setPeriod(btn.value)}
                            className={`px-4 py-2 rounded-lg font-medium transition-colors ${period === btn.value
                                ? 'bg-indigo-500 text-white'
                                : 'bg-white/10 text-gray-400 hover:bg-white/20'
                                }`}
                        >
                            {btn.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="glass-card p-5">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-blue-500/20 rounded-lg"><Scale size={20} className="text-blue-400" /></div>
                        <span className="text-gray-400 text-sm">Weight</span>
                    </div>
                    <div className="text-2xl font-bold">{user?.weight_kg || 70} kg</div>
                    <div className={`text-sm ${data.summary.weightChange < 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {data.summary.weightChange < 0 ? '↓' : '↑'} {Math.abs(data.summary.weightChange)} kg
                    </div>
                </motion.div>

                <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.1 }} className="glass-card p-5">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-orange-500/20 rounded-lg"><Flame size={20} className="text-orange-400" /></div>
                        <span className="text-gray-400 text-sm">Calories</span>
                    </div>
                    <div className="text-2xl font-bold">{data.summary.totalCalories?.toLocaleString() || 0}</div>
                    <div className="text-sm text-gray-400">kcal consumed</div>
                </motion.div>

                <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.2 }} className="glass-card p-5">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-purple-500/20 rounded-lg"><Dumbbell size={20} className="text-purple-400" /></div>
                        <span className="text-gray-400 text-sm">Workouts</span>
                    </div>
                    <div className="text-2xl font-bold">{data.summary.totalWorkouts}</div>
                    <div className="text-sm text-gray-400">sessions completed</div>
                </motion.div>

                <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.3 }} className="glass-card p-5">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-indigo-500/20 rounded-lg"><Moon size={20} className="text-indigo-400" /></div>
                        <span className="text-gray-400 text-sm">Avg Sleep</span>
                    </div>
                    <div className="text-2xl font-bold">{data.summary.avgSleep?.toFixed(1) || 0} hrs</div>
                    <div className="text-sm text-gray-400">per night</div>
                </motion.div>
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* Calorie Trend */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-bold flex items-center gap-2 text-orange-400 mb-4">
                        <Flame size={20} /> Calorie Trend
                    </h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={data.calories}>
                                <defs>
                                    <linearGradient id="colorCalories" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                <XAxis dataKey="day" stroke="#888" />
                                <YAxis stroke="#888" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                                <Area type="monotone" dataKey="calories" stroke="#f97316" fill="url(#colorCalories)" strokeWidth={2} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Workout History */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-bold flex items-center gap-2 text-purple-400 mb-4">
                        <Dumbbell size={20} /> Workout History
                    </h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={data.workouts}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                <XAxis dataKey="day" stroke="#888" />
                                <YAxis stroke="#888" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                                <Bar dataKey="duration" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Sleep Pattern */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-bold flex items-center gap-2 text-indigo-400 mb-4">
                        <Moon size={20} /> Sleep Pattern
                    </h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={data.sleep}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                <XAxis dataKey="day" stroke="#888" />
                                <YAxis stroke="#888" domain={[0, 12]} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                                <Bar dataKey="hours" fill="#6366f1" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="flex justify-between text-sm text-gray-400 mt-2">
                        <span>Avg: {data.summary.avgSleep?.toFixed(1) || 0} hrs</span>
                        <span>Goal: 8 hrs</span>
                    </div>
                </div>

                {/* Water Intake */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-bold flex items-center gap-2 text-cyan-400 mb-4">
                        <Droplets size={20} /> Water Intake
                    </h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={data.water}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                <XAxis dataKey="day" stroke="#888" />
                                <YAxis stroke="#888" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                                    itemStyle={{ color: '#fff' }}
                                    formatter={(value: any) => [`${value} ml`, 'Amount']}
                                />
                                <Bar dataKey="amount" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="flex justify-between text-sm text-gray-400 mt-2">
                        <span>Total: {(data.summary.totalWater / 1000).toFixed(1)}L</span>
                        <span>Goal: 3L/day</span>
                    </div>
                </div>
            </div>

            {/* Activity Calendar */}
            <div className="glass-card p-6">
                <h3 className="text-lg font-bold flex items-center gap-2 mb-6">
                    <Calendar size={20} className="text-green-400" /> Activity Calendar
                </h3>
                <div className="mb-4">
                    <div className="text-sm text-gray-400 mb-2">December 2024</div>
                    <div className="grid grid-cols-7 gap-2 text-center text-xs text-gray-500 mb-2">
                        {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((d, i) => (
                            <div key={i}>{d}</div>
                        ))}
                    </div>
                    <div className="grid grid-cols-7 gap-2">
                        {calendar.map((day, i) => (
                            <div
                                key={i}
                                className={`aspect-square rounded-lg flex items-center justify-center text-xs font-medium transition-colors ${day.isToday
                                    ? 'bg-green-500 text-white ring-2 ring-green-400'
                                    : day.active
                                        ? 'bg-green-500/30 text-green-400 hover:bg-green-500/40'
                                        : 'bg-white/5 text-gray-500 hover:bg-white/10'
                                    }`}
                            >
                                {day.day}
                            </div>
                        ))}
                    </div>
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-400">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded bg-green-500/30" /> Active Day
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded bg-green-500" /> Today
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded bg-white/5" /> Rest Day
                    </div>
                </div>
                <div className="mt-4 text-sm">
                    <span className="text-green-400 font-bold">{calendar.filter(d => d.active).length}</span>
                    <span className="text-gray-400"> / {calendar.length} active days this month</span>
                </div>
            </div>
        </div>
    );
}
