import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Plot from 'react-plotly.js';
import { ArrowLeft, Activity, Calendar, Droplets, Moon, Utensils, TrendingUp } from 'lucide-react';
import toast from 'react-hot-toast';
import { adminApi } from '../../services/api';
import AdminHeader from '../../components/AdminHeader';

export default function UserActivity() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<any>(null);

    useEffect(() => {
        if (id) loadData();
    }, [id]);

    const loadData = async () => {
        try {
            const activityData = await adminApi.getUserActivity(Number(id));
            setData(activityData);
        } catch (error) {
            toast.error('Failed to load user activity');
            navigate('/admin/users');
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-400">Loading user activity...</div>;
    if (!data) return null;

    const { stats, charts } = data;

    // Common layout for plots
    const plotLayout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#9ca3af' },
        margin: { t: 10, r: 10, l: 40, b: 30 },
        height: 250,
        xaxis: { showgrid: false },
        yaxis: { showgrid: true, gridcolor: 'rgba(255,255,255,0.1)' }
    };

    return (
        <div className="min-h-screen bg-mesh-gradient noise-overlay py-8 px-4 md:px-8">
            <div className="max-w-7xl mx-auto">
                <AdminHeader
                    title="User Activity"
                    description={`Detailed activity report for User #${id}`}
                >
                    <button
                        onClick={() => navigate('/admin/users')}
                        className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors text-sm font-medium"
                    >
                        ← Back to Users
                    </button>
                </AdminHeader>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    <div className="glass-card p-4">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-2 bg-indigo-500/20 rounded-lg text-indigo-400"><Activity size={20} /></div>
                            <span className="text-gray-400 text-xs font-semibold uppercase">Total Workouts</span>
                        </div>
                        <div className="text-2xl font-bold">{stats.total_workouts}</div>
                    </div>
                    <div className="glass-card p-4">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-2 bg-orange-500/20 rounded-lg text-orange-400"><Utensils size={20} /></div>
                            <span className="text-gray-400 text-xs font-semibold uppercase">Total Meals</span>
                        </div>
                        <div className="text-2xl font-bold">{stats.total_meals}</div>
                    </div>
                    <div className="glass-card p-4">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400"><Droplets size={20} /></div>
                            <span className="text-gray-400 text-xs font-semibold uppercase">Total Water</span>
                        </div>
                        <div className="text-2xl font-bold">{stats.total_water_ml}<span className="text-sm font-medium text-gray-500 ml-1">ml</span></div>
                    </div>
                    <div className="glass-card p-4">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-2 bg-purple-500/20 rounded-lg text-purple-400"><Moon size={20} /></div>
                            <span className="text-gray-400 text-xs font-semibold uppercase">Avg Sleep</span>
                        </div>
                        <div className="text-2xl font-bold">{stats.avg_sleep_hours}<span className="text-sm font-medium text-gray-500 ml-1">hrs</span></div>
                    </div>
                </div>

                {/* Charts Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    {/* Workout History */}
                    <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <TrendingUp size={18} className="text-indigo-400" /> Workout History (7 Days)
                        </h3>
                        <div className="w-full">
                            <Plot
                                data={[{
                                    y: charts.workouts,
                                    type: 'scatter',
                                    mode: 'lines+markers',
                                    line: { shape: 'spline', color: '#818cf8', width: 3 },
                                    marker: { color: '#6366f1', size: 6 }
                                }]}
                                layout={plotLayout}
                                config={{ displayModeBar: false, responsive: true }}
                                style={{ width: '100%', height: '250px' }}
                            />
                        </div>
                    </div>

                    {/* Calorie Intake */}
                    <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <Utensils size={18} className="text-orange-400" /> Calorie Intake
                        </h3>
                        <div className="w-full">
                            <Plot
                                data={[{
                                    y: charts.calories,
                                    type: 'bar',
                                    marker: { color: '#fb923c', opacity: 0.8 }
                                }]}
                                layout={plotLayout}
                                config={{ displayModeBar: false, responsive: true }}
                                style={{ width: '100%', height: '250px' }}
                            />
                        </div>
                    </div>

                    {/* Sleep Pattern */}
                    <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <Moon size={18} className="text-purple-400" /> Sleep Pattern
                        </h3>
                        <div className="w-full">
                            <Plot
                                data={[{
                                    y: charts.sleep,
                                    type: 'scatter',
                                    fill: 'tozeroy',
                                    fillcolor: 'rgba(168, 85, 247, 0.2)',
                                    line: { color: '#a855f7' }
                                }]}
                                layout={plotLayout}
                                config={{ displayModeBar: false, responsive: true }}
                                style={{ width: '100%', height: '250px' }}
                            />
                        </div>
                    </div>

                    {/* Weight Progress */}
                    <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <Activity size={18} className="text-emerald-400" /> Weight Progress
                        </h3>
                        <div className="w-full">
                            <Plot
                                data={[{
                                    y: charts.weight,
                                    type: 'scatter',
                                    mode: 'lines',
                                    line: { color: '#34d399', width: 3 }
                                }]}
                                layout={plotLayout}
                                config={{ displayModeBar: false, responsive: true }}
                                style={{ width: '100%', height: '250px' }}
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
