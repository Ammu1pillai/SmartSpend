// frontend/context/AuthContext.js
import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { loginUser, logoutUser, checkLoginStatus } from '../utils/api'; // Import your API functions
import { useRouter } from 'next/router';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null); // Will store { username, userId, isLoggedIn: true } or null
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    const fetchUser = useCallback(async () => {
        setLoading(true);
        try {
            const status = await checkLoginStatus();
            if (status.isLoggedIn) {
                setUser({
                    username: status.username,
                    userId: status.userId,
                    isLoggedIn: true
                });
            } else {
                setUser(null);
            }
        } catch (error) {
            console.error('Failed to fetch user status:', error);
            setUser(null);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchUser();
    }, [fetchUser]);

    const login = useCallback((token, userData) => {
        setUser({
            username: userData.username, // Assuming userData from loginUser API response has 'username'
            userId: userData.id,     // Assuming userData from loginUser API response has 'userId'
            isLoggedIn: true
        });
        setLoading(false); // Finished logging in, so set loading to false
    }, []);

    const logout = async () => {
        try {
            setLoading(true);
            await logoutUser();
            setUser(null);
            setLoading(false);
            router.push('/login'); // Redirect to login page after logout
        } catch (error) {
            console.error('Logout failed:', error);
            setUser(null);
            router.push('/login');
        } finally{
            setLoading(false); 
        }
    };

    // This value will be provided to any component that uses this context
    const value = {
        user,
        loading,
        login,
        logout,
        fetchUser // Expose fetchUser so components can manually re-fetch (e.g., after signup)
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Custom hook to use the AuthContext
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};