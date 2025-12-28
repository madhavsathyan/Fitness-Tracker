import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis } from 'recharts';

interface WeeklyBarProps {
    data: any[];
    dataKey: string;
    color: string;
    height?: number;
}

export default function WeeklyBarChart({ data, dataKey, color, height = 200 }: WeeklyBarProps) {
    return (
        <div style={{ width: '100%', height }}>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.1)" />
                    <XAxis
                        dataKey="day"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: '#9ca3af', fontSize: 12 }}
                    />
                    <Tooltip
                        cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                        contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                        itemStyle={{ color: '#fff' }}
                    />
                    <Bar
                        dataKey={dataKey}
                        fill={color}
                        radius={[4, 4, 0, 0]}
                        barSize={30}
                    />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
