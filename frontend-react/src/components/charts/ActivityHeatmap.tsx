interface HeatmapProps {
    data: { day: string; hour: string; value: number }[]; // Value 0-100
}

export default function ActivityHeatmap({ data }: HeatmapProps) {
    const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    const hours = Array.from({ length: 8 }, (_, i) => i * 3); // 0, 3, 6... 21

    // Helper to get color intensity
    const getColor = (value: number) => {
        if (value < 20) return 'bg-white/5';
        if (value < 50) return 'bg-indigo-500/30';
        if (value < 80) return 'bg-indigo-500/60';
        return 'bg-indigo-500';
    };

    return (
        <div className="w-full overflow-x-auto">
            <div className="min-w-[500px]">
                <div className="flex mb-2">
                    <div className="w-12"></div>
                    {days.map(day => (
                        <div key={day} className="flex-1 text-center text-xs text-gray-400 font-medium">{day}</div>
                    ))}
                </div>
                <div className="space-y-1">
                    {hours.map(hour => (
                        <div key={hour} className="flex items-center">
                            <div className="w-12 text-xs text-gray-500 text-right pr-2">{hour}:00</div>
                            {days.map(day => {
                                const entry = data.find(d => d.day === day && d.hour.startsWith(hour.toString().padStart(2, '0')));
                                const value = entry ? entry.value : 0;
                                return (
                                    <div key={`${day}-${hour}`} className="flex-1 px-0.5">
                                        <div
                                            className={`h-6 rounded hover:scale-105 transition-transform cursor-pointer ${getColor(value)}`}
                                            title={`${day} @ ${hour}:00 - Activity: ${value}%`} // Simple native tooltip
                                        />
                                    </div>
                                );
                            })}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
