import React, { createContext, useContext, useState, useMemo, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { lightTheme, darkTheme, typography } from '../theme';
import { activeBranding, activeBrandProfile } from '../config/branding';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
    const [themeMode, setThemeMode] = useState('light');

    useEffect(() => {
        const loadTheme = async () => {
            const storedTheme = await AsyncStorage.getItem('themeMode');
            if (storedTheme) {
                setThemeMode(storedTheme);
            }
        };
        loadTheme();
    }, []);

    const toggleTheme = async () => {
        const nextMode = themeMode === 'light' ? 'dark' : 'light';
        setThemeMode(nextMode);
        await AsyncStorage.setItem('themeMode', nextMode);
    };

    const currentTheme = useMemo(() => {
        return themeMode === 'dark' ? darkTheme : lightTheme;
    }, [themeMode]);

    const value = {
        theme: currentTheme,
        isDark: themeMode === 'dark',
        toggleTheme,
        typography,
        branding: activeBranding,
        brandProfile: activeBrandProfile,
    };

    return (
        <ThemeContext.Provider value={value}>
            {children}
        </ThemeContext.Provider>
    );
};

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
};
