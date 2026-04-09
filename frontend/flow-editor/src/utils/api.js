/**
 * Utilidades de comunicación con la API Django.
 * El token CSRF se lee desde la cookie `csrftoken` emitida por Django.
 */

function getCsrfToken() {
  return document.cookie
    .split('; ')
    .find((row) => row.startsWith('csrftoken='))
    ?.split('=')[1] ?? '';
}

/**
 * Guarda una definición de flujo como nueva versión BORRADOR.
 * @param {string} url - URL del endpoint POST /api/flujos/<id>/definicion/
 * @param {object} definicion - Objeto {nodos, transiciones}
 * @returns {Promise<{ok, version_id, numero_version}>}
 */
export async function guardarDefinicion(url, definicion) {
  const resp = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify(definicion),
  });
  if (!resp.ok) {
    const data = await resp.json().catch(() => ({}));
    throw new Error(data.error || `Error ${resp.status} al guardar la definición.`);
  }
  return resp.json();
}

/**
 * Publica la versión BORRADOR más reciente del flujo.
 * @param {string} url - URL del endpoint POST /api/flujos/<id>/publicar/
 * @returns {Promise<{ok, version_id}>}
 */
export async function publicarFlujo(url) {
  const resp = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    body: JSON.stringify({}),
  });
  if (!resp.ok) {
    const data = await resp.json().catch(() => ({}));
    if (resp.status === 403) {
      throw new Error('Sesión expirada o sin permiso. Reautenticá y volvé a intentar.');
    }
    throw new Error(data.error || `Error ${resp.status} al publicar el flujo.`);
  }
  return resp.json();
}

/**
 * Carga la definición de flujo actual (PUBLICADA o último BORRADOR).
 * @param {string} url - URL del endpoint GET /api/flujos/<id>/definicion/
 * @returns {Promise<{definicion, version_id, numero_version, estado} | {definicion: null, version: null}>}
 */
export async function cargarDefinicion(url) {
  const resp = await fetch(url, {
    headers: { 'Accept': 'application/json' },
  });
  if (!resp.ok) {
    throw new Error(`Error ${resp.status} al cargar la definición.`);
  }
  return resp.json();
}
