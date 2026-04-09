import { Handle, Position } from 'reactflow';

export default function FinNode({ data, selected }) {
  return (
    <div style={{
      background: selected ? '#fee2e2' : '#fef2f2',
      border: `2px solid ${selected ? '#dc2626' : '#ef4444'}`,
      borderRadius: 8,
      padding: '10px 16px',
      minWidth: 140,
      textAlign: 'center',
      boxShadow: selected ? '0 0 0 2px #dc2626' : 'none',
    }}>
      <Handle type="target" position={Position.Top} />
      <div style={{ fontSize: 18, marginBottom: 2 }}>⏹</div>
      <div style={{ fontWeight: 700, fontSize: 12, color: '#7f1d1d' }}>FIN</div>
      <div style={{ fontSize: 11, color: '#991b1b', marginTop: 2 }}>{data.label || 'Fin'}</div>
    </div>
  );
}
