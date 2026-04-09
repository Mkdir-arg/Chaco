import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, Pressable, Platform, ActivityIndicator, RefreshControl } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../context/ThemeContext';
import StaggeredItem from '../components/StaggeredItem';
import relevamientoService from '../services/relevamientoService';

const statusColor = (estado, colors) => {
    if (estado === 'SINCRONIZADO') return '#2DCE89';
    if (estado === 'SINCRONIZANDO') return colors.accent;
    if (estado === 'ERROR') return '#EA0606';
    return colors.primary; // PENDIENTE
};

const statusIcon = (estado) => {
    if (estado === 'SINCRONIZADO') return 'cloud-done';
    if (estado === 'SINCRONIZANDO') return 'sync';
    if (estado === 'ERROR') return 'alert-circle';
    return 'cloud-upload';
};

export default function RelevamientosScreen({ onStartNewRelevamiento, onOpenRelevamiento }) {
    const { theme, typography } = useTheme();
    const [relevamientos, setRelevamientos] = useState([]);
    const [statusFilter, setStatusFilter] = useState('TODOS');
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState('');
    const filterOptions = [
        { key: 'TODOS', label: 'Todos' },
        { key: 'SINCRONIZADOS', label: 'Sincronizados' },
        { key: 'PENDIENTES', label: 'Pendientes' },
    ];

    const formatDate = (isoDate) => {
        if (!isoDate) return '-';
        try {
            return new Date(isoDate).toLocaleString('es-AR', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
            });
        } catch {
            return isoDate;
        }
    };

    const loadRelevamientos = useCallback(async (silent = false) => {
        if (silent) setRefreshing(true);
        else setLoading(true);
        setError('');

        const result = await relevamientoService.getRelevamientos({ refreshFromRemote: true });
        if (!result.success && result.error) setError(result.error);
        setRelevamientos(result.records || []);

        setLoading(false);
        setRefreshing(false);
    }, []);

    useEffect(() => {
        loadRelevamientos();
    }, [loadRelevamientos]);

    const filteredRelevamientos = useMemo(() => {
        if (statusFilter === 'TODOS') return relevamientos;
        if (statusFilter === 'SINCRONIZADOS') {
            return relevamientos.filter((item) => item.sync_estado === 'SINCRONIZADO');
        }
        if (statusFilter === 'PENDIENTES') {
            return relevamientos.filter((item) => item.sync_estado !== 'SINCRONIZADO');
        }
        return relevamientos;
    }, [relevamientos, statusFilter]);

    return (
        <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
            <ScrollView
                contentContainerStyle={styles.content}
                refreshControl={
                    <RefreshControl
                        refreshing={refreshing}
                        onRefresh={() => loadRelevamientos(true)}
                        colors={[theme.colors.primary]}
                        tintColor={theme.colors.primary}
                    />
                }
            >
                <StaggeredItem index={0}>
                    <View style={styles.titleRow}>
                        <Text style={[styles.sectionTitle, { color: theme.colors.text, fontFamily: typography.bold }]}>
                            Lista de relevamientos
                        </Text>
                        <Pressable onPress={() => loadRelevamientos(true)} style={styles.refreshBtn}>
                            {refreshing ? (
                                <ActivityIndicator size="small" color={theme.colors.primary} />
                            ) : (
                                <Ionicons name="refresh" size={18} color={theme.colors.primary} />
                            )}
                        </Pressable>
                    </View>
                </StaggeredItem>
                <StaggeredItem index={1}>
                    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.filtersRow}>
                        {filterOptions.map((option) => {
                            const selected = statusFilter === option.key;
                            return (
                                <Pressable
                                    key={option.key}
                                    onPress={() => setStatusFilter(option.key)}
                                    style={[
                                        styles.filterChip,
                                        { backgroundColor: theme.colors.surface, borderColor: theme.colors.border },
                                        selected && { backgroundColor: theme.colors.primary, borderColor: theme.colors.primary },
                                    ]}
                                >
                                    <Text
                                        style={[
                                            styles.filterChipText,
                                            { color: theme.colors.text, fontFamily: typography.medium },
                                            selected && { color: '#FFFFFF', fontFamily: typography.bold },
                                        ]}
                                    >
                                        {option.label}
                                    </Text>
                                </Pressable>
                            );
                        })}
                    </ScrollView>
                </StaggeredItem>

                {loading ? (
                    <View style={styles.centerBox}>
                        <ActivityIndicator size="large" color={theme.colors.primary} />
                        <Text style={[styles.infoText, { color: theme.colors.textSoft, fontFamily: typography.medium }]}>
                            Cargando relevamientos...
                        </Text>
                    </View>
                ) : null}

                {!loading && !!error ? (
                    <View style={[styles.messageCard, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
                        <Text style={[styles.infoText, { color: '#EA0606', fontFamily: typography.semibold }]}>
                            {`Sin conexion con el servidor. Mostrando datos locales. (${error})`}
                        </Text>
                    </View>
                ) : null}

                {!loading && filteredRelevamientos.length === 0 ? (
                    <View style={[styles.messageCard, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
                        <Text style={[styles.infoText, { color: theme.colors.textSoft, fontFamily: typography.medium }]}>
                            {error
                                ? 'Sin conexion y no hay relevamientos locales para el filtro seleccionado.'
                                : 'No hay relevamientos para el filtro seleccionado.'}
                        </Text>
                    </View>
                ) : null}

                {!loading && filteredRelevamientos.map((item, index) => (
                    <StaggeredItem key={item.id} index={index + 2}>
                        <Pressable
                            onPress={() => onOpenRelevamiento && onOpenRelevamiento(item.id)}
                            style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}
                        >
                            <View style={styles.headerRow}>
                                <Text style={[styles.idText, { color: theme.colors.textSoft, fontFamily: typography.medium }]}>
                                    {item.id.slice(0, 8).toUpperCase()}
                                </Text>
                                <View style={[styles.statusIconWrap, { backgroundColor: `${statusColor(item.sync_estado, theme.colors)}20` }]}>
                                    <Ionicons
                                        name={statusIcon(item.sync_estado)}
                                        size={16}
                                        color={statusColor(item.sync_estado, theme.colors)}
                                    />
                                </View>
                            </View>

                            <Text style={[styles.title, { color: theme.colors.text, fontFamily: typography.semibold }]}>
                                {item.observaciones?.trim()
                                    ? `Relevamiento: ${item.observaciones.trim().slice(0, 42)}`
                                    : `Relevamiento Institucion #${item.id_institucion}`}
                            </Text>

                            <View style={styles.metaRow}>
                                <Ionicons name="calendar-outline" size={15} color={theme.colors.textSoft} />
                                <Text style={[styles.metaText, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>
                                    {formatDate(item.created_at)}
                                </Text>
                            </View>

                            <View style={styles.metaRow}>
                                <Ionicons name="location-outline" size={15} color={theme.colors.textSoft} />
                                <Text style={[styles.metaText, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>
                                    {item.latitud && item.longitud ? `${item.latitud}, ${item.longitud}` : 'Sin geolocalizacion'}
                                </Text>
                            </View>
                        </Pressable>
                    </StaggeredItem>
                ))}
            </ScrollView>

            <Pressable
                onPress={onStartNewRelevamiento}
                style={[
                    styles.fab,
                    {
                        backgroundColor: theme.colors.primary,
                        shadowColor: theme.colors.shadow,
                    },
                ]}
            >
                <Ionicons name="add" size={30} color="#FFFFFF" />
            </Pressable>
        </View>
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
        marginBottom: 16,
    },
    titleRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    refreshBtn: {
        width: 36,
        height: 36,
        borderRadius: 18,
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 10,
    },
    filtersRow: {
        paddingBottom: 12,
        paddingRight: 8,
    },
    filterChip: {
        borderWidth: 1,
        borderRadius: 999,
        paddingHorizontal: 12,
        paddingVertical: 7,
        marginRight: 8,
    },
    filterChipText: {
        fontSize: 12,
    },
    centerBox: {
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 22,
    },
    messageCard: {
        borderRadius: 14,
        borderWidth: 1,
        padding: 14,
        marginBottom: 10,
    },
    infoText: {
        fontSize: 13,
    },
    card: {
        borderRadius: 20,
        borderWidth: 1,
        padding: 16,
        marginBottom: 12,
    },
    headerRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 8,
    },
    idText: {
        fontSize: 12,
    },
    statusIconWrap: {
        width: 30,
        height: 30,
        borderRadius: 15,
        alignItems: 'center',
        justifyContent: 'center',
    },
    title: {
        fontSize: 16,
        marginBottom: 10,
    },
    metaRow: {
        flexDirection: 'row',
        alignItems: 'center',
        marginTop: 4,
    },
    metaText: {
        fontSize: 13,
        marginLeft: 6,
    },
    fab: {
        position: 'absolute',
        right: 18,
        bottom: Platform.OS === 'ios' ? 10 : 8,
        width: 58,
        height: 58,
        borderRadius: 29,
        alignItems: 'center',
        justifyContent: 'center',
        elevation: 10,
        shadowOffset: { width: 0, height: 6 },
        shadowOpacity: 0.25,
        shadowRadius: 12,
    },
});
