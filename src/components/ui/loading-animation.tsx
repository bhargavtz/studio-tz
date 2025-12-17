'use client';

import { motion } from 'framer-motion';
import { Sparkles, Code, Palette, Zap } from 'lucide-react';

interface LoadingAnimationProps {
    status?: string;
    className?: string;
}

export function LoadingAnimation({ status = 'Generating...', className = '' }: LoadingAnimationProps) {
    return (
        <div className={`flex flex-col items-center justify-center space-y-6 ${className}`}>
            {/* Main animated circle */}
            <div className="relative">
                {/* Outer rotating ring */}
                <motion.div
                    className="absolute inset-0"
                    animate={{ rotate: 360 }}
                    transition={{
                        duration: 3,
                        repeat: Infinity,
                        ease: 'linear',
                    }}
                >
                    <div className="w-24 h-24 rounded-full border-4 border-transparent border-t-emerald-400 border-r-purple-500 opacity-70"></div>
                </motion.div>

                {/* Middle rotating ring */}
                <motion.div
                    className="absolute inset-0"
                    animate={{ rotate: -360 }}
                    transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: 'linear',
                    }}
                >
                    <div className="w-24 h-24 rounded-full border-4 border-transparent border-b-blue-400 border-l-pink-500 opacity-50"></div>
                </motion.div>

                {/* Center icon container */}
                <div className="relative w-24 h-24 flex items-center justify-center">
                    <div className="absolute inset-4 rounded-full bg-gradient-to-br from-emerald-500/20 to-purple-500/20 backdrop-blur-xl border border-white/10"></div>

                    {/* Animated icons */}
                    <motion.div
                        animate={{
                            scale: [1, 1.2, 1],
                            rotate: [0, 180, 360],
                        }}
                        transition={{
                            duration: 2,
                            repeat: Infinity,
                            ease: 'easeInOut',
                        }}
                        className="relative z-10"
                    >
                        <Sparkles className="w-6 h-6 text-emerald-300" />
                    </motion.div>
                </div>
            </div>

            {/* Status text with typing effect */}
            <div className="text-center space-y-2">
                <motion.p
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className="text-lg font-medium text-slate-200"
                >
                    {status}
                </motion.p>

                {/* Animated dots */}
                <div className="flex items-center justify-center space-x-1">
                    {[0, 1, 2].map((i) => (
                        <motion.div
                            key={i}
                            className="w-2 h-2 rounded-full bg-emerald-400"
                            animate={{
                                scale: [1, 1.5, 1],
                                opacity: [0.3, 1, 0.3],
                            }}
                            transition={{
                                duration: 1.5,
                                repeat: Infinity,
                                delay: i * 0.2,
                            }}
                        />
                    ))}
                </div>
            </div>

            {/* Feature icons */}
            <div className="flex items-center gap-6 mt-4">
                {[
                    { icon: Code, label: 'Code', delay: 0 },
                    { icon: Palette, label: 'Design', delay: 0.2 },
                    { icon: Zap, label: 'Optimize', delay: 0.4 },
                ].map(({ icon: Icon, label, delay }) => (
                    <motion.div
                        key={label}
                        initial={{ opacity: 0, scale: 0 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay, duration: 0.3 }}
                        className="flex flex-col items-center gap-1"
                    >
                        <motion.div
                            animate={{
                                y: [0, -8, 0],
                            }}
                            transition={{
                                duration: 2,
                                repeat: Infinity,
                                delay: delay,
                            }}
                            className="w-10 h-10 rounded-lg bg-gradient-to-br from-slate-800 to-slate-900 border border-white/10 flex items-center justify-center"
                        >
                            <Icon className="w-5 h-5 text-emerald-300" />
                        </motion.div>
                        <span className="text-xs text-slate-400">{label}</span>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
