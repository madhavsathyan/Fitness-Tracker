/**
 * Register Page - 4-Step Wizard
 * Full registration flow with animations
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, ArrowRight, Loader2, Check, User, Mail, Lock, Ruler, Scale, Target } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { RegisterData } from '../services/api';
import confetti from 'canvas-confetti';

// Fitness goal options
const fitnessGoals = [
    { id: 'lose_weight', label: 'Lose Weight', emoji: '🏃', color: 'bg-blue-500/20 border-blue-500/50 hover:border-blue-400' },
    { id: 'build_muscle', label: 'Build Muscle', emoji: '💪', color: 'bg-purple-500/20 border-purple-500/50 hover:border-purple-400' },
    { id: 'maintain', label: 'Maintain Weight', emoji: '⚖️', color: 'bg-green-500/20 border-green-500/50 hover:border-green-400' },
    { id: 'endurance', label: 'Build Endurance', emoji: '🏃‍♂️', color: 'bg-orange-500/20 border-orange-500/50 hover:border-orange-400' },
];

const genderOptions = [
    { id: 'male', label: 'Male', emoji: '👨' },
    { id: 'female', label: 'Female', emoji: '👩' },
    { id: 'other', label: 'Other', emoji: '🧑' },
];

// Password strength checker
const checkPasswordStrength = (password: string): 'weak' | 'fair' | 'good' | 'strong' => {
    if (password.length === 0) return 'weak';
    let score = 0;
    if (password.length >= 8) score++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;

    if (score <= 1) return 'weak';
    if (score === 2) return 'fair';
    if (score === 3) return 'good';
    return 'strong';
};

export default function Register() {
    const navigate = useNavigate();
    const { register, isLoading, error, clearError } = useAuthStore();

    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState<RegisterData>({
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        age: undefined,
        gender: undefined,
        height_cm: 170,
        weight_kg: 70,
        fitness_goal: undefined,
    });
    const [confirmPassword, setConfirmPassword] = useState('');

    const updateField = (field: keyof RegisterData, value: any) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const nextStep = () => {
        if (step < 4) setStep(step + 1);
    };

    const prevStep = () => {
        if (step > 1) setStep(step - 1);
    };

    const handleSubmit = async () => {
        clearError();
        const success = await register(formData);
        if (success) {
            // Confetti celebration!
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 },
            });
            setTimeout(() => navigate('/login'), 2000);
        }
    };

    const slideVariants = {
        enter: (direction: number) => ({ x: direction > 0 ? 300 : -300, opacity: 0 }),
        center: { x: 0, opacity: 1 },
        exit: (direction: number) => ({ x: direction > 0 ? -300 : 300, opacity: 0 }),
    };

    return (
        <div className="min-h-screen bg-mesh-gradient noise-overlay relative overflow-hidden flex items-center justify-center px-4 py-8">
            {/* Gradient Orbs */}
            <div className="gradient-orb gradient-orb-indigo w-[400px] h-[400px] -top-20 -left-20" />
            <div className="gradient-orb gradient-orb-pink w-[300px] h-[300px] -bottom-10 -right-10" />

            {/* Register Card */}
            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                className="relative z-10 w-full max-w-lg"
            >
                <div className="glass-card p-8">
                    {/* Progress Steps */}
                    <div className="flex items-center justify-center gap-2 mb-8">
                        {[1, 2, 3, 4].map((s) => (
                            <div key={s} className="flex items-center">
                                <motion.div
                                    className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all ${s < step ? 'bg-green-500 text-white' :
                                        s === step ? 'bg-indigo-500 text-white shadow-glow' :
                                            'bg-white/10 text-gray-400'
                                        }`}
                                    animate={s === step ? { scale: [1, 1.1, 1] } : {}}
                                    transition={{ repeat: Infinity, duration: 2 }}
                                >
                                    {s < step ? <Check size={18} /> : s}
                                </motion.div>
                                {s < 4 && (
                                    <div className={`w-8 h-0.5 mx-1 ${s < step ? 'bg-green-500' : 'bg-white/10'}`} />
                                )}
                            </div>
                        ))}
                    </div>

                    {/* Step Content */}
                    <AnimatePresence mode="wait" custom={step}>
                        <motion.div
                            key={step}
                            custom={1}
                            variants={slideVariants}
                            initial="enter"
                            animate="center"
                            exit="exit"
                            transition={{ duration: 0.3 }}
                            className="min-h-[300px]"
                        >
                            {/* Step 1: Account */}
                            {step === 1 && (
                                <div className="space-y-4">
                                    <h2 className="text-xl font-bold text-center mb-6">Create Your Account</h2>

                                    <div className="grid grid-cols-2 gap-4">
                                        <input
                                            type="text"
                                            placeholder="First Name"
                                            value={formData.first_name || ''}
                                            onChange={(e) => updateField('first_name', e.target.value)}
                                            className="floating-input"
                                        />
                                        <input
                                            type="text"
                                            placeholder="Last Name"
                                            value={formData.last_name || ''}
                                            onChange={(e) => updateField('last_name', e.target.value)}
                                            className="floating-input"
                                        />
                                    </div>

                                    <input
                                        type="text"
                                        placeholder="Username"
                                        value={formData.username}
                                        onChange={(e) => updateField('username', e.target.value)}
                                        className="floating-input"
                                        required
                                    />

                                    <input
                                        type="email"
                                        placeholder="Email"
                                        value={formData.email}
                                        onChange={(e) => updateField('email', e.target.value)}
                                        className="floating-input"
                                        required
                                    />

                                    <div className="relative">
                                        <input
                                            type="password"
                                            placeholder="Password"
                                            value={formData.password}
                                            onChange={(e) => updateField('password', e.target.value)}
                                            className="floating-input"
                                            required
                                        />
                                        {/* Password Strength */}
                                        <AnimatePresence>
                                            {formData.password.length > 0 && (
                                                <motion.div
                                                    initial={{ opacity: 0, height: 0 }}
                                                    animate={{ opacity: 1, height: 'auto' }}
                                                    exit={{ opacity: 0, height: 0 }}
                                                    className={`strength-meter strength-${checkPasswordStrength(formData.password)} mt-2`}
                                                >
                                                    <div className="strength-segment" />
                                                    <div className="strength-segment" />
                                                    <div className="strength-segment" />
                                                    <div className="strength-segment" />
                                                </motion.div>
                                            )}
                                        </AnimatePresence>
                                    </div>

                                    <input
                                        type="password"
                                        placeholder="Confirm Password"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        className="floating-input"
                                        required
                                    />
                                </div>
                            )}

                            {/* Step 2: Profile */}
                            {step === 2 && (
                                <div className="space-y-6">
                                    <h2 className="text-xl font-bold text-center mb-6">Your Profile</h2>

                                    {/* Age */}
                                    <div>
                                        <label className="block text-sm text-gray-400 mb-2">Age</label>
                                        <input
                                            type="number"
                                            min="10"
                                            max="120"
                                            value={formData.age || ''}
                                            onChange={(e) => updateField('age', parseInt(e.target.value) || undefined)}
                                            className="floating-input"
                                            placeholder="Your age"
                                        />
                                    </div>

                                    {/* Gender Selection */}
                                    <div>
                                        <label className="block text-sm text-gray-400 mb-2">Gender</label>
                                        <div className="grid grid-cols-3 gap-3">
                                            {genderOptions.map((g) => (
                                                <motion.button
                                                    key={g.id}
                                                    type="button"
                                                    onClick={() => updateField('gender', g.id)}
                                                    whileTap={{ scale: 0.95 }}
                                                    className={`p-4 rounded-xl border text-center transition-all ${formData.gender === g.id
                                                        ? 'bg-indigo-500/20 border-indigo-500 shadow-glow-sm'
                                                        : 'bg-white/5 border-white/10 hover:border-white/30'
                                                        }`}
                                                >
                                                    <div className="text-2xl mb-1">{g.emoji}</div>
                                                    <div className="text-sm">{g.label}</div>
                                                </motion.button>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Height & Weight */}
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-sm text-gray-400 mb-2">Height (cm)</label>
                                            <input
                                                type="number"
                                                value={formData.height_cm || ''}
                                                onChange={(e) => updateField('height_cm', parseFloat(e.target.value) || undefined)}
                                                className="floating-input"
                                                placeholder="170"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm text-gray-400 mb-2">Weight (kg)</label>
                                            <input
                                                type="number"
                                                value={formData.weight_kg || ''}
                                                onChange={(e) => updateField('weight_kg', parseFloat(e.target.value) || undefined)}
                                                className="floating-input"
                                                placeholder="70"
                                            />
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Step 3: Fitness Goals */}
                            {step === 3 && (
                                <div className="space-y-4">
                                    <h2 className="text-xl font-bold text-center mb-6">Your Fitness Goal</h2>

                                    <div className="grid grid-cols-2 gap-4">
                                        {fitnessGoals.map((goal) => (
                                            <motion.button
                                                key={goal.id}
                                                type="button"
                                                onClick={() => updateField('fitness_goal', goal.id)}
                                                whileTap={{ scale: 0.95 }}
                                                whileHover={{ scale: 1.02 }}
                                                className={`p-6 rounded-xl border text-center transition-all relative ${formData.fitness_goal === goal.id
                                                    ? 'bg-indigo-500/20 border-indigo-500 shadow-glow'
                                                    : goal.color
                                                    }`}
                                            >
                                                {formData.fitness_goal === goal.id && (
                                                    <div className="absolute top-2 right-2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                                                        <Check size={14} />
                                                    </div>
                                                )}
                                                <div className="text-4xl mb-2">{goal.emoji}</div>
                                                <div className="font-semibold">{goal.label}</div>
                                            </motion.button>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Step 4: Confirmation */}
                            {step === 4 && (
                                <div className="space-y-4">
                                    <h2 className="text-xl font-bold text-center mb-6">Confirm Your Details</h2>

                                    {/* Account Info Section */}
                                    <div className="bg-white/5 rounded-xl p-4">
                                        <div className="flex justify-between items-center mb-3">
                                            <span className="text-sm text-indigo-400 font-medium">Account Info</span>
                                            <button
                                                type="button"
                                                onClick={() => setStep(1)}
                                                className="text-xs px-3 py-1 bg-indigo-500/20 text-indigo-400 rounded-lg hover:bg-indigo-500/30 transition-colors"
                                            >
                                                Edit
                                            </button>
                                        </div>
                                        <div className="space-y-2 text-sm">
                                            <div className="flex justify-between">
                                                <span className="text-gray-400">Username</span>
                                                <span className="font-semibold">{formData.username}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-gray-400">Email</span>
                                                <span className="font-semibold">{formData.email}</span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Profile Info Section */}
                                    <div className="bg-white/5 rounded-xl p-4">
                                        <div className="flex justify-between items-center mb-3">
                                            <span className="text-sm text-indigo-400 font-medium">Profile Info</span>
                                            <button
                                                type="button"
                                                onClick={() => setStep(2)}
                                                className="text-xs px-3 py-1 bg-indigo-500/20 text-indigo-400 rounded-lg hover:bg-indigo-500/30 transition-colors"
                                            >
                                                Edit
                                            </button>
                                        </div>
                                        <div className="space-y-2 text-sm">
                                            <div className="flex justify-between">
                                                <span className="text-gray-400">Age</span>
                                                <span className="font-semibold">{formData.age || 'Not set'}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-gray-400">Gender</span>
                                                <span className="font-semibold capitalize">{formData.gender || 'Not set'}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-gray-400">Height</span>
                                                <span className="font-semibold">{formData.height_cm} cm</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-gray-400">Weight</span>
                                                <span className="font-semibold">{formData.weight_kg} kg</span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Fitness Goal Section */}
                                    <div className="bg-white/5 rounded-xl p-4">
                                        <div className="flex justify-between items-center mb-3">
                                            <span className="text-sm text-indigo-400 font-medium">Fitness Goal</span>
                                            <button
                                                type="button"
                                                onClick={() => setStep(3)}
                                                className="text-xs px-3 py-1 bg-indigo-500/20 text-indigo-400 rounded-lg hover:bg-indigo-500/30 transition-colors"
                                            >
                                                Edit
                                            </button>
                                        </div>
                                        <div className="flex justify-between text-sm">
                                            <span className="text-gray-400">Goal</span>
                                            <span className="font-semibold capitalize">
                                                {fitnessGoals.find(g => g.id === formData.fitness_goal)?.emoji} {formData.fitness_goal?.replace('_', ' ') || 'Not set'}
                                            </span>
                                        </div>
                                    </div>

                                    {error && (
                                        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-center">
                                            {error}
                                        </div>
                                    )}
                                </div>
                            )}
                        </motion.div>
                    </AnimatePresence>

                    {/* Navigation Buttons */}
                    <div className="flex justify-between mt-8">
                        <button
                            type="button"
                            onClick={prevStep}
                            disabled={step === 1}
                            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${step === 1 ? 'opacity-30 cursor-not-allowed' : 'hover:bg-white/10'
                                }`}
                        >
                            <ArrowLeft size={18} />
                            Back
                        </button>

                        {step < 4 ? (
                            <button
                                type="button"
                                onClick={nextStep}
                                className="btn-gradient px-6 py-2 flex items-center gap-2"
                            >
                                Next
                                <ArrowRight size={18} />
                            </button>
                        ) : (
                            <button
                                type="button"
                                onClick={handleSubmit}
                                disabled={isLoading}
                                className="btn-gradient px-6 py-2 flex items-center gap-2"
                            >
                                {isLoading ? (
                                    <>
                                        <Loader2 className="animate-spin" size={18} />
                                        Creating...
                                    </>
                                ) : (
                                    <>
                                        Create Account
                                        <Check size={18} />
                                    </>
                                )}
                            </button>
                        )}
                    </div>

                    {/* Login Link */}
                    <div className="text-center mt-6 pt-6 border-t border-white/10">
                        <p className="text-gray-400">
                            Already have an account?{' '}
                            <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-semibold">
                                Sign in
                            </Link>
                        </p>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
