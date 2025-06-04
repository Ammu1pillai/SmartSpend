// frontend/pages/_app.js
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { theme } from '../styles/theme'; // Your custom theme
import { AuthProvider } from '../context/AuthContext'; // Your AuthContext
import Layout from '../components/Layout';

function MyApp({ Component, pageProps }) {
  return (
    <AuthProvider>
      <ThemeProvider theme={theme}>
        {/* CssBaseline provides a consistent baseline for styling across browsers. */}
        <CssBaseline />
        <Layout>
          <Component {...pageProps} />
        </Layout>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default MyApp;