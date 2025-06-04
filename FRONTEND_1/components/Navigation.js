// frontend/components/Navigation.js
// This component should ONLY be responsible for the AppBar (header) and the Drawer menu.

import { useState } from 'react';
import { AppBar, Toolbar, Typography, Button, IconButton, Drawer, List, ListItem, ListItemIcon, ListItemText, Box, useMediaQuery } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import HomeIcon from '@mui/icons-material/Home';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import LoginIcon from '@mui/icons-material/Login';
import LogoutIcon from '@mui/icons-material/Logout';
import AppRegistrationIcon from '@mui/icons-material/AppRegistration';
// AssessmentIcon can be removed if not directly used in Navigation's UI
import { useRouter } from 'next/router';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { theme } from '../styles/theme'; // Ensure your theme object is correctly imported

// This component should NOT receive 'children' prop as it's not a layout wrapper
export default function Navigation() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const router = useRouter();
  const { user, logout } = useAuth();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const toggleDrawer = (open) => (event) => {
    if (event.type === 'keydown' && (event.key === 'Tab' || event.key === 'Shift')) {
      return;
    }
    setDrawerOpen(open);
  };

  const navItems = [
    { text: 'Dashboard', icon: <HomeIcon />, path: '/', requiresAuth: true },
    { text: 'Upload Receipt', icon: <CloudUploadIcon />, path: '/upload', requiresAuth: true },
    { text: 'Profile', icon: <AccountCircleIcon />, path: '/profile', requiresAuth: true },
    { text: 'Login', icon: <LoginIcon />, path: '/login', requiresAuth: false, showIfLoggedIn: false },
    { text: 'Sign Up', icon: <AppRegistrationIcon />, path: '/signup', requiresAuth: false, showIfLoggedIn: false },
  ];

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  const drawerList = () => (
    <Box
      sx={{ width: 250 }}
      role="presentation"
      onClick={toggleDrawer(false)}
      onKeyDown={toggleDrawer(false)}
    >
      <List>
        {navItems.map((item) => {
          if ((item.requiresAuth && user?.isLoggedIn) ||
              (!item.requiresAuth && !user?.isLoggedIn && item.showIfLoggedIn !== true)) {
            return (
              <ListItem
                button
                key={item.text}
                component={Link}
                href={item.path}
                passHref
              >
                <ListItemIcon sx={{ color: 'secondary.light' }}>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} sx={{ color: 'text.primary' }} />
              </ListItem>
            );
          }
          return null;
        })}
        {user?.isLoggedIn && (
          <ListItem button onClick={handleLogout}>
            <ListItemIcon sx={{ color: 'secondary.light' }}><LogoutIcon /></ListItemIcon>
            <ListItemText primary="Logout" sx={{ color: 'text.primary' }} />
          </ListItem>
        )}
      </List>
    </Box>
  );

  return (
    // Only return the AppBar and Drawer.
    // REMOVE all ThemeProvider, CssBaseline, Head, main Box, and Footer elements.
    <>
      <AppBar position="static" sx={{ background: 'linear-gradient(90deg, #D32F2F 0%, #1a1a1a 100%)' }}>
        <Toolbar>
          {isMobile && (
            <IconButton
              size="large"
              edge="start"
              color="inherit"
              aria-label="menu"
              sx={{ mr: 2 }}
              onClick={toggleDrawer(true)}
            >
              <MenuIcon />
            </IconButton>
          )}
          <Typography
            variant="h6"
            component={Link}
            href="/"
            sx={{
              flexGrow: 1,
              cursor: 'pointer',
              color: 'white',
              textDecoration: 'none',
              '&:hover': { color: theme.palette.primary.light }
            }}
          >
            SmartSpend
          </Typography>

          {!isMobile && (
            <Box>
              {navItems.map((item) => {
                if ((item.requiresAuth && user?.isLoggedIn) ||
                    (!item.requiresAuth && !user?.isLoggedIn && item.showIfLoggedIn !== true)) {
                  return (
                    <motion.div
                        key={item.text}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        style={{ display: 'inline-block' }}
                    >
                      <Button
                        color="inherit"
                        component={Link}
                        href={item.path}
                        passHref
                        sx={{ mx: 1 }}
                      >
                        {item.icon} <span style={{ marginLeft: 5 }}>{item.text}</span>
                      </Button>
                    </motion.div>
                  );
                }
                return null;
              })}
              {user?.isLoggedIn && (
                <motion.div
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    style={{ display: 'inline-block' }}
                >
                  <Button color="inherit" onClick={handleLogout} sx={{ mx: 1 }}>
                      <LogoutIcon /> <span style={{ marginLeft: 5 }}>Logout</span>
                  </Button>
                </motion.div>
              )}
            </Box>
          )}
        </Toolbar>
      </AppBar>
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={toggleDrawer(false)}
      >
        {drawerList()}
      </Drawer>
    </>
  );
}