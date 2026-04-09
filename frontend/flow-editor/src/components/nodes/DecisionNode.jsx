import { Handle, Position } from 'reactflow';

export default function DecisionNode({ data, selected }) {
  return (
    <div style={{
      background: selected ? '#f3e8ff' : '#faf5ff',
      border: `2px solid ${selected ? '#9333ea' : '#a855f7'}`,
      borderRadius: 8,
      padding: '10px 16px',
      minWidth: 160,
      textAlign: 'center',
      boxShadow: selected ? '0 0 0 2px #9333ea' : 'none',
    }}>
      <Handle type="target" position={Position.Top} />
      <div style={{ fontSize: 18, marginBottom: 2 }}>🔀</div>
      <div style={{ fontWeight: 700, fontSize: 12, color: '#581c87' }}>DECISIÓN</div>
      <div style={{ fontSize: 11, color: '#6b21a8', marginTop: 2 }}>{data.label || 'Decisión'}</div>
      {/* Múltiples salidas — React Flow maneja las conexiones desde este handle */}
      <Handle type="source" position={Position.Bottom} id="out" />
    </div>
  );
}
