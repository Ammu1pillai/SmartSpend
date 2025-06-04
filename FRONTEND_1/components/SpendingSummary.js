import React, { useState, useEffect } from 'react';
import { Box, Typography } from '@mui/material';

// --- IMPORTANT: Adjust this path if your api.js is not in a 'utils' folder relative to this file ---
import api from '../utils/api'; // <--- ADDED THIS IMPORT

export default function SpendingSummary() {
    const [summary, setSummary] = useState({
        currentMonth: 'Loading...',
        lastMonth: 'Loading...',
        averageDaily: 'Loading...',
        savingsRate: 'Loading...',
        savingsRateColor: 'text.secondary'
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchSummary = async () => {
            try {
                // --- CHANGED THIS LINE: Using the imported 'api' instance ---
                const response = await api.get('/api/summary');
                const data = response.data; // Axios puts data in .data, no need for .json()

                setSummary({
                    currentMonth: `$${data.currentMonthSpending ? data.currentMonthSpending.toFixed(2) : '0.00'}`,
                    lastMonth: `$${data.lastMonthSpending ? data.lastMonthSpending.toFixed(2) : '0.00'}`,
                    averageDaily: `$${data.averageDaily ? data.averageDaily.toFixed(2) : '0.00'}`,
                    savingsRate: `${data.savingsRate ? data.savingsRate : '0'}%`,
                    savingsRateColor: data.savingsRate && data.savingsRate > 0 ? 'primary' : 'text.secondary'
                });
            } catch (err) {
                console.error("Failed to fetch summary:", err);
                setError(err);
            } finally {
                setLoading(false);
            }
        };

        fetchSummary();
    }, []);

    if (loading) {
        return <Typography>Loading summary...</Typography>;
    }

    if (error) {
        return <Typography color="error">Error loading summary: {error.message}</Typography>;
    }

    return (
        <>
            <Typography variant="h6" gutterBottom>
                Spending Summary
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography>This Month:</Typography>
                <Typography>{summary.currentMonth}</Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography>Last Month:</Typography>
                <Typography>{summary.lastMonth}</Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography>Average Daily:</Typography>
                <Typography>{summary.averageDaily}</Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                <Typography variant="subtitle1">Savings Rate:</Typography>
                <Typography variant="subtitle1" color={summary.savingsRateColor}>
                    {summary.savingsRate}
                </Typography>
            </Box>
        </>
    );
}