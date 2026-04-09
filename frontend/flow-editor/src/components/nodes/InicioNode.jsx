import { Handle, Position } from 'reactflow';

export default function InicioNode({ data, selected }) {
  return (
    <div style={{
      background: selected ? '#d1fae5' : '#ecfdf5',
      border: `2px solid ${selected ? '#059669' : '#10b981'}`,
      borderRadius: 8,
      padding: '10px 16px',
      minWidth: 140,
      textAlign: 'center',
      boxShadow: selected ? '0 0 0 2px #059669' : 'none',
    }}>
      <div style={{ fontSize: 18, marginBottom: 2 }}>▶</div>
      <div style={{ fontWeight: 700, fontSize: 12, color: '#064e3b' }}>INICIO</div>
      <div style={{ fontSize: 11, color: '#065f46', marginTop: 2 }}>{data.label || 'Inicio'}</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
