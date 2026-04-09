import React from 'react';
import { View, Text, StyleSheet, Pressable, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../context/ThemeContext';

export default function BottomNav({ activeTab, onTabPress, onOpenSettings }) {
    const { theme, typography } = useTheme();

    const tabs = [
        { id: 'Inicio', icon: 'home' },
    ];

    return (
        <View style={[styles.container, { backgroundColor: theme.colors.surface, borderTopColor: theme.colors.border }]}>
            <View style={styles.content}>
                {tabs.map((tab) => {
                    const isActive = activeTab === tab.id;
                    return (
                        <Pressable
                            key={tab.id}
                            onPress={() => onTabPress(tab.id)}
                            style={styles.tabItem}
                        >
                            <Ionicons
                                name={isActive ? tab.icon : tab.icon + '-outline'}
                                size={24}
                                color={isActive ? theme.colors.primary : theme.colors.textSoft}
                            />
                            <Text style={[
                                styles.tabLabel,
                                {
                                    color: isActive ? theme.colors.primary : theme.colors.textSoft,
                                    fontFamily: isActive ? typography.bold : typography.medium
                                }
                            ]}>
                                {tab.id}
                            </Text>
                        </Pressable>
                    );
                })}

                <Pressable onPress={onOpenSettings} style={styles.tabItem}>
                    <Ionicons name="menu" size={28} color={theme.colors.text} />
                    <Text style={[
                        styles.tabLabel,
                        { color: theme.colors.text, fontFamily: typography.medium }
                    ]}>
                        Menú
                    </Text>
                </Pressable>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        height: Platform.OS === 'ios' ? 90 : 70,
        borderTopWidth: 1,
        paddingBottom: Platform.OS === 'ios' ? 25 : 0,
        backgroundColor: '#FFFFFF',
        // Fallback for solid shadow color to avoid native crash if palette fails
        shadowColor: '#000',
        shadowOffset: { width: 0, height: -4 },
        shadowOpacity: 0.05,
        shadowRadius: 10,
        elevation: 20,
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
    },
    content: {
        flex: 1,
        flexDirection: 'row',
        justifyContent: 'space-around',
        alignItems: 'center',
    },
    tabItem: {
        alignItems: 'center',
        justifyContent: 'center',
        paddingTop: 8,
    },
    tabLabel: {
        fontSize: 10,
        marginTop: 4,
    },
});
