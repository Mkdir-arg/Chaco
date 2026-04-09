import { supabase } from '../config/supabaseConfig';
import * as SecureStore from 'expo-secure-store';
import bcrypt from 'bcryptjs';

// Servicio de autenticación
export const authService = {
  // Registrar nuevo usuario
  async register(username, password, nombre, foto = null) {
    try {
      // Hash de la contraseña (recomendado hacer en backend)
      const hashedPassword = await bcrypt.hash(password, 10);

      const { data, error } = await supabase
        .from('usuarios')
        .insert([
          {
            username,
            password: hashedPassword,
            nombre,
            foto,
            es_admin: false,
          },
        ])
        .select()
        .single();

      if (error) throw error;

      return { success: true, user: data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Login de usuario
  async login(username, password) {
    try {
      // Obtener usuario por username
      const { data: users, error } = await supabase
        .from('usuarios')
        .select(
          `
          id,
          username,
          nombre,
          foto,
          es_admin,
          password,
          usuario_grupos(
            grupo_id,
            grupos(id, nombre)
          )
        `
        )
        .eq('username', username)
        .eq('activo', true)
        .single();

      if (error || !users) {
        return { success: false, error: 'Usuario no encontrado' };
      }

      // Comparar contraseña (esto es una simplificación, idealmente usar bcrypt)
      // Para producción, implementar verificación en backend
      if (users.password !== password) {
        return { success: false, error: 'Contraseña incorrecta' };
      }

      // Guardar token/sesión en almacenamiento seguro
      await SecureStore.setItemAsync('user_id', users.id);
      await SecureStore.setItemAsync(
        'user_data',
        JSON.stringify({
          id: users.id,
          username: users.username,
          nombre: users.nombre,
          foto: users.foto,
          es_admin: users.es_admin,
        })
      );

      // Preparar grupo
      const grupos = users.usuario_grupos?.map((ug) => ug.grupos) || [];

      return {
        success: true,
        user: {
          id: users.id,
          username: users.username,
          nombre: users.nombre,
          foto: users.foto,
          es_admin: users.es_admin,
          grupos,
        },
      };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Logout
  async logout() {
    try {
      await SecureStore.deleteItemAsync('user_id');
      await SecureStore.deleteItemAsync('user_data');
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Obtener usuario actual
  async getCurrentUser() {
    try {
      const userId = await SecureStore.getItemAsync('user_id');
      if (!userId) return null;

      const { data: user, error } = await supabase
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
            grupos(id, nombre)
          )
        `
        )
        .eq('id', userId)
        .single();

      if (error) return null;

      const grupos = user.usuario_grupos?.map((ug) => ug.grupos) || [];

      return {
        id: user.id,
        username: user.username,
        nombre: user.nombre,
        foto: user.foto,
        es_admin: user.es_admin,
        grupos,
      };
    } catch (error) {
      console.error('Error getting current user:', error);
      return null;
    }
  },

  // Asignar grupo a usuario
  async addGroupToUser(userId, groupId) {
    try {
      const { data, error } = await supabase
        .from('usuario_grupos')
        .insert([{ usuario_id: userId, grupo_id: groupId }])
        .select();

      if (error) throw error;
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Remover grupo de usuario
  async removeGroupFromUser(userId, groupId) {
    try {
      const { error } = await supabase
        .from('usuario_grupos')
        .delete()
        .eq('usuario_id', userId)
        .eq('grupo_id', groupId);

      if (error) throw error;
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Obtener grupos disponibles
  async getGroups() {
    try {
      const { data, error } = await supabase
        .from('grupos')
        .select('*')
        .order('nombre');

      if (error) throw error;
      return { success: true, groups: data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },
};
