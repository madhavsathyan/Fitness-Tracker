/**
 * API Service
 * Handles all HTTP requests to the FastAPI backend
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const api: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor - add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('accessToken');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor - handle errors
api.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
        if (error.response?.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('accessToken');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// ==================== AUTH ====================

export interface LoginCredentials {
    username: string;
    password: string;
}

export interface RegisterData {
    username: string;
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
    age?: number;
    gender?: string;
    height_cm?: number;
    weight_kg?: number;
    fitness_goal?: string;
}

export interface User {
    id: number;
    username: string;
    email: string;
    role: string;
    first_name?: string;
    last_name?: string;
    age?: number;
    gender?: string;
    height_cm?: number;
    weight_kg?: number;
    fitness_goal?: string;
    is_active: boolean;
    daily_water_goal_ml?: number;
    daily_calorie_goal?: number;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
}

export const authApi = {
    login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
        const formData = new URLSearchParams();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);

        const response = await api.post<AuthResponse>('/auth/login', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });
        return response.data;
    },

    register: async (data: RegisterData): Promise<User> => {
        const response = await api.post<{ user: User }>('/auth/register', data);
        return response.data.user;
    },

    getCurrentUser: async (): Promise<User> => {
        const response = await api.get<User>('/auth/me');
        return response.data;
    },

    checkRole: async (): Promise<{ role: string }> => {
        const response = await api.get<{ role: string }>('/auth/me');
        return { role: response.data.role };
    },
};

// ==================== DASHBOARD ====================

export interface DashboardData {
    summary: {
        total_calories_today: number;
        total_workouts_week: number;
        avg_sleep_hours: number;
        water_intake_today: number;
    };
    weekly_workouts: Array<{ day: string; minutes: number; type: string }>;
    daily_calories: Array<{ date: string; calories: number }>;
    macronutrients: { protein: number; carbs: number; fat: number };
    weight_trend: Array<{ date: string; weight: number }>;
}

export const dashboardApi = {
    getDashboardData: async (userId?: number): Promise<DashboardData> => {
        const params = userId ? { user_id: userId } : {};
        const response = await api.get<DashboardData>('/analytics/dashboard', { params });
        return response.data;
    },

    getTodayProgress: async (userId?: number) => {
        const params = userId ? { user_id: userId } : {};
        const response = await api.get('/analytics/dashboard/today', { params });
        return response.data;
    },

    getWeeklyOverview: async (userId?: number) => {
        const params = userId ? { user_id: userId } : {};
        const response = await api.get('/analytics/dashboard/weekly', { params });
        return response.data;
    },

    getWorkoutsChartData: async (userId?: number) => {
        const params = userId ? { user_id: userId } : {};
        const response = await api.get('/analytics/dashboard/workouts-chart', { params });
        return response.data;
    },

    getWeeklyStats: async (userId?: number) => {
        const params = userId ? { user_id: userId } : {};
        const response = await api.get('/analytics/weekly', { params });
        return response.data;
    },

    getDashboardCharts: async () => {
        const response = await api.get('/charts/dashboard');
        return response.data;
    },
};

// ==================== ADMIN ====================

export const adminApi = {
    getAllUsers: async (params?: { skip?: number; limit?: number }): Promise<User[]> => {
        const response = await api.get<User[]>('/users/', { params });
        return response.data;
    },

    searchUsers: async (query: string): Promise<User[]> => {
        const response = await api.get<User[]>('/search/users', { params: { q: query } });
        return response.data;
    },

    getDashboardData: async (userId?: number) => {
        const response = await api.get(`/users/${userId}/dashboard`);
        return response.data;
    },

    getAdminOverviewCharts: async () => {
        const response = await api.get('/charts/admin/overview');
        return response.data;
    },

    getRecentSignups: async (limit: number = 10): Promise<User[]> => {
        const response = await api.get<User[]>('/users/', {
            params: { limit, sort: 'created_at:desc' },
        });
        return response.data;
    },

    deleteUser: async (userId: number): Promise<void> => {
        await api.delete(`/admin/users/${userId}`);
    },

    getUserDetails: async (userId: number) => {
        const response = await api.get(`/admin/users/${userId}/details`);
        return response.data;
    },

    getUserActivity: async (userId: number) => {
        const response = await api.get(`/admin/users/${userId}/activity`);
        return response.data;
    },

    updateUserRole: async (userId: number, role: 'user' | 'admin') => {
        const response = await api.put(`/admin/users/${userId}/role`, { role });
        return response.data;
    },

    toggleUserBlacklist: async (userId: number, isBlacklisted: boolean, reason?: string) => {
        const response = await api.put(`/admin/users/${userId}/blacklist`, {
            is_blacklisted: isBlacklisted,
            reason
        });
        return response.data;
    },

    getActivityFeed: async (params?: { limit?: number; action_type?: string }) => {
        const response = await api.get('/activity/', { params });
        return response.data;
    },

    getActivityStats: async () => {
        const response = await api.get('/activity/stats');
        return response.data;
    },

    getSystemStats: async () => {
        const response = await api.get('/admin/stats');
        return response.data;
    },

    getAnalytics: async () => {
        const response = await api.get('/analytics/dashboard');
        return response.data;
    },
};

// ==================== WORKOUTS ====================

export const workoutApi = {
    getAll: async (params?: { user_id?: number; limit?: number }) => {
        const response = await api.get('/workouts/', { params });
        return response.data;
    },

    getDailySummary: async (date: string, userId?: number) => {
        const params = userId ? { user_id: userId } : {};
        const response = await api.get(`/workouts/daily_summary`, { params: { ...params, target_date: date } });
        return response.data;
    },

    getWeekly: async (userId?: number) => {
        const params = userId ? { user_id: userId } : {};
        const response = await api.get('/workouts/weekly', { params });
        return response.data;
    },

    create: async (data: any) => {
        const response = await api.post('/workouts/', data);
        return response.data;
    },

    update: async (id: number, data: any) => {
        const response = await api.put(`/workouts/${id}`, data);
        return response.data;
    },

    delete: async (id: number) => {
        await api.delete(`/workouts/${id}`);
    },
};

// ==================== NUTRITION ====================

export const nutritionApi = {
    getAll: async (params?: { user_id?: number; limit?: number }) => {
        const response = await api.get('/nutrition/', { params });
        return response.data;
    },

    getDailySummary: async (date: string, userId?: number) => {
        const params = userId ? { user_id: userId } : {};
        const response = await api.get(`/nutrition/daily/${date}`, { params });
        return response.data;
    },

    getWeekly: async (userId?: number) => {
        const params = userId ? { user_id: userId } : {};
        const response = await api.get('/nutrition/weekly', { params });
        return response.data;
    },

    create: async (data: any) => {
        const response = await api.post('/nutrition/', data);
        return response.data;
    },

    update: async (id: number, data: any) => {
        const response = await api.put(`/nutrition/${id}`, data);
        return response.data;
    },

    delete: async (id: number) => {
        await api.delete(`/nutrition/${id}`);
    },
};

// ==================== WATER ====================

export const waterApi = {
    getDailyTotal: async (date: string, userId?: number) => {
        const params = userId ? { user_id: userId } : {};
        const response = await api.get(`/water/daily/${date}`, { params });
        return response.data;
    },

    getWeekly: async (userId?: number) => {
        const params = userId ? { user_id: userId } : {};
        const response = await api.get('/water/weekly', { params });
        return response.data;
    },

    create: async (data: any) => {
        const response = await api.post('/water/', data);
        return response.data;
    },

    update: async (id: number, data: any) => {
        const response = await api.put(`/water/${id}`, data);
        return response.data;
    },

    delete: async (id: number) => {
        await api.delete(`/water/${id}`);
    },
};

// ==================== SLEEP ====================

export const sleepApi = {
    getAverage: async (userId?: number) => {
        const params = userId ? { user_id: userId } : {};
        const response = await api.get('/sleep/average', { params });
        return response.data;
    },

    getByDateRange: async (startDate: string, endDate: string, userId?: number) => {
        const params = { start_date: startDate, end_date: endDate, user_id: userId };
        const response = await api.get('/sleep/', { params });
        return response.data;
    },
    getWeekly: async (userId?: number) => {
        const params = userId ? { user_id: userId } : {};
        const response = await api.get('/sleep/weekly', { params });
        return response.data;
    },

    getAll: async (params?: { user_id?: number; limit?: number }) => {
        const response = await api.get('/sleep/', { params });
        return response.data;
    },

    create: async (data: any) => {
        const response = await api.post('/sleep/', data);
        return response.data;
    },

    update: async (id: number, data: any) => {
        const response = await api.put(`/sleep/${id}`, data);
        return response.data;
    },

    delete: async (id: number) => {
        await api.delete(`/sleep/${id}`);
    },
};

// ==================== WEIGHT ====================

export const weightApi = {
    getTrend: async (userId?: number, days: number = 30) => {
        const params = { ...(userId && { user_id: userId }), days };
        const response = await api.get('/weight/trend', { params });
        return response.data;
    },

    create: async (data: any) => {
        const response = await api.post('/weight/', data);
        return response.data;
    },
};

// ==================== GOALS ====================

export const goalsApi = {
    getAll: async (params?: { user_id?: number; category?: string; is_active?: boolean }) => {
        const response = await api.get('/goals/', { params });
        return response.data;
    },

    create: async (data: any) => {
        const response = await api.post('/goals/', data);
        return response.data;
    },

    update: async (id: number, data: any) => {
        const response = await api.put(`/goals/${id}`, data);
        return response.data;
    },

    delete: async (id: number) => {
        await api.delete(`/goals/${id}`);
    },
};

export default api;
