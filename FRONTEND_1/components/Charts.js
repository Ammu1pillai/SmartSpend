import React, { useState, useEffect } from 'react';
import { Bar, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, registerables } from 'chart.js';
import { Typography, Box } from '@mui/material';

// --- ADJUSTED IMPORT PATH HERE ---
// This path assumes your chart component is in a folder one level above 'utils',
// for example, if chart is in `src/components/` and api.js is in `src/utils/`.
import api from '../utils/api'; // <--- THIS IS THE CORRECTED PATH

ChartJS.register(...registerables);

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
     plugins: {
        legend: {
            position: 'top',
        },
        title: {
            display: true,
            text: 'Chart', // Add a title here
        }
    }
};

export function BarChart() {
    const [chartData, setChartData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchBarChartData = async () => {
            try {
                // Using the imported 'api' instance
                const response = await api.get('/api/charts/bar');
                setChartData(response.data); // Axios puts data in .data
            } catch (err) {
                console.error("Failed to fetch bar chart data:", err);
                setError(err);
            } finally {
                setLoading(false);
            }
        };

        fetchBarChartData();
    }, []);

    if (loading) {
        return <Typography>Loading bar chart...</Typography>;
    }

    if (error) {
        return <Typography color="error">Error loading bar chart: {error.message}</Typography>;
    }

    if (!chartData) {
        return <Typography>No bar chart data available.</Typography>;
    }

    return (
        // *** ADD A PARENT DIV/BOX WITH A DEFINED HEIGHT ***
        // You can adjust the height as needed (e.g., '400px', '50vh', etc.)
        <Box sx={{ height: '300px', width: '100%' }}> 
            <Bar data={chartData} options={chartOptions} />
        </Box>
    );
}

export function PieChart() {
    const [chartData, setChartData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchPieChartData = async () => {
            try {
                // Using the imported 'api' instance
                const response = await api.get('/api/charts/pie');
                setChartData(response.data); // Axios puts data in .data
            } catch (err) {
                console.error("Failed to fetch pie chart data:", err);
                setError(err);
            } finally {
                setLoading(false);
            }
        };

        fetchPieChartData();
    }, []);

    if (loading) {
        return <Typography>Loading pie chart...</Typography>;
    }

    if (error) {
        return <Typography color="error">Error loading pie chart: {error.message}</Typography>;
    }

    if (!chartData) {
        return <Typography>No pie chart data available.</Typography>;
    }

     return (
        // *** ADD A PARENT DIV/BOX WITH A DEFINED HEIGHT ***
        // Pie charts often look good in a square or similar aspect ratio
        <Box sx={{ height: '300px', width: '400px' }}> 
            <Pie data={chartData} options={chartOptions} />
        </Box>
    );
}