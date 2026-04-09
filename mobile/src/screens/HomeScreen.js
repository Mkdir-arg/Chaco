import React from 'react';
import { View, Text, StyleSheet, ScrollView, Pressable } from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import MaskedView from '@react-native-masked-view/masked-view';
import StaggeredItem from '../components/StaggeredItem';

const GradientIcon = ({ name, size = 24, style }) => {
    return (
        <View style={[{ width: size, height: size }, style]}>
            <MaskedView
                style={{ flex: 1 }}
                maskElement={
                    <View style={{ backgroundColor: 'transparent', justifyContent: 'center', alignItems: 'center', flex: 1 }}>
                        <Ionicons name={name} size={size} color="black" />
                    </View>
                }
            >
                <LinearGradient
                    colors={theme.colors.gradients?.brand || ['#FF0080', '#7928CA']}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 0, y: 1 }}
                    style={{ flex: 1 }}
                />
            </MaskedView>
        </View>
    );
};

const ACTIONS = [
    { id: 'relevamientos', title: 'Relevamientos', icon: 'clipboard', subtitle: 'Listado y detalle' },
    { id: 'sync', title: 'Sincronizacion', icon: 'cloud-upload', subtitle: 'Enviar pendientes' },
    { id: 'mensajes', title: 'Mensajes', icon: 'chatbubbles', subtitle: 'Bandeja interna' },
    { id: 'notificaciones', title: 'Notificaciones', icon: 'notifications', subtitle: 'Alertas del sistema' },
];

export default function HomeScreen({ onOpenRelevamientos, onSyncPress, onOpenMensajes, onOpenNotificaciones }) {
    const { theme, typography } = useTheme();
    const { user } = useAuth();
    const displayName = user?.username || user?.nombre || 'Usuario';

    const handleActionPress = (actionId) => {
        if (actionId === 'relevamientos') return onOpenRelevamientos?.();
        if (actionId === 'sync') return onSyncPress?.();
        if (actionId === 'mensajes') return onOpenMensajes?.();
        if (actionId === 'notificaciones') return onOpenNotificaciones?.();
    };

    return (
        <ScrollView style={[styles.container, { backgroundColor: theme.colors.background }]} contentContainerStyle={styles.content}>
            <StaggeredItem index={0}>
                <Text style={[styles.sectionTitle, { color: theme.colors.text, fontFamily: typography.bold }]}>
                    Bienvenido, {displayName}
                </Text>
            </StaggeredItem>

            <View style={styles.actionsWrap}>
                {ACTIONS.map((task, index) => (
                    <View key={task.id} style={styles.tileCol}>
                        <StaggeredItem index={index + 1}>
                            <Pressable
                                onPress={() => handleActionPress(task.id)}
                                style={({ pressed }) => [styles.cardWrap, { opacity: pressed ? 0.92 : 1 }]}
                            >
                                <LinearGradient
                                    colors={theme.colors.gradients?.brand || ['#FF0080', '#7928CA']}
                                    start={{ x: 0, y: 0 }}
                                    end={{ x: 1, y: 1 }}
                                    style={[styles.card, { shadowColor: theme.colors.secondary }]}
                                >
                                    <View style={styles.iconBadge}>
                                        <Ionicons name={task.icon} size={26} color="#FFFFFF" />
                                    </View>
                                    <View style={styles.cardTextWrap}>
                                        <Text style={[styles.cardTitle, { color: '#FFFFFF', fontFamily: typography.bold }]}>
                                            {task.title}
                                        </Text>
                                        <Text style={[styles.cardSubtitle, { color: 'rgba(255,255,255,0.9)', fontFamily: typography.medium }]}>
                                            {task.subtitle}
                                        </Text>
                                    </View>
                                </LinearGradient>
                            </Pressable>
                        </StaggeredItem>
                    </View>
                ))}
            </View>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    content: {
        padding: 20,
    },
    sectionTitle: {
        fontSize: 20,
        marginBottom: 20,
    },
    actionsWrap: {
        width: '100%',
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
    },
    tileCol: {
        width: '48%',
    },
    cardWrap: {
        borderRadius: 22,
        marginBottom: 16,
        width: '100%',
        aspectRatio: 1,
    },
    card: {
        width: '100%',
        height: '100%',
        paddingVertical: 22,
        paddingHorizontal: 18,
        borderRadius: 22,
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        shadowColor: '#000000',
        shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.2,
        shadowRadius: 12,
        elevation: 6,
    },
    iconBadge: {
        width: 46,
        height: 46,
        borderRadius: 23,
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'rgba(255,255,255,0.22)',
        marginRight: 14,
    },
    cardTextWrap: {
        width: '100%',
        marginTop: 8,
    },
    cardTitle: {
        fontSize: 19,
        marginBottom: 3,
    },
    cardSubtitle: {
        fontSize: 13,
    },
});
