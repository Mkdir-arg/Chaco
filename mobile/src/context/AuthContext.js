import React, { createContext, useState, useContext, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';
import { createClient } from '@supabase/supabase-js';
import Constants from 'expo-constants';

const AuthContext = createContext({});

// Obtener credenciales de Supabase desde app.json
const SUPABASE_URL = Constants.expoConfig?.extra?.supabaseUrl || 'https://tu-proyecto.supabase.co';
const SUPABASE_ANON_KEY = Constants.expoConfig?.extra?.supabaseAnonKey || 'tu-anon-key-aqui';

console.log('🔌 Conectando a Supabase:', SUPABASE_URL);

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

if (!Constants.expoConfig?.extra?.supabaseUrl || !Constants.expoConfig?.extra?.supabaseAnonKey) {
    console.warn('⚠️ ADVERTENCIA: Credenciales de Supabase no configuradas. Revisa app.json');
}

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Al iniciar la app, intentamos recuperar el usuario
        checkAuth();
    }, []);

    const checkAuth = async () => {
        try {
            const userId = await SecureStore.getItemAsync('user_id');
            if (userId) {
                // Obtener datos del usuario desde Supabase
                await fetchUser(userId);
            }
        } catch (e) {
            console.error('Error al recuperar autenticación', e);
        } finally {
            setLoading(false);
        }
    };

    const fetchUser = async (userId) => {
        try {
            const { data: userData, error } = await supabase
                .from('usuarios')
                .select(
                    `
                    id,
                    username,
                    nombre,
                    foto,
                    es_admin,
                    usuario_grupos(
                        grupo_id,
                        grupos(id, nombre, descripcion)
                    )
                `
                )
                .eq('id', userId)
                .eq('activo', true)
                .single();

            if (error || !userData) {
                console.error('Error fetching user:', error);
                logout();
                return;
            }

            const grupos = userData.usuario_grupos?.map((ug) => ug.grupos) || [];

            setUser({
                id: userData.id,
                username: userData.username,
                nombre: userData.nombre,
                foto: userData.foto,
                es_admin: userData.es_admin,
                grupos,
            });
        } catch (e) {
            console.error('Error obteniendo usuario', e);
            logout();
        }
    };

    const login = async (username, password) => {
        try {
            console.log('🔐 Intentando login con usuario:', username);
            
            // Obtener usuario por username
            const { data: userData, error: fetchError } = await supabase
                .from('usuarios')
                .select(
                    `
                    id,
                    username,
                    nombre,
                    foto,
                    es_admin,
                    password,
                    activo,
                    usuario_grupos(
                        grupo_id,
                        grupos(id, nombre, descripcion)
                    )
                `
                )
                .eq('username', username)
                .eq('activo', true)
                .single();

            console.log('📊 Respuesta de Supabase:', { userData, fetchError });

            if (fetchError || !userData) {
                console.error('❌ Error o usuario no encontrado:', fetchError?.message);
                return {
                    success: false,
                    error: fetchError?.message || 'Usuario no encontrado'
                };
            }

            console.log('✅ Usuario encontrado:', userData.username);

            // Comparar contraseña (en producción usar bcrypt en backend)
            if (userData.password !== password) {
                console.error('❌ Contraseña incorrecta');
                return { success: false, error: 'Contraseña incorrecta' };
            }

            console.log('✅ Contraseña correcta');

            // Guardar ID del usuario en almacenamiento seguro
            await SecureStore.setItemAsync('user_id', userData.id);

            const grupos = userData.usuario_grupos?.map((ug) => ug.grupos) || [];

            setUser({
                id: userData.id,
                username: userData.username,
                nombre: userData.nombre,
                foto: userData.foto,
                es_admin: userData.es_admin,
                grupos,
            });

            console.log('✅ Login exitoso para:', username);
            return { success: true };
        } catch (e) {
            console.error('❌ Error en login:', e.message);
            return { success: false, error: 'Hubo un error al conectar con el servidor' };
        }
    };

    const logout = async () => {
        try {
            await SecureStore.deleteItemAsync('user_id');
        } catch (e) {
            console.error('Error removing user_id:', e);
        }
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{
            user,
            loading,
            isAuthenticated: !!user,
            login,
            logout,
        }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
