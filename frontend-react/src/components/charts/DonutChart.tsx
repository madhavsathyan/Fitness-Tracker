import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip, Legend } from 'recharts';

interface DonutChartProps {
    data: { name: string; value: number }[];
    colors: string[];
    height?: number;
    innerRadius?: number;
}

export default function DonutChart({ data, colors, height = 200, innerRadius = 35 }: DonutChartProps) {
    // If no data or all zeros, show empty state
    const hasData = data.length > 0 && data.some(d => d.value > 0);

    if (!hasData) {
        return (
            <div style={{ width: '100%', height }} className="flex items-center justify-center text-gray-500 text-sm">
                No data to display
            </div>
        );
    }

    return (
        <div style={{ width: '100%', height }}>
            <ResponsiveContainer width="100%" height="100%">
                <PieChart margin={{ top: 10, right: 10, bottom: 10, left: 10 }}>
                    <Pie
                        data={data}
                        cx="50%"
                        cy="45%"
                        innerRadius={innerRadius}
                        outerRadius={innerRadius + 22}
                        paddingAngle={3}
                        dataKey="value"
                        stroke="none"
                    >
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                        ))}
                    </Pie>
                    <Tooltip
                        contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                        itemStyle={{ color: '#fff' }}
                    />
                    <Legend
                        verticalAlign="bottom"
                        height={25}
                        iconType="circle"
                        iconSize={8}
                        formatter={(value) => <span style={{ color: '#9ca3af', fontSize: '11px' }}>{value}</span>}
                    />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
}
