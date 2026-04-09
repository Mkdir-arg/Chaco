import AsyncStorage from '@react-native-async-storage/async-storage';
import { supabase } from '../config/supabaseConfig';

const LOCAL_RECORDS_KEY = 'field_citizen_legajo_records';
const SYNC_QUEUE_KEY = 'field_citizen_legajo_sync_queue';

const CITIZENS_TABLE = 'ciudadanos';
const LEGAJOS_TABLE = 'legajos';

const nowIso = () => new Date().toISOString();

const createLocalId = () => `local_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;

const safeParse = (value, fallback = []) => {
  try {
    return value ? JSON.parse(value) : fallback;
  } catch {
    return fallback;
  }
};

const readRecords = async () => {
  const raw = await AsyncStorage.getItem(LOCAL_RECORDS_KEY);
  return safeParse(raw, []);
};

const writeRecords = async (records) => {
  await AsyncStorage.setItem(LOCAL_RECORDS_KEY, JSON.stringify(records));
};

const readQueue = async () => {
  const raw = await AsyncStorage.getItem(SYNC_QUEUE_KEY);
  return safeParse(raw, []);
};

const writeQueue = async (queue) => {
  await AsyncStorage.setItem(SYNC_QUEUE_KEY, JSON.stringify(queue));
};

const normalizeRecord = (input = {}) => ({
  local_id: input.local_id || createLocalId(),
  citizen_id: input.citizen_id || null,
  legajo_id: input.legajo_id || null,
  citizen: {
    nombre: input.citizen?.nombre || '',
    apellido: input.citizen?.apellido || '',
    dni: input.citizen?.dni || '',
    telefono: input.citizen?.telefono || '',
    domicilio: input.citizen?.domicilio || '',
  },
  legajo: {
    via_ingreso: input.legajo?.via_ingreso || 'ESPONTANEA',
    nivel_riesgo: input.legajo?.nivel_riesgo || 'BAJO',
    estado: input.legajo?.estado || 'EN_SEGUIMIENTO',
    notas: input.legajo?.notas || '',
  },
  synced: !!input.synced,
  updated_at: input.updated_at || nowIso(),
});

const upsertLocalRecord = async (record) => {
  const normalized = normalizeRecord(record);
  const records = await readRecords();
  const next = records.filter((item) => item.local_id !== normalized.local_id);
  next.unshift(normalized);
  await writeRecords(next);
  return normalized;
};

const enqueueSyncOperation = async (record) => {
  const queue = await readQueue();
  queue.push({
    op_id: createLocalId(),
    type: 'upsert_citizen_legajo',
    payload: record,
    created_at: nowIso(),
  });
  await writeQueue(queue);
};

const syncSingleOperation = async (operation) => {
  const payload = operation.payload;

  const citizenPayload = {
    nombre: payload.citizen.nombre,
    apellido: payload.citizen.apellido,
    dni: payload.citizen.dni,
    telefono: payload.citizen.telefono,
    domicilio: payload.citizen.domicilio,
    updated_at: nowIso(),
  };

  let citizenId = payload.citizen_id;
  if (citizenId) {
    const { data, error } = await supabase
      .from(CITIZENS_TABLE)
      .update(citizenPayload)
      .eq('id', citizenId)
      .select('id')
      .single();
    if (error) throw error;
    citizenId = data.id;
  } else {
    const { data, error } = await supabase
      .from(CITIZENS_TABLE)
      .insert(citizenPayload)
      .select('id')
      .single();
    if (error) throw error;
    citizenId = data.id;
  }

  const legajoPayload = {
    ciudadano_id: citizenId,
    via_ingreso: payload.legajo.via_ingreso,
    nivel_riesgo: payload.legajo.nivel_riesgo,
    estado: payload.legajo.estado,
    notas: payload.legajo.notas,
    updated_at: nowIso(),
  };

  let legajoId = payload.legajo_id;
  if (legajoId) {
    const { data, error } = await supabase
      .from(LEGAJOS_TABLE)
      .update(legajoPayload)
      .eq('id', legajoId)
      .select('id')
      .single();
    if (error) throw error;
    legajoId = data.id;
  } else {
    const { data, error } = await supabase
      .from(LEGAJOS_TABLE)
      .insert(legajoPayload)
      .select('id')
      .single();
    if (error) throw error;
    legajoId = data.id;
  }

  return { citizenId, legajoId };
};

const markRecordSynced = async (localId, citizenId, legajoId) => {
  const records = await readRecords();
  const next = records.map((item) => {
    if (item.local_id !== localId) return item;
    return {
      ...item,
      citizen_id: citizenId,
      legajo_id: legajoId,
      synced: true,
      updated_at: nowIso(),
    };
  });
  await writeRecords(next);
};

const replaceLocalWithRemoteSnapshot = async () => {
  const { data: citizens, error: citizensError } = await supabase
    .from(CITIZENS_TABLE)
    .select('id, nombre, apellido, dni, telefono, domicilio, updated_at')
    .order('updated_at', { ascending: false });

  if (citizensError) {
    throw citizensError;
  }

  if (!citizens?.length) {
    return [];
  }

  const citizenIds = citizens.map((c) => c.id);
  const { data: legajos, error: legajosError } = await supabase
    .from(LEGAJOS_TABLE)
    .select('id, ciudadano_id, via_ingreso, nivel_riesgo, estado, notas, updated_at')
    .in('ciudadano_id', citizenIds)
    .order('updated_at', { ascending: false });

  if (legajosError) {
    throw legajosError;
  }

  const legajoByCitizen = {};
  (legajos || []).forEach((legajo) => {
    if (!legajoByCitizen[legajo.ciudadano_id]) {
      legajoByCitizen[legajo.ciudadano_id] = legajo;
    }
  });

  const mapped = citizens.map((citizen) => {
    const legajo = legajoByCitizen[citizen.id];
    return normalizeRecord({
      local_id: `remote_${citizen.id}`,
      citizen_id: citizen.id,
      legajo_id: legajo?.id || null,
      citizen: {
        nombre: citizen.nombre,
        apellido: citizen.apellido,
        dni: citizen.dni,
        telefono: citizen.telefono,
        domicilio: citizen.domicilio,
      },
      legajo: {
        via_ingreso: legajo?.via_ingreso || 'ESPONTANEA',
        nivel_riesgo: legajo?.nivel_riesgo || 'BAJO',
        estado: legajo?.estado || 'EN_SEGUIMIENTO',
        notas: legajo?.notas || '',
      },
      synced: true,
      updated_at: citizen.updated_at || nowIso(),
    });
  });

  await writeRecords(mapped);
  return mapped;
};

const citizenLegajoService = {
  async saveCitizenLegajo(payload) {
    const record = await upsertLocalRecord({
      local_id: payload.local_id,
      citizen_id: payload.citizen_id,
      legajo_id: payload.legajo_id,
      citizen: payload.citizen,
      legajo: payload.legajo,
      synced: false,
      updated_at: nowIso(),
    });

    await enqueueSyncOperation(record);
    const syncResult = await this.syncPendingOperations();

    return {
      success: true,
      record,
      syncResult,
    };
  },

  async syncPendingOperations() {
    const queue = await readQueue();
    if (!queue.length) {
      return { synced: 0, failed: 0 };
    }

    let synced = 0;
    let failed = 0;
    const remaining = [];

    for (const operation of queue) {
      try {
        const result = await syncSingleOperation(operation);
        await markRecordSynced(
          operation.payload.local_id,
          result.citizenId,
          result.legajoId
        );
        synced += 1;
      } catch (error) {
        failed += 1;
        remaining.push(operation);
      }
    }

    await writeQueue(remaining);
    return { synced, failed };
  },

  async getPendingCount() {
    const queue = await readQueue();
    return queue.length;
  },

  async getCitizenLegajoRecords({ refreshFromRemote = true } = {}) {
    if (refreshFromRemote) {
      try {
        await this.syncPendingOperations();
        const remoteRecords = await replaceLocalWithRemoteSnapshot();
        return {
          success: true,
          records: remoteRecords,
        };
      } catch (error) {
        const localRecords = await readRecords();
        return {
          success: false,
          records: localRecords,
          error: error?.message || 'No se pudo actualizar desde Supabase',
        };
      }
    }

    const localRecords = await readRecords();
    return { success: true, records: localRecords };
  },
};

export default citizenLegajoService;
