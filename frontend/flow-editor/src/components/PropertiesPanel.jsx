/**
 * Panel derecho — propiedades del nodo o transición seleccionada.
 */

const OPERADORES = ['==', '!=', '>', '>=', '<', '<=', 'in'];

export default function PropertiesPanel({ selectedNode, selectedEdge, nodes, onUpdateNode, onUpdateEdge }) {
  if (!selectedNode && !selectedEdge) {
    return (
      <div style={{ width: 240, background: '#f8fafc', borderLeft: '1px solid #e2e8f0', padding: 16 }}>
        <div style={{ color: '#94a3b8', fontSize: 12 }}>
          Seleccioná un nodo o una conexión para editar sus propiedades.
        </div>
      </div>
    );
  }

  if (selectedNode) {
    const { data } = selectedNode;
    return (
      <div style={{ width: 240, background: '#f8fafc', borderLeft: '1px solid #e2e8f0', padding: 16, overflowY: 'auto' }}>
        <div style={{ fontWeight: 700, fontSize: 12, color: '#475569', marginBottom: 12, textTransform: 'uppercase' }}>
          Nodo — {data.tipo}
        </div>
        <label style={labelStyle}>Nombre del paso</label>
        <input
          style={inputStyle}
          value={data.label || ''}
          onChange={(e) => onUpdateNode(selectedNode.id, { label: e.target.value })}
          placeholder="Ej: Evaluación inicial"
        />
        <label style={labelStyle}>Descripción / instrucciones</label>
        <textarea
          style={{ ...inputStyle, minHeight: 72, resize: 'vertical' }}
          value={data.descripcion || ''}
          onChange={(e) => onUpdateNode(selectedNode.id, { descripcion: e.target.value })}
          placeholder="Instrucciones para el operador..."
        />
        <div style={{ marginTop: 8, fontSize: 10, color: '#94a3b8' }}>
          ID interno: <code>{selectedNode.id}</code>
        </div>
      </div>
    );
  }

  // Arista seleccionada — solo mostrar editor de condición si el nodo origen es "decision"
  if (selectedEdge) {
    const sourceNode = nodes.find((n) => n.id === selectedEdge.source);
    const esDecision = sourceNode?.data?.tipo === 'decision';
    const condicion = selectedEdge.data?.condicion ?? null;

    return (
      <div style={{ width: 240, background: '#f8fafc', borderLeft: '1px solid #e2e8f0', padding: 16, overflowY: 'auto' }}>
        <div style={{ fontWeight: 700, fontSize: 12, color: '#475569', marginBottom: 12, textTransform: 'uppercase' }}>
          Transición
        </div>
        {!esDecision ? (
          <div style={{ fontSize: 11, color: '#64748b' }}>
            Esta transición es libre (sin condición). Solo los nodos de decisión pueden tener condiciones configurables.
          </div>
        ) : (
          <>
            <label style={labelStyle}>Tipo de transición</label>
            <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
              <button
                style={{ ...btnStyle, background: condicion === null ? '#e0e7ff' : '#fff', fontWeight: condicion === null ? 700 : 400 }}
                onClick={() => onUpdateEdge(selectedEdge.id, { condicion: null })}
              >
                Libre
              </button>
              <button
                style={{ ...btnStyle, background: condicion !== null ? '#e0e7ff' : '#fff', fontWeight: condicion !== null ? 700 : 400 }}
                onClick={() => onUpdateEdge(selectedEdge.id, { condicion: condicion ?? { campo: '', operador: '==', valor: '' } })}
              >
                Condicional
              </button>
            </div>
            {condicion !== null && (
              <>
                <label style={labelStyle}>Campo a evaluar</label>
                <input
                  style={inputStyle}
                  value={condicion.campo || ''}
                  onChange={(e) => onUpdateEdge(selectedEdge.id, { condicion: { ...condicion, campo: e.target.value } })}
                  placeholder="Ej: aprobado"
                />
                <label style={labelStyle}>Operador</label>
                <select
                  style={inputStyle}
                  value={condicion.operador || '=='}
                  onChange={(e) => onUpdateEdge(selectedEdge.id, { condicion: { ...condicion, operador: e.target.value } })}
                >
                  {OPERADORES.map((op) => <option key={op} value={op}>{op}</option>)}
                </select>
                <label style={labelStyle}>Valor</label>
                <input
                  style={inputStyle}
                  value={condicion.valor ?? ''}
                  onChange={(e) => onUpdateEdge(selectedEdge.id, { condicion: { ...condicion, valor: e.target.value } })}
                  placeholder="Ej: true"
                />
                <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 4 }}>
                  La transición se toma cuando <code>{condicion.campo || 'campo'}</code> {condicion.operador} <code>{String(condicion.valor ?? '')}</code>
                </div>
              </>
            )}
          </>
        )}
      </div>
    );
  }

  return null;
}

const labelStyle = {
  display: 'block',
  fontSize: 11,
  fontWeight: 600,
  color: '#475569',
  marginBottom: 4,
  marginTop: 10,
};

const inputStyle = {
  width: '100%',
  padding: '6px 8px',
  border: '1px solid #cbd5e1',
  borderRadius: 4,
  fontSize: 12,
  boxSizing: 'border-box',
  background: '#fff',
};

const btnStyle = {
  flex: 1,
  padding: '4px 8px',
  border: '1px solid #cbd5e1',
  borderRadius: 4,
  fontSize: 11,
  cursor: 'pointer',
};
