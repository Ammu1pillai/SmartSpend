import React, { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';

// --- IMPORTANT: Adjust this path if your api.js is not in a 'utils' folder relative to this file ---
import api from '../utils/api'; // <--- ADDED THIS IMPORT

export default function ReactTransactions() {
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchTransactions = async () => {
            try {
                // --- CHANGED THIS LINE: Using the imported 'api' instance ---
                const response = await api.get('/api/transactions');
                setTransactions(response.data); // Axios puts data in .data, no need for .json()
            } catch (err) {
                console.error("Failed to fetch transactions:", err);
                setError(err);
            } finally {
                setLoading(false);
            }
        };

        fetchTransactions();
    }, []);

    if (loading) {
        return <Typography>Loading transactions...</Typography>;
    }

    if (error) {
        return <Typography color="error">Error loading transactions: {error.message}</Typography>;
    }

    if (transactions.length === 0) {
        return (
            <>
                <Typography variant="h6" gutterBottom>
                    Recent Transactions
                </Typography>
                <Typography>No recent transactions available.</Typography>
            </>
        );
    }

    return (
        <>
            <Typography variant="h6" gutterBottom>
                Recent Transactions
            </Typography>
            <Table size="small">
                <TableHead>
                    <TableRow>
                        <TableCell>Store</TableCell>
                        <TableCell align="right">Amount</TableCell>
                        <TableCell>Date</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {transactions.map((tx) => (
                        <TableRow key={tx.id}>
                            <TableCell>{tx.store}</TableCell>
                            <TableCell align="right">${tx.amount ? tx.amount.toFixed(2) : '0.00'}</TableCell>
                            <TableCell>{tx.date}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </>
    );
}