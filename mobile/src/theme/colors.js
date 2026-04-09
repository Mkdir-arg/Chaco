import { activeBranding } from '../config/branding';

export const palette = {
    // Brand Colors
    magenta: activeBranding.colors.primary,
    purple: activeBranding.colors.secondary,
    violet: activeBranding.colors.secondary,
    cyan: activeBranding.colors.accent,
    fuchsia: activeBranding.colors.secondary,
    lime: activeBranding.colors.success,

    // Neutrals Light
    text: activeBranding.colors.text,
    textMuted: activeBranding.colors.textMuted,
    textSoft: activeBranding.colors.textSoft,
    border: activeBranding.colors.border,
    background: activeBranding.colors.background,
    surface: activeBranding.colors.surface,

    // Neutrals Dark
    darkBackground: activeBranding.colors.darkBackground,
    darkSurface: activeBranding.colors.darkSurface,
    darkSurfaceAlt: activeBranding.colors.darkSurfaceAlt,
    darkText: activeBranding.colors.darkText,
    darkTextMuted: activeBranding.colors.darkTextMuted,
    darkBorder: activeBranding.colors.darkBorder,

    // System
    error: '#EA0606',
    success: activeBranding.colors.success,
    white: '#FFFFFF',
    black: '#000000',
};

export const lightTheme = {
    mode: 'light',
    colors: {
        primary: palette.magenta,
        secondary: palette.purple,
        accent: palette.cyan,
        success: palette.success,
        background: palette.background,
        surface: palette.surface,
        surfaceAlt: '#F1F3F7',
        text: palette.text,
        textMuted: palette.textMuted,
        textSoft: palette.textSoft,
        border: palette.border,
        icon: activeBranding.colors.icon,
        shadow: '#000000', // Use solid black for shadow color
        gradients: activeBranding.gradients,
        auth: {
            glow: activeBranding.colors.authGlow,
            networkLine: activeBranding.colors.authNetworkLine,
            nodeOuter: activeBranding.colors.authNodeOuter,
            nodeInner: activeBranding.colors.authNodeInner,
            grid: activeBranding.colors.authGrid,
            blobA: activeBranding.colors.authBlobA,
            blobB: activeBranding.colors.authBlobB,
            blobC: activeBranding.colors.authBlobC,
        },
        button: {
            secondary: {
                text: activeBranding.colors.buttonSecondaryText,
                bg: activeBranding.colors.buttonSecondaryBg,
                border: activeBranding.colors.buttonSecondaryBorder,
                hoverBg: activeBranding.colors.buttonSecondaryHoverBg,
            },
            tertiary: {
                text: activeBranding.colors.buttonTertiaryText,
                bg: activeBranding.colors.buttonTertiaryBg,
                border: activeBranding.colors.buttonTertiaryBorder,
                hoverText: activeBranding.colors.buttonTertiaryHoverText,
                hoverBg: activeBranding.colors.buttonTertiaryHoverBg,
                hoverBorder: activeBranding.colors.buttonTertiaryHoverBorder,
                focusText: activeBranding.colors.buttonTertiaryFocusText,
                focusBg: activeBranding.colors.buttonTertiaryFocusBg,
                focusBorder: activeBranding.colors.buttonTertiaryFocusBorder,
            },
            disabled: {
                bg: activeBranding.colors.buttonDisabledBg,
                border: activeBranding.colors.buttonDisabledBorder,
                text: activeBranding.colors.buttonDisabledText,
            },
        },
    }
};

export const darkTheme = {
    mode: 'dark',
    colors: {
        primary: activeBranding.colors.primary,
        secondary: activeBranding.colors.secondary,
        accent: activeBranding.colors.accent,
        success: activeBranding.colors.success,
        background: activeBranding.colors.darkBackground,
        surface: activeBranding.colors.darkSurface,
        surfaceAlt: activeBranding.colors.darkSurfaceAlt,
        text: activeBranding.colors.darkText,
        textMuted: activeBranding.colors.darkTextMuted,
        textSoft: activeBranding.colors.darkTextSoft,
        border: activeBranding.colors.darkBorder,
        icon: activeBranding.colors.icon,
        shadow: '#000000',
        gradients: activeBranding.gradients,
        auth: {
            glow: activeBranding.colors.authGlow,
            networkLine: activeBranding.colors.authNetworkLine,
            nodeOuter: activeBranding.colors.authNodeOuter,
            nodeInner: activeBranding.colors.authNodeInner,
            grid: activeBranding.colors.authGrid,
            blobA: activeBranding.colors.authBlobA,
            blobB: activeBranding.colors.authBlobB,
            blobC: activeBranding.colors.authBlobC,
        },
        button: {
            secondary: {
                text: activeBranding.colors.buttonSecondaryText,
                bg: activeBranding.colors.buttonSecondaryBg,
                border: activeBranding.colors.buttonSecondaryBorder,
                hoverBg: activeBranding.colors.buttonSecondaryHoverBg,
            },
            tertiary: {
                text: activeBranding.colors.buttonTertiaryText,
                bg: activeBranding.colors.buttonTertiaryBg,
                border: activeBranding.colors.buttonTertiaryBorder,
                hoverText: activeBranding.colors.buttonTertiaryHoverText,
                hoverBg: activeBranding.colors.buttonTertiaryHoverBg,
                hoverBorder: activeBranding.colors.buttonTertiaryHoverBorder,
                focusText: activeBranding.colors.buttonTertiaryFocusText,
                focusBg: activeBranding.colors.buttonTertiaryFocusBg,
                focusBorder: activeBranding.colors.buttonTertiaryFocusBorder,
            },
            disabled: {
                bg: activeBranding.colors.buttonDisabledBg,
                border: activeBranding.colors.buttonDisabledBorder,
                text: activeBranding.colors.buttonDisabledText,
            },
        },
    }
};
