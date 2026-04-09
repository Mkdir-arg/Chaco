import React, { useState } from 'react';
import { View, Text, TextInput, Pressable, StyleSheet, Image, ScrollView, KeyboardAvoidingView, Platform, TouchableWithoutFeedback, Keyboard, Alert } from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import CustomButton from '../components/CustomButton';
import { supabase } from '../context/AuthContext';

export default function RegisterScreen({ onBackToLogin }) {
    const { theme, typography, isDark, branding } = useTheme();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [nombre, setNombre] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [error, setError] = useState('');
    const [isRegistering, setIsRegistering] = useState(false);

    const handleRegister = async () => {
        setError('');

        const trimmedUsername = username.trim();
        const trimmedPassword = password.trim();
        const trimmedNombre = nombre.trim();

        // Validaciones
        if (!trimmedUsername || !trimmedPassword || !trimmedNombre || !confirmPassword.trim()) {
            setError('Por favor, completa todos los campos');
            return;
        }

        if (trimmedUsername.length < 3) {
            setError('El usuario debe tener al menos 3 caracteres');
            return;
        }

        if (trimmedPassword.length < 6) {
            setError('La contraseña debe tener al menos 6 caracteres');
            return;
        }

        if (trimmedPassword !== confirmPassword.trim()) {
            setError('Las contraseñas no coinciden');
            return;
        }

        setIsRegistering(true);

        try {
            // Verificar si el usuario ya existe
            const { data: existingUser } = await supabase
                .from('usuarios')
                .select('id')
                .eq('username', trimmedUsername)
                .single();

            if (existingUser) {
                setError('Este usuario ya está registrado');
                setIsRegistering(false);
                return;
            }

            // Crear nuevo usuario
            const { data, error: insertError } = await supabase
                .from('usuarios')
                .insert([
                    {
                        username: trimmedUsername,
                        password: trimmedPassword, // En producción, hashear con bcrypt
                        nombre: trimmedNombre,
                        es_admin: false,
                        foto: null,
                        activo: true,
                    },
                ])
                .select()
                .single();

            if (insertError) {
                setError('Error al crear el usuario: ' + insertError.message);
                return;
            }

            // Mostrar alerta de éxito
            Alert.alert('Registro exitoso', 'Tu cuenta ha sido creada. Ahora inicia sesión.', [
                {
                    text: 'OK',
                    onPress: () => {
                        // Limpiar y volver a login
                        setUsername('');
                        setPassword('');
                        setConfirmPassword('');
                        setNombre('');
                        onBackToLogin();
                    },
                },
            ]);
        } catch (err) {
            setError('Error al registrar: ' + err.message);
        } finally {
            setIsRegistering(false);
        }
    };

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
            style={[styles.container, { backgroundColor: theme.colors.background }]}
        >
            <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
                <ScrollView
                    contentContainerStyle={styles.scrollContent}
                    bounces={false}
                    keyboardShouldPersistTaps="handled"
                >
                    <View style={styles.header}>
                        <Pressable onPress={onBackToLogin} style={styles.backButton}>
                            <Ionicons name="chevron-back" size={24} color={theme.colors.text} />
                        </Pressable>
                        <Text style={[styles.title, { fontFamily: typography.bold, color: theme.colors.text }]}>
                            Crear Cuenta
                        </Text>
                        <Text style={[styles.subtitle, { fontFamily: typography.regular, color: theme.colors.textMuted }]}>
                            {branding.registerSubtitle}
                        </Text>
                    </View>

                    <View style={styles.form}>
                        {!!error && (
                            <View style={styles.errorContainer}>
                                <Text style={[styles.errorText, { fontFamily: typography.medium }]}>{error}</Text>
                            </View>
                        )}

                        <View style={styles.inputGroup}>
                            <Text style={[styles.label, { fontFamily: typography.semibold, color: theme.colors.textSoft }]}>
                                NOMBRE COMPLETO
                            </Text>
                            <View
                                style={[
                                    styles.input,
                                    { borderColor: theme.colors.border, backgroundColor: isDark ? theme.colors.surface : '#F8F9FA' },
                                    !!error && nombre === '' && styles.inputError,
                                ]}
                            >
                                <TextInput
                                    placeholder="Tu nombre"
                                    placeholderTextColor={isDark ? theme.colors.textSoft : '#A0A0A0'}
                                    style={[styles.field, { fontFamily: typography.regular, color: theme.colors.text }]}
                                    value={nombre}
                                    onChangeText={(text) => {
                                        setNombre(text);
                                        setError('');
                                    }}
                                />
                            </View>
                        </View>

                        <View style={styles.inputGroup}>
                            <Text style={[styles.label, { fontFamily: typography.semibold, color: theme.colors.textSoft }]}>
                                USUARIO
                            </Text>
                            <View
                                style={[
                                    styles.input,
                                    { borderColor: theme.colors.border, backgroundColor: isDark ? theme.colors.surface : '#F8F9FA' },
                                    !!error && username === '' && styles.inputError,
                                ]}
                            >
                                <TextInput
                                    placeholder="tu_usuario"
                                    placeholderTextColor={isDark ? theme.colors.textSoft : '#A0A0A0'}
                                    style={[styles.field, { fontFamily: typography.regular, color: theme.colors.text }]}
                                    autoCapitalize="none"
                                    value={username}
                                    onChangeText={(text) => {
                                        setUsername(text);
                                        setError('');
                                    }}
                                />
                            </View>
                        </View>

                        <View style={styles.inputGroup}>
                            <Text style={[styles.label, { fontFamily: typography.semibold, color: theme.colors.textSoft }]}>
                                CONTRASEÑA
                            </Text>
                            <View
                                style={[
                                    styles.input,
                                    styles.passwordInputWrapper,
                                    { borderColor: theme.colors.border, backgroundColor: isDark ? theme.colors.surface : '#F8F9FA' },
                                    !!error && password === '' && styles.inputError,
                                ]}
                            >
                                <TextInput
                                    placeholder="••••••••"
                                    placeholderTextColor={isDark ? theme.colors.textSoft : '#A0A0A0'}
                                    secureTextEntry={!showPassword}
                                    style={[styles.field, { fontFamily: typography.regular, color: theme.colors.text }]}
                                    value={password}
                                    onChangeText={(text) => {
                                        setPassword(text);
                                        setError('');
                                    }}
                                />
                                <Pressable onPress={() => setShowPassword(!showPassword)} style={styles.eyeIcon}>
                                    <Ionicons
                                        name={showPassword ? 'eye-off-outline' : 'eye-outline'}
                                        size={22}
                                        color={theme.colors.textSoft}
                                    />
                                </Pressable>
                            </View>
                        </View>

                        <View style={styles.inputGroup}>
                            <Text style={[styles.label, { fontFamily: typography.semibold, color: theme.colors.textSoft }]}>
                                CONFIRMAR CONTRASEÑA
                            </Text>
                            <View
                                style={[
                                    styles.input,
                                    styles.passwordInputWrapper,
                                    { borderColor: theme.colors.border, backgroundColor: isDark ? theme.colors.surface : '#F8F9FA' },
                                    !!error && confirmPassword === '' && styles.inputError,
                                ]}
                            >
                                <TextInput
                                    placeholder="••••••••"
                                    placeholderTextColor={isDark ? theme.colors.textSoft : '#A0A0A0'}
                                    secureTextEntry={!showConfirmPassword}
                                    style={[styles.field, { fontFamily: typography.regular, color: theme.colors.text }]}
                                    value={confirmPassword}
                                    onChangeText={(text) => {
                                        setConfirmPassword(text);
                                        setError('');
                                    }}
                                />
                                <Pressable onPress={() => setShowConfirmPassword(!showConfirmPassword)} style={styles.eyeIcon}>
                                    <Ionicons
                                        name={showConfirmPassword ? 'eye-off-outline' : 'eye-outline'}
                                        size={22}
                                        color={theme.colors.textSoft}
                                    />
                                </Pressable>
                            </View>
                        </View>

                        <CustomButton
                            title="REGISTRARSE"
                            onPress={handleRegister}
                            loading={isRegistering}
                            size="L"
                            style={styles.buttonMargin}
                        />

                        <View style={styles.loginLinkContainer}>
                            <Text style={[styles.loginLinkText, { fontFamily: typography.regular, color: theme.colors.textMuted }]}>
                                ¿Ya tienes cuenta?{' '}
                            </Text>
                            <Pressable onPress={onBackToLogin}>
                                <Text style={[styles.loginLink, { fontFamily: typography.semibold, color: theme.colors.primary }]}>
                                    Inicia sesión
                                </Text>
                            </Pressable>
                        </View>
                    </View>
                </ScrollView>
            </TouchableWithoutFeedback>
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    scrollContent: {
        flexGrow: 1,
        padding: 24,
        justifyContent: 'center',
    },
    header: {
        marginBottom: 40,
        paddingTop: 20,
    },
    backButton: {
        marginBottom: 16,
        width: 40,
        height: 40,
        justifyContent: 'center',
    },
    title: {
        fontSize: 32,
        marginBottom: 8,
    },
    subtitle: {
        fontSize: 16,
    },
    form: {
        width: '100%',
    },
    errorContainer: {
        backgroundColor: '#FEE2E2',
        padding: 12,
        borderRadius: 12,
        marginBottom: 20,
        borderWidth: 1,
        borderColor: '#EF4444',
    },
    errorText: {
        color: '#B91C1C',
        fontSize: 14,
        textAlign: 'center',
    },
    inputGroup: {
        marginBottom: 20,
    },
    label: {
        fontSize: 12,
        color: '#8392AB',
        marginBottom: 10,
        letterSpacing: 1.5,
    },
    input: {
        height: 56,
        borderWidth: 1,
        borderRadius: 16,
        paddingHorizontal: 16,
    },
    passwordInputWrapper: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    eyeIcon: {
        padding: 8,
    },
    inputError: {
        borderColor: '#EF4444',
    },
    field: {
        flex: 1,
        fontSize: 16,
    },
    buttonMargin: {
        marginTop: 10,
    },
    loginLinkContainer: {
        flexDirection: 'row',
        justifyContent: 'center',
        marginTop: 20,
    },
    loginLinkText: {
        fontSize: 14,
    },
    loginLink: {
        fontSize: 14,
    },
});
