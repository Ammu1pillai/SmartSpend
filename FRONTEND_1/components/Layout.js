import { ThemeProvider } from '@mui/material/styles';
import { theme } from '../styles/theme';
import { CssBaseline, Container, Box, Typography } from '@mui/material'; // Add Box, Typography
import Head from 'next/head';
import Navigation from './Navigation';

export default function Layout({ children }) {
    return (
        <ThemeProvider theme={theme}>
        <Head>
            <title>SmartSpend Analyzer</title>
            <meta name="description" content="Track and analyze your spending" />
            <link rel="icon" href="/favicon.ico" />
        </Head>

        <CssBaseline />

        <Navigation />

        <Container
            maxWidth="lg"
            sx={{
                mt: 20,
                mb: 4,
                minHeight: 'calc(100vh - 64px - 56px)', // Adjust based on header/footer height
            }}
        >
            {children}
        </Container>

        <Box // This Box was missing
            component="footer"
            sx={{
                py: 3,
                px: 2,
                mt: 'auto',
                backgroundColor: (theme) =>
                theme.palette.mode === 'light'
                    ? theme.palette.grey[200]
                    : theme.palette.grey[800],
            }}
        >
            <Container maxWidth="lg">
                <Typography variant="body2" color="text.secondary" align="center">
                    © {new Date().getFullYear()} SmartSpend Analyzer
                </Typography>
            </Container>
        </Box>
        </ThemeProvider>
    );
}