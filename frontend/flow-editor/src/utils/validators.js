/**
 * Validaciones del grafo de flujo.
 * Retornan arrays de mensajes de error/advertencia.
 */

/**
 * Valida que el flujo tenga la estructura mínima para poder publicarse.
 * @param {Array} nodes - Nodos de React Flow
 * @param {Array} edges - Aristas de React Flow
 * @returns {{errores: string[], advertencias: string[]}}
 */
export function validarFlujo(nodes, edges) {
  const errores = [];
  const advertencias = [];

  const tieneInicio = nodes.some((n) => n.data?.tipo === 'inicio');
  const tieneFin = nodes.some((n) => n.data?.tipo === 'fin');

  if (!tieneInicio) {
    errores.push('El flujo debe tener un nodo de inicio.');
  }
  if (!tieneFin) {
    errores.push('El flujo debe tener al menos un nodo de fin.');
  }

  // Nodos sin conexiones
  nodes.forEach((node) => {
    const tieneSalida = edges.some((e) => e.source === node.id);
    const tieneEntrada = edges.some((e) => e.target === node.id);
    const esTipoInicio = node.data?.tipo === 'inicio';
    const esTipoFin = node.data?.tipo === 'fin';

    if (!esTipoFin && !tieneSalida) {
      advertencias.push(
        `El nodo "${node.data?.label || node.id}" no tiene conexión de salida.`
      );
    }
    if (!esTipoInicio && !tieneEntrada) {
      advertencias.push(
        `El nodo "${node.data?.label || node.id}" no tiene conexión de entrada.`
      );
    }
  });

  // Nodos sin nombre
  nodes.forEach((node) => {
    if (!node.data?.label?.trim()) {
      advertencias.push(`Un nodo (${node.data?.tipo || node.id}) no tiene nombre configurado.`);
    }
  });

  return { errores, advertencias };
}

/**
 * Verifica si el flujo puede publicarse (sin errores bloqueantes).
 */
export function puedePublicar(nodes, edges) {
  const { errores } = validarFlujo(nodes, edges);
  return errores.length === 0;
}
