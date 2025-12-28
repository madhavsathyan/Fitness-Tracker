/**
 * Auth Store
 * Zustand store for authentication state management
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi, User, LoginCredentials, RegisterData } from '../services/api';

interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;

    // Actions
    login: (credentials: LoginCredentials) => Promise<boolean>;
    register: (data: RegisterData) => Promise<boolean>;
    logout: () => void;
    checkAuth: () => Promise<void>;
    clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,

            login: async (credentials: LoginCredentials) => {
                set({ isLoading: true, error: null });
                try {
                    const response = await authApi.login(credentials);
                    localStorage.setItem('accessToken', response.access_token);

                    // Get user details
                    const user = await authApi.getCurrentUser();

                    set({
                        token: response.access_token,
                        user,
                        isAuthenticated: true,
                        isLoading: false,
                    });
                    return true;
                } catch (error: any) {
                    const message = error.response?.data?.detail || 'Login failed';
                    set({ error: message, isLoading: false });
                    return false;
                }
            },

            register: async (data: RegisterData) => {
                set({ isLoading: true, error: null });
                try {
                    await authApi.register(data);
                    set({ isLoading: false });
                    return true;
                } catch (error: any) {
                    const message = error.response?.data?.detail || 'Registration failed';
                    set({ error: message, isLoading: false });
                    return false;
                }
            },

            logout: () => {
                localStorage.removeItem('accessToken');
                localStorage.removeItem('auth-storage'); // Clear persisted Zustand state
                set({
                    user: null,
                    token: null,
                    isAuthenticated: false,
                });
            },

            checkAuth: async () => {
                const token = localStorage.getItem('accessToken');
                if (!token) {
                    set({ isAuthenticated: false, user: null });
                    return;
                }

                try {
                    const user = await authApi.getCurrentUser();
                    set({ user, isAuthenticated: true, token });
                } catch {
                    localStorage.removeItem('accessToken');
                    set({ isAuthenticated: false, user: null, token: null });
                }
            },

            clearError: () => set({ error: null }),
        }),
        {
            name: 'auth-storage',
            partialize: (state) => ({
                token: state.token,
                user: state.user,
                isAuthenticated: state.isAuthenticated,
            }),
        }
    )
);

// Helper hook to check if user is admin
export const useIsAdmin = () => {
    const user = useAuthStore((state) => state.user);
    return user?.role === 'admin';
};

// Helper hook to get current user role
export const useUserRole = () => {
    const user = useAuthStore((state) => state.user);
    return user?.role || 'guest';
};
