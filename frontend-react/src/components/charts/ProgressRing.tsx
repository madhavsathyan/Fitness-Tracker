import { motion } from 'framer-motion';

interface ProgressRingProps {
    radius: number;
    stroke: number;
    progress: number; // 0-100
    color?: string;
}

export default function ProgressRing({ radius, stroke, progress, color = '#3b82f6' }: ProgressRingProps) {
    // Clamp progress between 0 and 100
    const clampedProgress = Math.min(100, Math.max(0, progress));
    const normalizedRadius = radius - stroke * 2;
    const circumference = normalizedRadius * 2 * Math.PI;
    const strokeDashoffset = circumference - (clampedProgress / 100) * circumference;

    return (
        <div className="relative flex items-center justify-center">
            <svg
                height={radius * 2}
                width={radius * 2}
                className="rotate-[-90deg]" // Start from top
            >
                {/* Background Ring */}
                <circle
                    stroke="rgba(255,255,255,0.1)"
                    strokeWidth={stroke}
                    fill="transparent"
                    r={normalizedRadius}
                    cx={radius}
                    cy={radius}
                />
                {/* Progress Ring - Only show if progress > 0 */}
                {clampedProgress > 0 && (
                    <motion.circle
                        stroke={color}
                        strokeWidth={stroke}
                        strokeDasharray={circumference + ' ' + circumference}
                        style={{ strokeDashoffset }}
                        strokeLinecap="round"
                        fill="transparent"
                        r={normalizedRadius}
                        cx={radius}
                        cy={radius}
                        initial={{ strokeDashoffset: circumference }}
                        animate={{ strokeDashoffset }}
                        transition={{ duration: 1.5, ease: "easeOut" }}
                    />
                )}
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center text-white">
                <span className="text-2xl font-bold">{Math.round(clampedProgress)}%</span>
                <span className="text-xs text-gray-400">Goal</span>
            </div>
        </div>
    );
}
