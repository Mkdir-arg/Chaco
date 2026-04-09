import { Handle, Position } from 'reactflow';

export default function EsperaNode({ data, selected }) {
  return (
    <div style={{
      background: selected ? '#fef9c3' : '#fefce8',
      border: `2px solid ${selected ? '#ca8a04' : '#eab308'}`,
      borderRadius: 8,
      padding: '10px 16px',
      minWidth: 140,
      textAlign: 'center',
      boxShadow: selected ? '0 0 0 2px #ca8a04' : 'none',
    }}>
      <Handle type="target" position={Position.Top} />
      <div style={{ fontSize: 18, marginBottom: 2 }}>⏳</div>
      <div style={{ fontWeight: 700, fontSize: 12, color: '#713f12' }}>ESPERA</div>
      <div style={{ fontSize: 11, color: '#854d0e', marginTop: 2 }}>{data.label || 'Espera'}</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
