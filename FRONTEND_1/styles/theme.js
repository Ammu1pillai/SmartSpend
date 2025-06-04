// frontend/styles/theme.js
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'dark', // Enable dark mode
    primary: {
      main: '#D32F2F', // Your deep red
      light: '#FF6659',
      dark: '#9A0007',
      contrastText: '#fff',
    },
    secondary: {
      main: '#B0BEC5', // Silver/gray
      light: '#CFD8DC', // Lighter silver
      dark: '#78909C', // Darker silver
      contrastText: '#000',
    },
    error: {
      main: '#FF1744', // A vivid red for errors
    },
    warning: {
      main: '#FFC107',
    },
    info: {
      main: '#2196F3',
    },
    success: {
      main: '#4CAF50',
    },
    background: {
      default: '#121212', // Very dark gray for overall background
      paper: '#1E1E1E',   // Slightly lighter dark gray for paper components
    },
    text: {
      primary: '#E0E0E0', // Light gray for main text on dark backgrounds
      secondary: '#A0A0A0', // Medium gray for secondary text
      disabled: '#616161',
    },
    action: {
      active: '#B0BEC5',
      hover: 'rgba(255, 102, 89, 0.08)', // Light red hover for interactive elements
      selected: 'rgba(255, 102, 89, 0.16)',
      disabled: 'rgba(255, 255, 255, 0.3)',
      disabledBackground: 'rgba(255, 255, 255, 0.12)',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 700, // Make headings bolder
      marginBottom: '1.5rem',
      color: '#FF6659', // Light red for main headings
    },
    h5: {
      fontWeight: 600,
      color: '#D32F2F', // Deep red for subheadings
    },
    h6: {
      fontWeight: 500,
      color: '#B0BEC5', // Silver for card titles, etc.
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
    body1: {
      color: '#E0E0E0', // Main text
    },
    body2: {
      color: '#A0A0A0', // Secondary text
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12, // More rounded buttons
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            boxShadow: '0px 0px 15px rgba(211, 47, 47, 0.5)', // Red glow on hover
          },
        },
        containedPrimary: {
          // Applying gradient directly to contained primary buttons
          background: 'linear-gradient(45deg, #D32F2F 30%, #FF6659 90%)',
          color: 'white',
          '&:hover': {
            background: 'linear-gradient(45deg, #FF6659 30%, #D32F2F 90%)', // Reverse gradient on hover
            transform: 'translateY(-2px)', // Subtle lift
          },
        },
        outlinedPrimary: {
          borderColor: '#B0BEC5',
          color: '#B0BEC5',
          '&:hover': {
            borderColor: '#FF6659',
            color: '#FF6659',
            backgroundColor: 'rgba(255, 102, 89, 0.08)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            '& fieldset': {
              borderColor: '#757575', // Darker border for text fields
            },
            '&:hover fieldset': {
              borderColor: '#B0BEC5', // Silver on hover
            },
            '&.Mui-focused fieldset': {
              borderColor: '#D32F2F', // Red when focused
            },
            '& input': {
              color: '#E0E0E0', // Input text color
            },
          },
          '& .MuiInputLabel-root': {
            color: '#A0A0A0', // Label color
          },
          '& .MuiInputLabel-root.Mui-focused': {
            color: '#D32F2F', // Focused label color
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 16, // More rounded corners for cards/papers
          boxShadow: '0px 8px 30px rgba(0, 0, 0, 0.3)', // More pronounced shadow for dark theme
          transition: 'transform 0.3s ease-in-out', // Added for hover reveals
          background: '#1E1E1E', // Match background.paper
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0px 8px 30px rgba(0, 0, 0, 0.3)',
          background: '#1E1E1E',
          transition: 'transform 0.3s ease-in-out',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0px 4px 15px rgba(0, 0, 0, 0.4)', // Slightly more shadow for app bar
          borderBottom: 'none', // Remove border for cleaner dark look
          background: '#1a1a1a', // Darker background for app bar
        }
      }
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          background: '#1a1a1a', // Match app bar
          color: '#E0E0E0',
        },
      },
    },
    MuiListItemIcon: {
      styleOverrides: {
        root: {
          color: '#B0BEC5', // Silver icons
        },
      },
    },
    MuiListItemText: {
      styleOverrides: {
        primary: {
          color: '#E0E0E0', // Light gray text for menu items
        },
      },
    },
  },
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 900,
      lg: 1200,
      xl: 1536,
    },
  },
});