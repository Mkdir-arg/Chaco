import { Handle, Position } from 'reactflow';

export default function AccionHumanaNode({ data, selected }) {
  return (
    <div style={{
      background: selected ? '#dbeafe' : '#eff6ff',
      border: `2px solid ${selected ? '#2563eb' : '#3b82f6'}`,
      borderRadius: 8,
      padding: '10px 16px',
      minWidth: 160,
      textAlign: 'center',
      boxShadow: selected ? '0 0 0 2px #2563eb' : 'none',
    }}>
      <Handle type="target" position={Position.Top} />
      <div style={{ fontSize: 18, marginBottom: 2 }}>👤</div>
      <div style={{ fontWeight: 700, fontSize: 12, color: '#1e3a8a' }}>ACCIÓN HUMANA</div>
      <div style={{ fontSize: 11, color: '#1d4ed8', marginTop: 2 }}>{data.label || 'Acción'}</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
