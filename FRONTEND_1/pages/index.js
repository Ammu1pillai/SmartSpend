import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../context/AuthContext';
import { Typography, Box, CircularProgress, Paper, Grid, Card, CardContent, Alert } from '@mui/material';
import { getSpendingSummary, getTransactions } from '../utils/api';
import { BarChart, PieChart } from '../components/Charts';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

function TransactionDate({ date }) {
  const [formattedDate, setFormattedDate] = useState('');

  useEffect(() => {
    if (date) {
      setFormattedDate(new Date(date).toLocaleDateString());
    }
  }, [date]);

  return <span>{formattedDate}</span>;
}

export default function Home() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [summary, setSummary] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [dataLoading, setDataLoading] = useState(true);
  const [dataError, setDataError] = useState('');
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);

    if (!loading && (!user || !user.isLoggedIn)) {
      router.push('/login');
    }

    const fetchData = async () => {
      if (user && user.isLoggedIn) {
        setDataLoading(true);
        setDataError('');
        try {
          const [summaryRes, transactionsRes] = await Promise.all([
            getSpendingSummary(),
            getTransactions(),
          ]);
          setSummary(summaryRes);
          setTransactions(transactionsRes);
        } catch (err) {
          console.error('Failed to fetch dashboard data:', err);
          setDataError('Failed to load dashboard data. Please try again.');
        } finally {
          setDataLoading(false);
        }
      }
    };

    if (!loading) {
      fetchData();
    }
  }, [user, loading, router]);

  if (loading || dataLoading) {
    return (
      // IMPORTANT: Removed the <Layout> wrapper here for loading state
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
        <Typography variant="h6" sx={{ ml: 2 }}>
          {loading ? 'Checking authentication...' : 'Loading dashboard data...'}
        </Typography>
      </Box>
    );
  }

  if (!user || !user.isLoggedIn) {
    return null;
  }

  return (
    // --- IMPORTANT: Wrapped the multiple top-level elements in a React Fragment ---
    <>
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 2 }}>
        Welcome, {user.username || 'User'}!
      </Typography>

      {dataError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {dataError}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Spending Summary */}
        <Grid item xs={12} md={6} lg={4}>
          <Card elevation={3} sx={{
            height: '100%',
            background: 'linear-gradient(45deg, #D32F2F 30%, #B0BEC5 90%)',
            color: 'white',
            transition: 'transform 0.3s ease-in-out',
            '&:hover': { transform: 'scale(1.02)' }
          }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Monthly Spending Summary
              </Typography>
              {summary ? (
                <Box>
                  <Typography variant="body1">Current Month: ${summary.currentMonthSpending?.toFixed(2) || '0.00'}</Typography>
                  <Typography variant="body1">Last Month: ${summary.lastMonthSpending?.toFixed(2) || '0.00'}</Typography>
                  <Typography variant="body1">Avg. Daily: ${summary.averageDaily?.toFixed(2) || '0.00'}</Typography>
                  <Typography variant="body1">Savings Rate: {summary.savingsRate || 'N/A'}</Typography>
                </Box>
              ) : (
                <Typography>No summary available.</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Bar Chart */}
        <Grid item xs={12} md={6} lg={4}>
          <Paper elevation={3} sx={{ p: 2, height: '100%', transition: 'transform 0.3s ease-in-out', '&:hover': { transform: 'scale(1.02)' } }}>
            <Typography variant="h6" gutterBottom align="center">
              Daily Spending Trends
            </Typography>
            {isClient && <BarChart />}
          </Paper>
        </Grid>

        {/* Pie Chart */}
        <Grid item xs={12} md={6} lg={4}>
          <Paper elevation={3} sx={{ p: 2, height: '100%', transition: 'transform 0.3s ease-in-out', '&:hover': { transform: 'scale(1.02)' } }}>
            <Typography variant="h6" gutterBottom align="center">
              Spending Categories
            </Typography>
            {isClient && <PieChart />}
          </Paper>
        </Grid>

        {/* Recent Transactions */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 3, mt: 3, transition: 'transform 0.3s ease-in-out', '&:hover': { transform: 'scale(1.01)' } }}>
            <Typography variant="h5" component="h2" gutterBottom>
              Recent Transactions
            </Typography>
            {transactions.length > 0 ? (
              <Box>
                {transactions.slice(0, 5).map((transaction) => (
                  <Box key={transaction.id} sx={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed #eee', py: 1 }}>
                    <Typography variant="body1">{transaction.store}</Typography>
                    <Typography variant="body1">
                      ${transaction.amount?.toFixed(2) || '0.00'} on <TransactionDate date={transaction.date} />
                    </Typography>
                  </Box>
                ))}
              </Box>
            ) : (
              <Typography>No recent transactions found. Upload a receipt to get started!</Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </>
  );
}
