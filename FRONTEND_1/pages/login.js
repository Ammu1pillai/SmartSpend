// frontend/pages/login.js
import { useState } from 'react';
import { useRouter } from 'next/router';
import { Button, TextField, Typography, Container, Paper, Box, Alert } from '@mui/material'; // Added Alert
import { loginUser } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion'; // For animations

export default function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false); 
    const router = useRouter();
    const { login } = useAuth();

    const handleSubmit = async (event) => {
        debugger;
        event.preventDefault();
        setError('');

        if (isSubmitting) {
            console.log("Frontend: Already submitting, preventing duplicate.");
            return;
        }
        setIsSubmitting(true); 

        console.log('handleSubmit triggered.');
        console.log('Attempting login with username:', username, 'and password (length):', password.length);
        console.log('Current username state:', username); // Add this
        console.log('Current password state:', password); 
        
        await new Promise(resolve => setTimeout(resolve, 200));

        try {
            const data = await loginUser(username, password);
            login(data.access_token, data.user); // Update AuthContext state
            console.log('Frontend: Login successful. Response data:', data);
            router.push('/'); // Redirect to dashboard on successful login
        } catch (err) {
            console.error('Login failed:', err.response?.data || err.message);
            setError(err.response?.data?.msg || 'Login failed. Please check your credentials.');
        } finally {
            setIsSubmitting(false); // <--- ALWAYS RESET TO FALSE
        }
    };

    return (
            <Container component="main" maxWidth="xs">
                <motion.div
                    initial={{ opacity: 0, y: -50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                >
                    <Paper elevation={6} sx={{ // Increased elevation for more shadow
                        padding: 4,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        mt: 0,
                        borderRadius: 3, // Apply theme's border radius
                        background: 'linear-gradient(135deg, #333 0%, #1a1a1a 100%)', // Dark background
                        color: 'white' // White text for dark background
                    }}>
                        <Typography component="h1" variant="h5" sx={{ color: 'primary.light' }}>
                            Login
                        </Typography>
                        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
                            <TextField
                                margin="normal"
                                required
                                fullWidth
                                id="username"
                                label="Username"
                                name="username"
                                autoComplete="username"
                                autoFocus
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                InputLabelProps={{ style: { color: '#B0BEC5' } }} // Silver hint text
                                InputProps={{ style: { color: 'white' } }} // White input text
                                sx={{
                                    '& .MuiOutlinedInput-root': {
                                        '& fieldset': { borderColor: '#B0BEC5' },
                                        '&:hover fieldset': { borderColor: '#FF6659' },
                                        '&.Mui-focused fieldset': { borderColor: '#D32F2F' },
                                    }
                                }}
                            />
                            <TextField
                                margin="normal"
                                required
                                fullWidth
                                name="password"
                                label="Password"
                                type="password"
                                id="password"
                                autoComplete="current-password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                InputLabelProps={{ style: { color: '#B0BEC5' } }}
                                InputProps={{ style: { color: 'white' } }}
                                sx={{
                                    '& .MuiOutlinedInput-root': {
                                        '& fieldset': { borderColor: '#B0BEC5' },
                                        '&:hover fieldset': { borderColor: '#FF6659' },
                                        '&.Mui-focused fieldset': { borderColor: '#D32F2F' },
                                    }
                                }}
                            />
                            {error && (
                                <Alert severity="error" sx={{ mt: 2 }}>
                                    {error}
                                </Alert>
                            )}
                            <Button
                                type="submit"
                                fullWidth
                                variant="contained"
                                disabled={isSubmitting}
                                sx={{ mt: 3, mb: 2,
                                    background: 'linear-gradient(45deg, #D32F2F 30%, #FF6659 90%)',
                                    '&:hover': { background: 'linear-gradient(45deg, #FF6659 30%, #D32F2F 90%)' }
                                }}
                            >
                                Sign In
                            </Button>
                            <Box sx={{ textAlign: 'center' }}>
                                <Typography variant="body2" sx={{ color: '#B0BEC5' }}>
                                    Don't have an account?{' '}
                                    <Button
                                        onClick={() => router.push('/signup')}
                                        sx={{
                                            textTransform: 'none',
                                            p: 0,
                                            minWidth: 0,
                                            color: 'primary.light', // Light red for links
                                            '&:hover': { textDecoration: 'underline', backgroundColor: 'transparent' }
                                        }}
                                    >
                                        Sign Up
                                    </Button>
                                </Typography>
                            </Box>
                        </Box>
                    </Paper>
                </motion.div>
            </Container>
    );
}