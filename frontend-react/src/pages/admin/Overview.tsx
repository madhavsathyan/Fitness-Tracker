import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
    Users, TrendingUp, Activity, Calendar,
    Zap, Droplets, Moon, Dumbbell
} from 'lucide-react';
import { adminApi } from '../../services/api';
import AreaTrendChart from '../../components/charts/AreaTrendChart';
import WeeklyBarChart from '../../components/charts/WeeklyBarChart';
import DonutChart from '../../components/charts/DonutChart';
import ActivityHeatmap from '../../components/charts/ActivityHeatmap';
import RadarOverview from '../../components/charts/RadarOverview';
import StatCardSparkline from '../../components/charts/StatCardSparkline';
import BackButton from '../../components/BackButton';

// Animation variants
const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: { staggerChildren: 0.1 }
    }
};

const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
};

// Admin Stat Card
function AdminStatCard({ icon: Icon, label, value, trend, trendLabel, color, data }: any) {
    return (
        <motion.div
            variants={itemVariants}
            className="glass-card p-6 relative overflow-hidden group"
        >
            <div className={`absolute -right-6 -top-6 p-8 rounded-full ${color} opacity-10 group-hover:opacity-20 transition-opacity`}>
                <Icon size={64} />
            </div>

            <div className="flex justify-between items-start mb-4 relative z-10">
                <div>
                    <p className="text-gray-400 text-sm font-medium">{label}</p>
                    <h3 className="text-3xl font-bold mt-1">{value}</h3>
                </div>
                <div className={`p-2 rounded-lg ${color} bg-opacity-20 text-white`}>
                    <Icon size={20} />
                </div>
            </div>

            <div className="h-12 mb-3">
                <StatCardSparkline data={data || [10, 15, 12, 20, 18, 25, 22]} color="#ffffff" height={40} />
            </div>

            <div className="flex items-center gap-2 text-sm">
                <span className={`font-bold ${trend >= 0 ? 'text-green-400' : 'text-red-400'} flex items-center`}>
                    {trend >= 0 ? '+' : ''}{trend}%
                    <TrendingUp size={14} className={`ml-1 ${trend < 0 ? 'rotate-180' : ''}`} />
                </span>
                <span className="text-gray-500">{trendLabel}</span>
            </div>
        </motion.div>
    );
}

export default function AdminOverview() {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchCharts = async () => {
            try {
                const response = await adminApi.getAdminOverviewCharts();
                setData(response);
            } catch (error) {
                console.error("Failed to load admin charts", error);
            } finally {
                setLoading(false);
            }
        };
        fetchCharts();
    }, []);

    if (loading) return <div className="p-8 text-center text-gray-400">Loading analytics...</div>;
    if (!data) return <div className="p-8 text-center text-red-400">Failed to load data</div>;

    return (
        <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="space-y-6"
        >
            <BackButton to="/admin" label="Back to Admin" />
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold gradient-text">Platform Overview</h1>
                    <p className="text-gray-400">Real-time platform performance and user statistics</p>
                </div>
                <div className="flex gap-2">
                    <button className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm hover:bg-white/10 transition-colors">Last 7 Days</button>
                    <button className="px-4 py-2 bg-indigo-600/20 border border-indigo-500/50 text-indigo-400 rounded-lg text-sm">Last 30 Days</button>
                    <button className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm hover:bg-white/10 transition-colors">All Time</button>
                </div>
            </div>

            {/* Key Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <AdminStatCard
                    icon={Users}
                    label="Total Users"
                    value={data.key_stats.total_users.toLocaleString()}
                    trend={12.5}
                    trendLabel="vs last month"
                    color="bg-blue-500"
                    data={data.key_stats.sparklines.users}
                />
                <AdminStatCard
                    icon={Activity}
                    label="Active Today"
                    value={data.key_stats.active_today.toLocaleString()}
                    trend={5.2}
                    trendLabel="vs yesterday"
                    color="bg-green-500"
                    data={data.key_stats.sparklines.active}
                />
                <AdminStatCard
                    icon={Dumbbell}
                    label="Workouts Logged"
                    value={data.key_stats.total_workouts.toLocaleString()}
                    trend={8.1}
                    trendLabel="vs last week"
                    color="bg-purple-500"
                    data={data.key_stats.sparklines.workouts}
                />
                <AdminStatCard
                    icon={Zap}
                    label="System Health"
                    value="99.9%"
                    trend={0}
                    trendLabel="Uptime"
                    color="bg-orange-500"
                    data={[98, 99, 99, 98, 99, 99, 100]}
                />
            </div>

            {/* Main Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* User Growth Area Chart */}
                <motion.div variants={itemVariants} className="glass-card p-6 lg:col-span-2">
                    <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                        <Users size={20} className="text-blue-400" />
                        User Growth History
                    </h3>
                    <div className="h-80">
                        <AreaTrendChart
                            data={data.user_growth}
                            dataKey="users"
                            color="#3b82f6"
                            height={320}
                            gradientId="userGrowth"
                        />
                    </div>
                </motion.div>

                {/* Demographics Bar Chart */}
                <motion.div variants={itemVariants} className="glass-card p-6">
                    <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                        <Users size={20} className="text-pink-400" />
                        Age Distribution
                    </h3>
                    <div className="h-80">
                        <WeeklyBarChart
                            data={data.age_distribution}
                            dataKey="count"
                            color="#ec4899"
                            height={320}
                        />
                    </div>
                </motion.div>
            </div>

            {/* Platform Activity Heatmap */}
            <motion.div variants={itemVariants} className="glass-card p-6">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-lg font-bold flex items-center gap-2">
                        <Calendar size={20} className="text-indigo-400" />
                        Platform Activity Heatmap
                    </h3>
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                        <span>Less</span>
                        <div className="w-2 h-2 rounded-sm bg-indigo-500/30"></div>
                        <div className="w-2 h-2 rounded-sm bg-indigo-500/60"></div>
                        <div className="w-2 h-2 rounded-sm bg-indigo-500"></div>
                        <span>More</span>
                    </div>
                </div>
                {/* Heatmap Component */}
                <ActivityHeatmap data={data.heatmap} />
            </motion.div>

            {/* Breakdown Charts */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Workout Types Donut */}
                <motion.div variants={itemVariants} className="glass-card p-6">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <Dumbbell size={20} className="text-purple-400" />
                        Popular Workouts
                    </h3>
                    <div className="h-64">
                        <DonutChart
                            data={data.workout_types}
                            colors={['#8b5cf6', '#ec4899', '#3b82f6', '#10b981', '#f59e0b']}
                            height={250}
                        />
                    </div>
                </motion.div>

                {/* Calorie Distribution Donut */}
                <motion.div variants={itemVariants} className="glass-card p-6">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <Activity size={20} className="text-orange-400" />
                        Meal Consumption
                    </h3>
                    <div className="h-64">
                        <DonutChart
                            data={data.calories_by_meal}
                            colors={['#f97316', '#eab308', '#22c55e', '#ef4444']}
                            height={250}
                        />
                    </div>
                </motion.div>

                {/* Goal Achievement Radar */}
                <motion.div variants={itemVariants} className="glass-card p-6">
                    <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <TrendingUp size={20} className="text-green-400" />
                        Avg. Goal Achievement
                    </h3>
                    <div className="h-64">
                        <RadarOverview
                            data={data.averages}
                        />
                    </div>
                    <p className="text-center text-sm text-gray-400 mt-2">Platform average across all users</p>
                </motion.div>
            </div>
        </motion.div>
    );
}
