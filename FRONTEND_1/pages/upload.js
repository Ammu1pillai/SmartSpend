// frontend/pages/upload.js
import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../context/AuthContext'; // Corrected typo: AuthContext
import { Button, Paper, Typography, Box, CircularProgress, Alert, Container } from '@mui/material'; // Added Container import
import { CloudUpload } from '@mui/icons-material';
import { uploadReceipt } from '../utils/api';
import { motion } from 'framer-motion';

export default function Upload() {
    const { user, loading } = useAuth();
    const router = useRouter();

    const [isUploading, setIsUploading] = useState(false);
    const [uploadSuccess, setUploadSuccess] = useState(false);
    const [uploadError, setUploadError] = useState('');
    const [file, setFile] = useState(null);

    useEffect(() => {
        if (!loading && (!user || !user.isLoggedIn)) {
            router.push('/login');
        }
    }, [user, loading, router]);

    const handleUpload = async (e) => {
        e.preventDefault();
        setUploadError('');
        setUploadSuccess(false);

        console.log('--- handleUpload called ---');
        console.log('   User object at time of upload:', user);
        console.log('   user.userId at time of upload:', user?.userId);

        if (!file) {
            setUploadError("Please select an image to upload.");
            return;
        }
        if (!user || !user.userId) {
            console.warn('Condition met: user is null/undefined or user.userId is missing/null.');
            setUploadError("User not logged in. Please log in to upload.");
            return;
        }

        setIsUploading(true);

        try {
            await uploadReceipt(file); // userId is used on frontend for clarity, backend uses JWT identity
            setUploadSuccess(true);
            setFile(null);
            setTimeout(() => setUploadSuccess(false), 3000);
        } catch (error) {
            console.error('Upload failed:', error.response?.data || error.message);
            setUploadError(error.response?.data?.error || 'Upload failed. Please try again.');
        } finally {
            setIsUploading(false);
        }

    };

    if (loading) {
        return (
            // IMPORTANT: Removed the <Layout> wrapper here for loading state
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
                <CircularProgress sx={{ color: 'primary.light' }} />
                <Typography variant="h6" sx={{ ml: 2, color: 'text.primary' }}>Checking authentication...</Typography>
            </Box>
        );
    }

    if (!user || !user.isLoggedIn) {
        return null;
    }

    return (
        // --- IMPORTANT: Removed the <Layout> wrapper here and added Container ---
        <Container component="main" maxWidth="md"> {/* Using maxWidth="md" or "sm" might be better for upload content */}
            <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 4, color: 'primary.light' }}>
                Upload Receipt
            </Typography>
            <motion.div
                initial={{ opacity: 0, y: -50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <Paper elevation={6} sx={{ // Increased elevation for more shadow
                    p: 4,
                    maxWidth: 600, // Adjusted max width for the paper content
                    margin: 'auto',
                    mt: 2, // Keep this mt: 2 for spacing within the main content area
                    borderRadius: 3,
                    background: 'linear-gradient(135deg, #333 0%, #1a1a1a 100%)', // Dark background
                    color: 'white'
                }}>
                    <Typography variant="h6" gutterBottom align="center" sx={{ color: '#B0BEC5' }}>
                        Upload a new receipt for OCR processing
                    </Typography>
                    {uploadSuccess && <Alert severity="success" sx={{ mb: 2 }}>Receipt processed successfully!</Alert>}
                    {uploadError && <Alert severity="error" sx={{ mb: 2 }}>{uploadError}</Alert>}
                    <Box component="form" onSubmit={handleUpload} sx={{ mt: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                        <Button
                            variant="outlined"
                            component="label"
                            startIcon={<CloudUpload />}
                            fullWidth
                            sx={{
                                mb: 2,
                                borderColor: '#B0BEC5',
                                color: '#B0BEC5',
                                '&:hover': { borderColor: '#FF6659', color: '#FF6659' }
                            }}
                        >
                            Select Image
                            <input
                                type="file"
                                hidden
                                accept="image/*"
                                onChange={(e) => setFile(e.target.files[0])}
                            />
                        </Button>

                        {file && (
                            <Typography variant="body2" sx={{ mt: 1, color: '#B0BEC5' }}>
                                Selected file: {file.name}
                            </Typography>
                        )}

                        {isUploading ? (
                            <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                                <CircularProgress size={24} sx={{ mr: 2, color: 'primary.light' }} />
                                <Typography sx={{ color: 'text.primary' }}>Processing receipt...</Typography>
                            </Box>
                        ) : (
                            <Button
                                type="submit"
                                variant="contained"
                                color="primary"
                                sx={{ mt: 2,
                                    background: 'linear-gradient(45deg, #D32F2F 30%, #FF6659 90%)',
                                    '&:hover': { background: 'linear-gradient(45deg, #FF6659 30%, #D32F2F 90%)' },
                                    color: 'white'
                                }}
                                disabled={!file}
                            >
                                Upload Receipt
                            </Button>
                        )}
                    </Box>
                </Paper>
            </motion.div>
        </Container>
        // --- IMPORTANT: Removed the </Layout> wrapper here ---
    );
}
