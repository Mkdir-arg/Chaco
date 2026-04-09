/**
 * Panel izquierdo — tipos de nodo disponibles para arrastrar al canvas.
 */

const TIPOS = [
  { tipo: 'inicio',         label: 'Inicio',         icon: '▶',  color: '#10b981', desc: 'Punto de entrada del flujo' },
  { tipo: 'fin',            label: 'Fin',             icon: '⏹', color: '#ef4444', desc: 'Cierre del caso' },
  { tipo: 'accion_humana',  label: 'Acción Humana',  icon: '👤', color: '#3b82f6', desc: 'Requiere intervención del operador' },
  { tipo: 'espera',         label: 'Espera',          icon: '⏳', color: '#eab308', desc: 'Pausa temporal (bajo demanda)' },
  { tipo: 'decision',       label: 'Decisión',        icon: '🔀', color: '#a855f7', desc: 'Ramificación condicional' },
];

export default function NodePanel({ tieneInicio }) {
  const onDragStart = (event, tipo) => {
    event.dataTransfer.setData('application/reactflow-tipo', tipo);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <div style={{
      width: 200,
      background: '#f8fafc',
      borderRight: '1px solid #e2e8f0',
      padding: 12,
      overflowY: 'auto',
    }}>
      <div style={{ fontWeight: 700, fontSize: 12, color: '#475569', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        Nodos
      </div>
      {TIPOS.map(({ tipo, label, icon, color, desc }) => {
        const deshabilitado = tipo === 'inicio' && tieneInicio;
        return (
          <div
            key={tipo}
            draggable={!deshabilitado}
            onDragStart={deshabilitado ? undefined : (e) => onDragStart(e, tipo)}
            title={deshabilitado ? 'Ya existe un nodo de inicio' : desc}
            style={{
              background: '#fff',
              border: `1px solid ${deshabilitado ? '#cbd5e1' : color}`,
              borderRadius: 6,
              padding: '8px 10px',
              marginBottom: 8,
              cursor: deshabilitado ? 'not-allowed' : 'grab',
              opacity: deshabilitado ? 0.4 : 1,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              fontSize: 12,
              color: '#1e293b',
              userSelect: 'none',
            }}
          >
            <span style={{ fontSize: 16 }}>{icon}</span>
            <div>
              <div style={{ fontWeight: 600 }}>{label}</div>
              <div style={{ color: '#64748b', fontSize: 10 }}>{desc}</div>
            </div>
          </div>
        );
      })}
      <div style={{ marginTop: 16, fontSize: 10, color: '#94a3b8', lineHeight: 1.4 }}>
        Arrastrá los nodos al canvas y conectalos entre sí.
      </div>
    </div>
  );
}
