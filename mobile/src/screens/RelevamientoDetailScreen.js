import React, { useEffect, useMemo, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator, Image, Pressable, Alert, Modal } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Svg, { Path } from 'react-native-svg';
import * as FileSystemLegacy from 'expo-file-system/legacy';
import * as Sharing from 'expo-sharing';
import * as WebBrowser from 'expo-web-browser';
import { useTheme } from '../context/ThemeContext';
import Banner from '../components/Banner';
import relevamientoService from '../services/relevamientoService';
import { supabase } from '../config/supabaseConfig';

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

export default function RelevamientoDetailScreen({ relevamientoId, onClose, syncStatus = 'synced', syncPendingCount = 0, onSyncPress }) {
  const { theme, typography } = useTheme();
  const [activeTab, setActiveTab] = useState('RESUMEN');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [detail, setDetail] = useState(null);
  const [imageUrls, setImageUrls] = useState({});
  const [mapProviderIndex, setMapProviderIndex] = useState(0);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewUri, setPreviewUri] = useState('');
  const [previewName, setPreviewName] = useState('');
  const [sharingId, setSharingId] = useState('');

  useEffect(() => {
    let mounted = true;
    (async () => {
      const result = await relevamientoService.getRelevamientoDetail(relevamientoId);
      if (!mounted) return;
      if (!result.success) {
        setError(result.error || 'No se pudo cargar el detalle.');
      } else {
        setDetail(result.detail);
      }
      setLoading(false);
    })();
    return () => { mounted = false; };
  }, [relevamientoId]);

  const readValue = (...keys) => {
    for (const key of keys) {
      const value = detail?.[key] ?? detail?.payload?.[key];
      if (value !== undefined && value !== null && String(value).trim() !== '') {
        return String(value);
      }
    }
    return '-';
  };

  const signaturePaths = useMemo(
    () => detail?.firma_paths || detail?.payload?.firma_paths || [],
    [detail]
  );

  const attachments = detail?.adjuntos || [];
  const imageAttachments = attachments.filter((item) => item.tipo_archivo === 'IMAGEN');
  const docAttachments = attachments.filter((item) => item.tipo_archivo !== 'IMAGEN');
  const lat = readValue('latitud');
  const lng = readValue('longitud');
  const hasGeo = lat !== '-' && lng !== '-';
  const mapPreviewUrls = hasGeo
    ? [
      `https://staticmap.openstreetmap.de/staticmap.php?center=${lat},${lng}&zoom=16&size=800x420&markers=${lat},${lng},red-pushpin`,
      `https://static-maps.yandex.ru/1.x/?ll=${lng},${lat}&size=650,300&z=16&l=map&pt=${lng},${lat},pm2rdm&lang=es_ES`,
    ]
    : [];
  const mapPreviewUrl = mapPreviewUrls[mapProviderIndex] || null;

  const getSignatureBounds = (paths) => {
    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;
    paths.forEach((path) => {
      const nums = path.match(/-?\d+(\.\d+)?/g);
      if (!nums) return;
      for (let i = 0; i < nums.length; i += 2) {
        const x = parseFloat(nums[i]);
        const y = parseFloat(nums[i + 1]);
        if (Number.isNaN(x) || Number.isNaN(y)) continue;
        minX = Math.min(minX, x);
        minY = Math.min(minY, y);
        maxX = Math.max(maxX, x);
        maxY = Math.max(maxY, y);
      }
    });
    if (!Number.isFinite(minX) || !Number.isFinite(minY) || !Number.isFinite(maxX) || !Number.isFinite(maxY)) return null;
    return { minX, minY, width: Math.max(1, maxX - minX), height: Math.max(1, maxY - minY) };
  };

  const getCenteredSignaturePaths = (paths, targetWidth = 320, targetHeight = 190, padding = 14) => {
    const bounds = getSignatureBounds(paths);
    if (!bounds) return paths;
    const scaleX = (targetWidth - padding * 2) / bounds.width;
    const scaleY = (targetHeight - padding * 2) / bounds.height;
    const scale = Math.min(scaleX, scaleY);
    const offsetX = (targetWidth - bounds.width * scale) / 2 - bounds.minX * scale;
    const offsetY = (targetHeight - bounds.height * scale) / 2 - bounds.minY * scale;
    return paths.map((path) =>
      path.replace(/(-?\d+(\.\d+)?),(-?\d+(\.\d+)?)/g, (_, x, __, y) => {
        const nx = parseFloat(x) * scale + offsetX;
        const ny = parseFloat(y) * scale + offsetY;
        return `${nx.toFixed(2)},${ny.toFixed(2)}`;
      })
    );
  };

  useEffect(() => {
    let mounted = true;
    const resolveImageUris = async () => {
      const nextMap = {};
      for (const item of imageAttachments) {
        const raw = item.storage_path || '';
        if (!raw) continue;
        if (raw.startsWith('http://') || raw.startsWith('https://') || raw.startsWith('file://') || raw.startsWith('content://')) {
          nextMap[item.id || raw] = raw;
          continue;
        }
        try {
          const { data } = await supabase.storage.from(item.storage_bucket || 'relevamientos').createSignedUrl(raw, 3600);
          if (data?.signedUrl) nextMap[item.id || raw] = data.signedUrl;
        } catch {
          // ignore
        }
      }
      if (mounted) setImageUrls(nextMap);
    };
    resolveImageUris();
    return () => { mounted = false; };
  }, [detail]);

  const resolveAttachmentUrl = async (item) => {
    const raw = item?.storage_path || '';
    if (!raw) return '';
    if (
      raw.startsWith('http://') ||
      raw.startsWith('https://') ||
      raw.startsWith('file://') ||
      raw.startsWith('content://')
    ) {
      return encodeURI(raw);
    }
    const { data } = await supabase.storage
      .from(item.storage_bucket || 'relevamientos')
      .createSignedUrl(raw, 3600);
    return data?.signedUrl || '';
  };

  const sanitizeFileName = (name = 'archivo') =>
    String(name).replace(/[\\/:*?"<>|]/g, '_').trim() || `archivo_${Date.now()}`;

  const openImagePreview = async (item) => {
    try {
      const url = imageUrls[item.id || item.storage_path] || await resolveAttachmentUrl(item);
      if (!url) throw new Error('No se pudo abrir la imagen');
      setPreviewUri(url);
      setPreviewName(item?.nombre_original || 'Imagen');
      setPreviewVisible(true);
    } catch (e) {
      Alert.alert('Imagen', e?.message || 'No se pudo abrir la imagen');
    }
  };

  const previewDocumentInApp = async (item) => {
    try {
      const url = await resolveAttachmentUrl(item);
      if (!url) throw new Error('No se pudo abrir el documento');
      await WebBrowser.openBrowserAsync(url, { showTitle: true, enableDefaultShareMenuItem: false });
    } catch (e) {
      Alert.alert('Documento', e?.message || 'No se pudo abrir el documento');
    }
  };

  const shareAttachment = async (item) => {
    const id = String(item?.id || item?.storage_path || Math.random());
    try {
      setSharingId(id);
      const canShare = await Sharing.isAvailableAsync();
      if (!canShare) throw new Error('Compartir no disponible en este dispositivo');
      const url = await resolveAttachmentUrl(item);
      if (!url) throw new Error('Adjunto sin URL');
      const fileName = sanitizeFileName(item?.nombre_original || 'adjunto');
      const localUri = `${FileSystemLegacy.cacheDirectory}${Date.now()}_${fileName}`;
      const result = await FileSystemLegacy.downloadAsync(url, localUri);
      if (!result?.uri) throw new Error('No se pudo preparar el archivo');
      await Sharing.shareAsync(result.uri);
    } catch (e) {
      Alert.alert('Compartir', e?.message || 'No se pudo compartir el adjunto');
    } finally {
      setSharingId('');
    }
  };

  const tabs = ['RESUMEN', 'ADJUNTOS', 'FIRMA'];
  const createdDateLabel = formatDate(detail?.created_at || detail?.relevado_at);
  const syncedDateLabel = detail?.last_synced_at
    ? formatDate(detail?.last_synced_at)
    : (readValue('sync_estado') === 'SINCRONIZADO' ? formatDate(detail?.created_at) : 'Pendiente');

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.bannerWrap}>
        <Banner
          title="Detalle"
          syncStatus={syncStatus}
          syncPendingCount={syncPendingCount}
          onSyncPress={onSyncPress}
          showBackButton
          onBackPress={onClose}
        />
      </View>

      <View style={styles.tabsRow}>
        {tabs.map((tab) => {
          const selected = activeTab === tab;
          return (
            <Pressable
              key={tab}
              onPress={() => setActiveTab(tab)}
              style={[
                styles.tabChip,
                { backgroundColor: theme.colors.surface, borderColor: theme.colors.border },
                selected && { backgroundColor: theme.colors.primary, borderColor: theme.colors.primary },
              ]}
            >
              <Text
                style={[
                  styles.tabChipText,
                  { color: theme.colors.text, fontFamily: typography.medium },
                  selected && { color: '#FFFFFF', fontFamily: typography.bold },
                ]}
              >
                {tab}
              </Text>
            </Pressable>
          );
        })}
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {loading ? (
          <ActivityIndicator size="large" color={theme.colors.primary} />
        ) : error ? (
          <Text style={{ color: '#EA0606', fontFamily: typography.semibold }}>{error}</Text>
        ) : (
          <>
            {activeTab === 'RESUMEN' && (
              <>
                <View style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
                  <Text style={[styles.cardTitle, { color: theme.colors.text, fontFamily: typography.bold }]}>General</Text>
                  <View style={styles.kvRow}><Text style={[styles.k, { color: theme.colors.text, fontFamily: typography.semibold }]}>ID</Text><Text style={[styles.v, { color: theme.colors.textSoft, fontFamily: typography.medium }]}>{readValue('id', 'local_id')}</Text></View>
                  <View style={styles.kvRow}><Text style={[styles.k, { color: theme.colors.text, fontFamily: typography.semibold }]}>Estado</Text><Text style={[styles.v, { color: theme.colors.textSoft, fontFamily: typography.medium }]}>{readValue('sync_estado')}</Text></View>
                  <View style={styles.kvRow}><Text style={[styles.k, { color: theme.colors.text, fontFamily: typography.semibold }]}>Fecha creado</Text><Text style={[styles.v, { color: theme.colors.textSoft, fontFamily: typography.medium }]}>{createdDateLabel}</Text></View>
                  <View style={styles.kvRow}><Text style={[styles.k, { color: theme.colors.text, fontFamily: typography.semibold }]}>Fecha sincronizado</Text><Text style={[styles.v, { color: theme.colors.textSoft, fontFamily: typography.medium }]}>{syncedDateLabel}</Text></View>
                  <View style={styles.kvRow}><Text style={[styles.k, { color: theme.colors.text, fontFamily: typography.semibold }]}>Institucion</Text><Text style={[styles.v, { color: theme.colors.textSoft, fontFamily: typography.medium }]}>#{readValue('id_institucion')}</Text></View>
                  <View style={styles.kvRow}><Text style={[styles.k, { color: theme.colors.text, fontFamily: typography.semibold }]}>Geo</Text><Text style={[styles.v, { color: theme.colors.textSoft, fontFamily: typography.medium }]}>{hasGeo ? `${lat}, ${lng}` : 'Sin geolocalizacion'}</Text></View>
                  {mapPreviewUrl ? (
                    <Image
                      source={{ uri: mapPreviewUrl }}
                      style={styles.mapPreview}
                      resizeMode="cover"
                      onError={() => {
                        if (mapProviderIndex < mapPreviewUrls.length - 1) {
                          setMapProviderIndex((prev) => prev + 1);
                        }
                      }}
                    />
                  ) : null}
                </View>

                <View style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
                  <Text style={[styles.cardTitle, { color: theme.colors.text, fontFamily: typography.bold }]}>Responsable</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Nombre: {readValue('responsable_nombre', 'nombre')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Apellido: {readValue('responsable_apellido', 'apellido')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>DNI: {readValue('responsable_dni', 'dni')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Telefono: {readValue('responsable_telefono', 'telefono')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Email: {readValue('responsable_email', 'email')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Funcion: {readValue('responsable_funcion', 'funcion')}</Text>
                </View>

                <View style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
                  <Text style={[styles.cardTitle, { color: theme.colors.text, fontFamily: typography.bold }]}>Institucion</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Tipo espacio fisico: {readValue('tipo_espacio_fisico')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Espacio fisico otro: {readValue('espacio_fisico_otro')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Tiene colaboradores: {readValue('tiene_colaboradores')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Cantidad colaboradores: {readValue('cantidad_colaboradores')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Tiene cocina: {readValue('tiene_cocina')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Espacio equipado: {readValue('espacio_equipado')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Tiene ventilacion: {readValue('tiene_ventilacion')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Tiene salida emergencia: {readValue('tiene_salida_emergencia')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Salida emergencia senializada: {readValue('salida_emergencia_senializada')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Tiene equipacion incendio: {readValue('tiene_equipacion_incendio')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Tiene botiquin: {readValue('tiene_botiquin')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Tiene buena iluminacion: {readValue('tiene_buena_iluminacion')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Tiene sanitarios: {readValue('tiene_sanitarios')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Desague hinodoro: {readValue('desague_hinodoro')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Gestion quejas: {readValue('gestion_quejas')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Gestion quejas otro: {readValue('gestion_quejas_otro')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Informacion quejas: {readValue('informacion_quejas')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Frecuencia limpieza: {readValue('frecuencia_limpieza')}</Text>
                </View>

                <View style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
                  <Text style={[styles.cardTitle, { color: theme.colors.text, fontFamily: typography.bold }]}>Cocina</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Espacio elaboracion alimentos: {readValue('espacio_elaboracion_alimentos')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Almacenamiento alimentos secos: {readValue('almacenamiento_alimentos_secos')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Heladera: {readValue('heladera')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Freezer: {readValue('freezer')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Recipiente residuos organicos: {readValue('recipiente_residuos_organicos')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Recipiente residuos reciclables: {readValue('recipiente_residuos_reciclables')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Otros residuos: {readValue('otros_residuos')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Recipiente otros residuos: {readValue('recipiente_otros_residuos')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Abastecimiento combustible: {readValue('abastecimiento_combustible')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Abastecimiento agua: {readValue('abastecimiento_agua')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Abastecimiento agua otro: {readValue('abastecimiento_agua_otro')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Instalacion electrica: {readValue('instalacion_electrica')}</Text>
                </View>

                <View style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
                  <Text style={[styles.cardTitle, { color: theme.colors.text, fontFamily: typography.bold }]}>Anexo y actividades</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Tipo insumo: {readValue('tipo_insumo')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Frecuencia insumo: {readValue('frecuencia_insumo')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Tecnologia: {readValue('tecnologia')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Acceso institucion: {readValue('acceso_institucion')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Distancia transporte: {readValue('distancia_transporte')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Servicio internet: {readValue('servicio_internet')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Zona inundable: {readValue('zona_inundable')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Jardin maternal: {readValue('actividades_jardin_maternal')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Jardin infantes: {readValue('actividades_jardin_infantes')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Apoyo escolar: {readValue('apoyo_escolar')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Alfabetizacion: {readValue('alfabetizacion_terminalidad')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Capacitaciones talleres: {readValue('capacitaciones_talleres')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Tipo talleres: {readValue('tipo_talleres')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Promocion salud: {readValue('promocion_salud')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Actividades discapacidad: {readValue('actividades_discapacidad')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Actividades recreativas: {readValue('actividades_recreativas')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Cuales recreativas: {readValue('cuales_actividades_recreativas')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Actividades culturales: {readValue('actividades_culturales')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Cuales culturales: {readValue('cuales_actividades_culturales')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Emprendimientos productivos: {readValue('emprendimientos_productivos')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Cuales emprendimientos: {readValue('cuales_emprendimientos_productivos')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Actividades religiosas: {readValue('actividades_religiosas')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Actividades huerta: {readValue('actividades_huerta')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Otras actividades: {readValue('otras_actividades')}</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Cuales otras actividades: {readValue('cuales_otras_actividades')}</Text>
                </View>

                <View style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
                  <Text style={[styles.cardTitle, { color: theme.colors.text, fontFamily: typography.bold }]}>Observaciones</Text>
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>
                    {readValue('observaciones')}
                  </Text>
                </View>

                <View style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
                  <Text style={[styles.cardTitle, { color: theme.colors.text, fontFamily: typography.bold }]}>
                    Campos extras ({detail?.campos_extra?.length || 0})
                  </Text>
                  {(detail?.campos_extra || []).length === 0 ? (
                    <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Sin campos extra</Text>
                  ) : (
                    (detail?.campos_extra || []).map((item, idx) => (
                      <View key={item.id || `${item.nombre}-${idx}`} style={styles.extraRow}>
                        <Text style={[styles.extraName, { color: theme.colors.text, fontFamily: typography.semibold }]}>{item.nombre}</Text>
                        <Text style={[styles.extraValue, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>{item.valor}</Text>
                      </View>
                    ))
                  )}
                </View>
              </>
            )}

            {activeTab === 'ADJUNTOS' && (
              <>
                <View style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
                  <Text style={[styles.cardTitle, { color: theme.colors.text, fontFamily: typography.bold }]}>
                    Imagenes ({imageAttachments.length})
                  </Text>
                  {imageAttachments.length === 0 ? (
                    <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Sin imagenes</Text>
                  ) : (
                    <View style={styles.imageGrid}>
                      {imageAttachments.map((item, idx) => (
                        <View key={item.id || `${item.nombre_original}-${idx}`} style={styles.imageBox}>
                          <TouchableOpacity onPress={() => openImagePreview(item)}>
                            {imageUrls[item.id || item.storage_path] ? (
                              <Image source={{ uri: imageUrls[item.id || item.storage_path] }} style={styles.imageThumb} resizeMode="cover" />
                            ) : (
                              <View style={[styles.imageThumb, styles.imagePlaceholder]}>
                                <Ionicons name="image-outline" size={22} color={theme.colors.textSoft} />
                                <Text style={[styles.imagePlaceholderText, { color: theme.colors.textSoft, fontFamily: typography.medium }]}>No disponible</Text>
                              </View>
                            )}
                          </TouchableOpacity>
                          <Text numberOfLines={1} style={[styles.imageName, { color: theme.colors.textSoft, fontFamily: typography.medium }]}>
                            {item.nombre_original || 'Imagen'}
                          </Text>
                        </View>
                      ))}
                    </View>
                  )}
                </View>

                <View style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
                  <Text style={[styles.cardTitle, { color: theme.colors.text, fontFamily: typography.bold }]}>
                    Documentos ({docAttachments.length})
                  </Text>
                  {docAttachments.length === 0 ? (
                    <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Sin documentos</Text>
                  ) : (
                    docAttachments.map((item, idx) => {
                      const actionId = String(item.id || item.storage_path || idx);
                      return (
                        <View key={actionId} style={styles.docRow}>
                          <View style={styles.docInfo}>
                            <Ionicons name="document-text-outline" size={18} color={theme.colors.primary} />
                            <Text style={[styles.docName, { color: theme.colors.textSoft, fontFamily: typography.medium }]}>
                              {item.nombre_original || item.storage_path || 'Documento'}
                            </Text>
                          </View>
                          <View style={styles.docActions}>
                            <TouchableOpacity style={styles.docActionBtn} onPress={() => previewDocumentInApp(item)}>
                              <Ionicons name="eye-outline" size={16} color={theme.colors.primary} />
                            </TouchableOpacity>
                            <TouchableOpacity
                              style={styles.docActionBtn}
                              onPress={() => shareAttachment(item)}
                              disabled={sharingId === actionId}
                            >
                              {sharingId === actionId ? (
                                <ActivityIndicator size="small" color={theme.colors.primary} />
                              ) : (
                                <Ionicons name="share-social-outline" size={16} color={theme.colors.primary} />
                              )}
                            </TouchableOpacity>
                          </View>
                        </View>
                      );
                    })
                  )}
                </View>
              </>
            )}

            {activeTab === 'FIRMA' && (
              <View style={[styles.card, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
                <Text style={[styles.cardTitle, { color: theme.colors.text, fontFamily: typography.bold }]}>Firma final</Text>
                {signaturePaths.length === 0 ? (
                  <Text style={[styles.row, { color: theme.colors.textSoft, fontFamily: typography.regular }]}>Sin firma registrada</Text>
                ) : (
                  <View style={[styles.signatureBox, { borderColor: theme.colors.border }]}>
                    <Svg height="100%" width="100%" viewBox="0 0 320 180">
                      {getCenteredSignaturePaths(signaturePaths).map((path, index) => (
                        <Path
                          key={index}
                          d={path}
                          stroke="#111111"
                          strokeWidth={2}
                          fill="none"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      ))}
                    </Svg>
                  </View>
                )}
              </View>
            )}
          </>
        )}
      </ScrollView>

      <Modal visible={previewVisible} transparent animationType="fade" onRequestClose={() => setPreviewVisible(false)}>
        <View style={styles.previewOverlay}>
          <View style={styles.previewTopBar}>
            <Text numberOfLines={1} style={[styles.previewTitle, { fontFamily: typography.semibold }]}>
              {previewName}
            </Text>
            <TouchableOpacity onPress={() => setPreviewVisible(false)} style={styles.previewCloseBtn}>
              <Ionicons name="close" size={24} color="#FFFFFF" />
            </TouchableOpacity>
          </View>
          <View style={styles.previewBody}>
            {previewUri ? <Image source={{ uri: previewUri }} style={styles.previewImage} resizeMode="contain" /> : null}
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  bannerWrap: {
    position: 'relative',
  },
  tabsRow: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingTop: 14,
    paddingBottom: 6,
  },
  tabChip: {
    borderWidth: 1,
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginRight: 8,
  },
  tabChipText: {
    fontSize: 13,
  },
  content: { padding: 16, paddingTop: 8 },
  card: {
    borderRadius: 14,
    borderWidth: 1,
    padding: 14,
    marginBottom: 12,
  },
  cardTitle: { fontSize: 17, marginBottom: 8 },
  row: { fontSize: 14, marginBottom: 5 },
  kvRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 6,
  },
  k: {
    width: 92,
    fontSize: 14,
  },
  v: {
    flex: 1,
    fontSize: 14,
  },
  extraRow: {
    paddingVertical: 7,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#DADADA',
  },
  extraName: {
    fontSize: 14,
  },
  extraValue: {
    fontSize: 13,
    marginTop: 2,
  },
  imageGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  imageBox: {
    width: '48%',
    marginBottom: 12,
  },
  imageThumb: {
    width: '100%',
    height: 120,
    borderRadius: 10,
    backgroundColor: '#EEE',
  },
  imagePlaceholder: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  imagePlaceholderText: {
    fontSize: 10,
    marginTop: 4,
  },
  imageName: {
    fontSize: 12,
    marginTop: 5,
  },
  docRow: {
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 10,
    padding: 10,
    marginBottom: 10,
  },
  docInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  docName: {
    fontSize: 14,
    marginLeft: 8,
    flex: 1,
  },
  docActions: {
    marginTop: 8,
    flexDirection: 'row',
    justifyContent: 'flex-end',
  },
  docActionBtn: {
    width: 34,
    height: 34,
    borderRadius: 17,
    marginLeft: 8,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(121,40,202,0.08)',
  },
  signatureBox: {
    height: 190,
    borderWidth: 1,
    borderRadius: 10,
    backgroundColor: '#FAFAFA',
    overflow: 'hidden',
  },
  previewOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.92)',
  },
  previewTopBar: {
    paddingTop: 46,
    paddingHorizontal: 14,
    paddingBottom: 10,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  previewTitle: {
    color: '#FFFFFF',
    fontSize: 14,
    flex: 1,
    marginRight: 8,
  },
  previewCloseBtn: {
    width: 34,
    height: 34,
    borderRadius: 17,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(255,255,255,0.15)',
  },
  previewBody: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 10,
  },
  previewImage: {
    width: '100%',
    height: '100%',
  },
  mapPreview: {
    width: '100%',
    height: 180,
    borderRadius: 10,
    marginTop: 8,
  },
});
