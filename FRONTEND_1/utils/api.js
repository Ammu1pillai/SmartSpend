// frontend/utils/api.js
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

const publicApi = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true,
});

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true,
});

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// AUTHENTICATION API CALLS

export const signupUser = async (email, username, password) => {
    try {
        const response = await publicApi.post('/api/register', { // Correct usage
            username,
            password,
            email
        });
        console.log('Signup successful, response:', response.data);
        return response.data;
    } catch (error) {
        console.error('Signup API Error:', error.response?.data || error.message);
        throw error;
    }
};

export const loginUser = async (username, password) => {
    try {
        // Use publicApi for login, as it's not an authenticated request.
        // No need for `${API_BASE_URL}/api/login` because baseURL is already set.
        const response = await publicApi.post('/api/login', {
            username,
            password,
        });
        console.log('Login successful, response:', response.data);
        const { access_token, user } = response.data;
        if (access_token) {
            localStorage.setItem('access_token', access_token);
            api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        }
        return response.data;
    } catch (error) {
        console.error('Login API Error:', error.response?.data || error.message);
        throw error;
    }
};

export const logoutUser = async () => {
    try {
        // Use 'api' for logout as it's a protected route.
        // Interceptor handles Authorization header.
        const response = await api.post('/api/logout', {});
        localStorage.removeItem('access_token');
        delete api.defaults.headers.common['Authorization'];
        console.log('Token removed from localStorage and header cleared.');
        return response.data;
    } catch (error) {
        console.error('Logout Error:', error.response?.data || error.message);
        localStorage.removeItem('access_token');
        delete api.defaults.headers.common['Authorization'];
        throw error;
    }
};

export const checkLoginStatus = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
        return { isLoggedIn: false, username: null, userId: null, email: null };
    }

    try {
        // Use 'api' for status check. Interceptor handles token.
        const response = await api.get('/api/status');
        const { isLoggedIn, user } = response.data;
        return { isLoggedIn, username: user.username, userId: user.id, email: user.email };
    } catch (error) {
        console.error('Token verification failed or expired:', error.response?.data?.msg || error.message);
        localStorage.removeItem('access_token');
        delete api.defaults.headers.common['Authorization'];
        return { isLoggedIn: false, username: null, userId: null, email: null };
    }
};

// PROTECTED RESOURCE API CALLS

export const uploadReceipt = async (file) => {
    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await api.post('/api/upload', formData, {
            headers: {
                'Content-Type': undefined,
            },
        });
        return response.data;
    } catch (error) {
        console.error('Upload API Error:', error.response?.data || error.message);
        throw error;
    }
};

export const getUserData = async (userId) => {
    try {
        const response = await api.get(`/api/profile/${userId}`); // Correct usage
        return response.data;
    } catch (error) {
        console.error('Get User Data API Error:', error.response?.data || error.message);
        throw error;
    }
};

export const getTransactions = async () => {
    try {
        const response = await api.get('/api/transactions'); // Correct usage
        return response.data;
    } catch (error) {
        console.error('Get Transactions API Error:', error.response?.data || error.message);
        throw error;
    }
};

export const getChartData = async (chartType) => {
    try {
        const response = await api.get(`/api/charts/${chartType}`); // Correct usage
        return response.data;
    } catch (error) {
        console.error(`Get ${chartType} Chart Data API Error:`, error.response?.data || error.message);
        throw error;
    }
};

export const getSpendingSummary = async () => {
    try {
        const response = await api.get('/api/summary'); // Correct usage
        return response.data;
    } catch (error) {
        console.error('Get Spending Summary API Error:', error.response?.data || error.message);
        throw error;
    }
};

export default api;