import { View, Text, StyleSheet, Platform, Pressable, ImageBackground, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../context/ThemeContext';

export default function Banner({
    title,
    syncStatus = 'synced',
    syncPendingCount = 0,
    onSyncPress,
    showBackButton = false,
    onBackPress,
}) {
    const { theme, typography, branding } = useTheme();
    const isSynced = syncStatus === 'synced';
    const isSyncing = syncStatus === 'syncing';
    const useSolidBanner = branding.banner?.mode === 'solid';

    const bannerContent = (
        <SafeAreaView>
            <View style={styles.content}>
                <View style={styles.headerRow}>
                    <View style={styles.leftHeaderGroup}>
                        {showBackButton ? (
                            <TouchableOpacity onPress={onBackPress} style={styles.backBtn}>
                                <Ionicons name="chevron-back" size={22} color="#FFF" />
                            </TouchableOpacity>
                        ) : null}
                        <Text style={[styles.title, { color: '#FFF', fontFamily: typography.extrabold }]}>
                            {title.toUpperCase()}
                        </Text>
                    </View>

                    <View style={styles.iconGroup}>
                        <Pressable style={styles.iconButton} onPress={onSyncPress}>
                            <Ionicons
                                name={isSyncing ? 'sync' : (isSynced ? 'cloud-done' : 'cloud-upload')}
                                size={28}
                                color={isSyncing ? theme.colors.accent : (isSynced ? theme.colors.success : theme.colors.warning)}
                            />
                            {syncPendingCount > 0 ? (
                                <View style={[styles.syncBadge, { borderColor: '#FFF', backgroundColor: theme.colors.primary }]}>
                                    <Text style={[styles.syncBadgeText, { fontFamily: typography.bold }]}>
                                        {syncPendingCount > 99 ? '99+' : syncPendingCount}
                                    </Text>
                                </View>
                            ) : null}
                        </Pressable>

                        <Pressable style={styles.notificationContainer}>
                            <Ionicons name="notifications-outline" size={26} color="#FFF" />
                            <View style={[
                                styles.badge,
                                {
                                    borderColor: '#FFF',
                                    backgroundColor: '#EA0606',
                                }
                            ]}>
                                <Text style={[styles.badgeText, { fontFamily: typography.bold }]}>2</Text>
                            </View>
                        </Pressable>
                    </View>
                </View>
            </View>
        </SafeAreaView>
    );

    return (
        <View style={styles.shadowContainer}>
            {useSolidBanner ? (
                <View
                    style={[
                        styles.container,
                        {
                            backgroundColor: branding.banner?.color || theme.colors.primary,
                            borderBottomWidth: 1,
                            borderBottomColor: theme.colors.border,
                        },
                    ]}
                >
                    {bannerContent}
                </View>
            ) : (
                <ImageBackground
                    source={branding.assets.bannerBackground}
                    style={[
                        styles.container,
                        {
                            borderBottomWidth: 1,
                            borderBottomColor: theme.colors.border,
                        },
                    ]}
                    imageStyle={{ opacity: 1 }}
                    resizeMode="cover"
                >
                    {bannerContent}
                </ImageBackground>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    shadowContainer: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.2,
        shadowRadius: 10,
        elevation: 10,
        zIndex: 10,
    },
    container: {
        paddingTop: Platform.OS === 'android' ? 28 : 6,
        paddingBottom: 14,
        borderBottomLeftRadius: 24,
        borderBottomRightRadius: 24,
        overflow: 'hidden',
    },
    content: {
        paddingHorizontal: 24,
    },
    headerRow: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    leftHeaderGroup: {
        flexDirection: 'row',
        alignItems: 'center',
        flexShrink: 1,
    },
    backBtn: {
        width: 30,
        height: 30,
        borderRadius: 15,
        backgroundColor: 'rgba(0,0,0,0.2)',
        alignItems: 'center',
        justifyContent: 'center',
        marginRight: 10,
    },
    title: {
        fontSize: 22,
        letterSpacing: 4,
        textShadowColor: 'rgba(0, 0, 0, 0.1)',
        textShadowOffset: { width: 0, height: 2 },
        textShadowRadius: 4,
    },
    notificationContainer: {
        position: 'relative',
        padding: 4,
    },
    iconGroup: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    iconButton: {
        padding: 4,
        marginRight: 8,
        position: 'relative',
    },
    syncBadge: {
        position: 'absolute',
        top: -2,
        right: -4,
        minWidth: 16,
        height: 16,
        borderRadius: 8,
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 1.5,
        paddingHorizontal: 3,
    },
    syncBadgeText: {
        color: '#FFF',
        fontSize: 9,
        lineHeight: 10,
    },
    badge: {
        position: 'absolute',
        top: 0,
        right: 0,
        minWidth: 18,
        height: 18,
        borderRadius: 9,
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 1.5,
    },
    badgeText: {
        color: '#FFF',
        fontSize: 10,
        textAlign: 'center',
    },
});
