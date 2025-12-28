import { PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer, Tooltip } from 'recharts';

interface RadarProps {
    data: any[];
}

export default function RadarOverview({ data }: RadarProps) {
    // Expected Data format: [{ subject: 'Math', A: 120, B: 110, fullMark: 150 }]
    // We'll adapt in parent to match this

    return (
        <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
                    <PolarGrid stroke="rgba(255,255,255,0.1)" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                    <Radar
                        name="This Week"
                        dataKey="value"
                        stroke="#8B5CF6"
                        strokeWidth={2}
                        fill="#8B5CF6"
                        fillOpacity={0.4}
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                        itemStyle={{ color: '#fff' }}
                    />
                </RadarChart>
            </ResponsiveContainer>
        </div>
    );
}
