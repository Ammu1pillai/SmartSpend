// frontend/pages/profile.js
import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../context/AuthContext';
import { getUserData } from '../utils/api';
import { Typography, Paper, Box, CircularProgress, Alert } from '@mui/material';
import { motion } from 'framer-motion';

export default function Profile() {
    const { user, loading } = useAuth();
    const router = useRouter();
    const [profileData, setProfileData] = useState(null);
    const [profileLoading, setProfileLoading] = useState(true);
    const [profileError, setProfileError] = useState('');

    useEffect(() => {
        if (!loading && (!user || !user.isLoggedIn)) {
            router.push('/login');
        }

        const fetchProfile = async () => {
            if (user && user.userId) {
                try {
                    setProfileLoading(true);
                    setProfileError('');
                    const data = await getUserData(user.userId);
                    setProfileData(data);
                } catch (err) {
                    console.error("Failed to fetch profile data:", err);
                    setProfileError(err.response?.data?.msg || 'Failed to load profile data.');
                } finally {
                    setProfileLoading(false);
                }
            } else {
                setProfileLoading(false);
            }
        };

        if (!loading) {
            fetchProfile();
        }
    }, [user, loading, router]);

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
                <CircularProgress sx={{ color: 'primary.light' }} />
                <Typography variant="h6" sx={{ ml: 2, color: 'text.primary' }}>Checking authentication...</Typography>
            </Box>
        );
    }

    if (!user || !user.isLoggedIn) {
        return null; // Redirect handled by useEffect
    }

    return (
        // --- IMPORTANT: Wrapped the two top-level elements in a React Fragment ---
        <>
            <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 4, color: 'primary.light' }}>
                User Profile
            </Typography>
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
            >
                <Paper elevation={6} sx={{ // Increased elevation for more shadow
                    p: 4,
                    maxWidth: 600,
                    margin: 'auto',
                    mt: 2, // Keep this at 2, or adjust as needed for spacing within the main content area
                    borderRadius: 3,
                    background: 'linear-gradient(135deg, #333 0%, #1a1a1a 100%)', // Dark background
                    color: 'white'
                }}>
                    {profileLoading ? (
                        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 4 }}>
                            <CircularProgress sx={{ color: 'primary.light' }} />
                            <Typography variant="h6" sx={{ ml: 2, color: 'text.primary' }}>Loading profile...</Typography>
                        </Box>
                    ) : profileError ? (
                        <Alert severity="error">{profileError}</Alert>
                    ) : profileData ? (
                        <Box>
                            <Typography variant="h6" gutterBottom sx={{ color: 'primary.light' }}>
                                Username: <span style={{ color: 'white' }}>{profileData.username || user.username}</span>
                            </Typography>
                            <Typography variant="body1" gutterBottom>
                                Email: <span style={{ color: '#B0BEC5' }}>{profileData.email || user.email || 'N/A'}</span>
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Member since: <span style={{ color: '#B0BEC5' }}>{profileData.join_date ? new Date(profileData.join_date).toLocaleDateString() : 'N/A'}</span>
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Total Spent (mock): <span style={{ color: '#B0BEC5' }}>${profileData.totalSpent ? profileData.totalSpent.toFixed(2) : '0.00'}</span>
                            </Typography>
                            {/* You could add a section here to display a list of user's receipts/transactions */}
                        </Box>
                    ) : (
                        <Typography sx={{ color: 'text.secondary' }}>No profile data available.</Typography>
                    )}
                </Paper>
            </motion.div>
        </>
    );
}
