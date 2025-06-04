// frontend/pages/signup.js
import { useState } from 'react';
import { useRouter } from 'next/router';
import { signupUser } from '../utils/api';
import { TextField, Button, Typography, Paper, Box, Alert, Container } from '@mui/material'; // Added Container import
import Link from 'next/link';
import { motion } from 'framer-motion';

export default function Signup() {
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const router = useRouter();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        if (password !== confirmPassword) {
            setError('Passwords do not match.');
            return;
        }

        try {
            const response = await signupUser(email, username, password);
            console.log('Signup successful:', response);
            setSuccess('Account created successfully! Redirecting to login...');
            setTimeout(() => {
                router.push('/login');
            }, 2000);
        }
        catch (err) {
            console.error('Signup failed:', err);
            let errorMsg = 'Signup failed. Please try again.';
            if (err.response) {
                try {
                    const data = await err.response.json();
                    errorMsg = data.msg || errorMsg;
                } catch (e) {
                    errorMsg = err.response.statusText || errorMsg;
                }
            }
            setError(errorMsg);
        }
    };

    return (
        // --- IMPORTANT: Removed the <Layout> wrapper here ---
        <Container component="main" maxWidth="xs"> {/* Added Container for consistent centering */}
            <motion.div
                initial={{ opacity: 0, y: -50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <Paper elevation={6} sx={{ // Increased elevation for more shadow
                    p: 4,
                    maxWidth: 400,
                    margin: 'auto',
                    mt: 2, // Keep this mt: 2 for spacing within the main content area
                    borderRadius: 3,
                    background: 'linear-gradient(135deg, #333 0%, #1a1a1a 100%)', // Dark background
                    color: 'white'
                }}>
                    <Typography variant="h5" component="h1" gutterBottom align="center" sx={{ color: 'primary.light' }}>
                        Sign Up
                    </Typography>
                    {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
                    {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
                    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            id="email"
                            label="Email Address"
                            name="email"
                            autoComplete="email"
                            autoFocus
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            type="email"
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
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            id="username"
                            label="Username"
                            name="username"
                            autoComplete="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
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
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            name="password"
                            label="Password"
                            type="password"
                            id="password"
                            autoComplete="new-password"
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
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            name="confirmPassword"
                            label="Confirm Password"
                            type="password"
                            id="confirmPassword"
                            autoComplete="new-password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            error={password !== confirmPassword && confirmPassword !== ''}
                            helperText={password !== confirmPassword && confirmPassword !== '' ? 'Passwords do not match' : ''}
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
                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            sx={{ mt: 3, mb: 2,
                                background: 'linear-gradient(45deg, #D32F2F 30%, #FF6659 90%)',
                                '&:hover': { background: 'linear-gradient(45deg, #FF6659 30%, #D32F2F 90%)' }
                            }}
                        >
                            Sign Up
                        </Button>
                        <Box sx={{ textAlign: 'center' }}>
                            <Link href="/login" passHref>
                                <Typography component="a" variant="body2" sx={{ cursor: 'pointer', color: 'primary.light', '&:hover': { textDecoration: 'underline' } }}>
                                    Already have an account? Login
                                </Typography>
                            </Link>
                        </Box>
                    </Box>
                </Paper>
            </motion.div>
        </Container>
        // --- IMPORTANT: Removed the </Layout> wrapper here ---
    );
}
