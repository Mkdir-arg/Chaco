import { useCallback, useEffect, useRef, useState } from 'react';
import ReactFlow, {
  addEdge,
  Background,
  Controls,
  MiniMap,
  useEdgesState,
  useNodesState,
} from 'reactflow';

import NodePanel from './components/NodePanel.jsx';
import PropertiesPanel from './components/PropertiesPanel.jsx';
import AccionHumanaNode from './components/nodes/AccionHumanaNode.jsx';
import DecisionNode from './components/nodes/DecisionNode.jsx';
import EsperaNode from './components/nodes/EsperaNode.jsx';
import FinNode from './components/nodes/FinNode.jsx';
import InicioNode from './components/nodes/InicioNode.jsx';
import { cargarDefinicion, guardarDefinicion, publicarFlujo } from './utils/api.js';
import { puedePublicar, validarFlujo } from './utils/validators.js';

const NODE_TYPES = {
  inicio: InicioNode,
  fin: FinNode,
  accion_humana: AccionHumanaNode,
  espera: EsperaNode,
  decision: DecisionNode,
};

const NODO_INICIO_DEFAULT = {
  id: 'n_inicio',
  type: 'inicio',
  position: { x: 250, y: 80 },
  data: { tipo: 'inicio', label: 'Inicio', descripcion: '' },
};

let nodeCounter = 1;
function nuevoId() {
  return `n_${Date.now()}_${nodeCounter++}`;
}

function definicionToFlow(definicion) {
  if (!definicion || !definicion.nodos) return { nodes: [NODO_INICIO_DEFAULT], edges: [] };

  const nodes = definicion.nodos.map((nodo, i) => ({
    id: nodo.id,
    type: nodo.tipo,
    position: nodo.config?.position || { x: 100 + i * 200, y: 100 + (i % 2) * 120 },
    data: { tipo: nodo.tipo, label: nodo.nombre, descripcion: nodo.config?.descripcion || '' },
  }));

  const edges = (definicion.transiciones || []).map((t, i) => ({
    id: `e_${t.desde}_${t.hasta}_${i}`,
    source: t.desde,
    target: t.hasta,
    data: { condicion: t.condicion ?? null },
    label: t.condicion ? `${t.condicion.campo} ${t.condicion.operador} ${t.condicion.valor}` : '',
    animated: false,
  }));

  return { nodes, edges };
}

function flowToDefinicion(nodes, edges) {
  return {
    nodos: nodes.map((n) => ({
      id: n.id,
      tipo: n.data.tipo,
      nombre: n.data.label || '',
      config: {
        descripcion: n.data.descripcion || '',
        position: n.position,
      },
    })),
    transiciones: edges.map((e) => ({
      desde: e.source,
      hasta: e.target,
      condicion: e.data?.condicion ?? null,
    })),
  };
}

export default function App({ programaId, programaNombre, apiDefinicionUrl, apiPublicarUrl }) {
  const reactFlowWrapper = useRef(null);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([NODO_INICIO_DEFAULT]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);
  const [toast, setToast] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [publicando, setPublicando] = useState(false);
  const [versionInfo, setVersionInfo] = useState(null);

  const showToast = (mensaje, tipo = 'success') => {
    setToast({ mensaje, tipo });
    setTimeout(() => setToast(null), 4000);
  };

  // Carga inicial
  useEffect(() => {
    if (!apiDefinicionUrl) return;
    cargarDefinicion(apiDefinicionUrl)
      .then((data) => {
        if (data.definicion) {
          const { nodes: n, edges: e } = definicionToFlow(data.definicion);
          setNodes(n);
          setEdges(e);
          setVersionInfo({ id: data.version_id, numero: data.numero_version, estado: data.estado });
        }
      })
      .catch((err) => showToast(err.message, 'error'))
      .finally(() => setCargando(false));
  }, [apiDefinicionUrl]);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge({ ...params, data: { condicion: null } }, eds)),
    [setEdges]
  );

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();
      const tipo = event.dataTransfer.getData('application/reactflow-tipo');
      if (!tipo || !reactFlowInstance) return;

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const id = nuevoId();
      const etiquetas = {
        inicio: 'Inicio', fin: 'Fin', accion_humana: 'Acción', espera: 'Espera', decision: 'Decisión',
      };
      const nuevoNodo = {
        id,
        type: tipo,
        position,
        data: { tipo, label: etiquetas[tipo] || tipo, descripcion: '' },
      };
      setNodes((ns) => [...ns, nuevoNodo]);
    },
    [reactFlowInstance, setNodes]
  );

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onNodeClick = useCallback((_, node) => {
    setSelectedNode(node);
    setSelectedEdge(null);
  }, []);

  const onEdgeClick = useCallback((_, edge) => {
    setSelectedEdge(edge);
    setSelectedNode(null);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
    setSelectedEdge(null);
  }, []);

  const onUpdateNode = useCallback((nodeId, patch) => {
    setNodes((ns) =>
      ns.map((n) => n.id === nodeId ? { ...n, data: { ...n.data, ...patch } } : n)
    );
    setSelectedNode((prev) => prev?.id === nodeId ? { ...prev, data: { ...prev.data, ...patch } } : prev);
  }, [setNodes]);

  const onUpdateEdge = useCallback((edgeId, patch) => {
    setEdges((es) =>
      es.map((e) => {
        if (e.id !== edgeId) return e;
        const newData = { ...e.data, ...patch };
        const cond = newData.condicion;
        return {
          ...e,
          data: newData,
          label: cond ? `${cond.campo} ${cond.operador} ${cond.valor}` : '',
        };
      })
    );
    setSelectedEdge((prev) => {
      if (!prev || prev.id !== edgeId) return prev;
      const newData = { ...prev.data, ...patch };
      return { ...prev, data: newData };
    });
  }, [setEdges]);

  const handleGuardar = async () => {
    if (!apiDefinicionUrl) return;
    setGuardando(true);
    try {
      const definicion = flowToDefinicion(nodes, edges);
      const result = await guardarDefinicion(apiDefinicionUrl, definicion);
      setVersionInfo({ id: result.version_id, numero: result.numero_version, estado: 'BORRADOR' });
      showToast(`Borrador v${result.numero_version} guardado.`);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setGuardando(false);
    }
  };

  const handlePublicar = async () => {
    if (!apiDefinicionUrl || !apiPublicarUrl) return;
    setPublicando(true);
    try {
      const definicion = flowToDefinicion(nodes, edges);
      const saved = await guardarDefinicion(apiDefinicionUrl, definicion);
      const published = await publicarFlujo(apiPublicarUrl);
      setVersionInfo({ id: published.version_id, numero: saved.numero_version, estado: 'PUBLICADA' });
      showToast(`Flujo v${saved.numero_version} publicado correctamente.`);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setPublicando(false);
    }
  };

  const tieneInicio = nodes.some((n) => n.data?.tipo === 'inicio');
  const { errores, advertencias } = validarFlujo(nodes, edges);
  const puedePublicarAhora = puedePublicar(nodes, edges);

  if (cargando) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#64748b' }}>
        Cargando editor...
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', fontFamily: 'system-ui, sans-serif' }}>
      {/* Toolbar */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 12, padding: '8px 16px',
        background: '#fff', borderBottom: '1px solid #e2e8f0', flexShrink: 0,
      }}>
        <span style={{ fontWeight: 600, fontSize: 13, color: '#1e293b', flex: 1 }}>
          {programaNombre}
          {versionInfo && (
            <span style={{ marginLeft: 8, fontSize: 11, color: '#64748b' }}>
              v{versionInfo.numero} — {versionInfo.estado}
            </span>
          )}
        </span>

        {errores.length > 0 && (
          <span style={{ fontSize: 11, color: '#ef4444' }} title={errores.join('\n')}>
            ⚠ {errores.length} error{errores.length > 1 ? 'es' : ''}
          </span>
        )}
        {advertencias.length > 0 && (
          <span style={{ fontSize: 11, color: '#f59e0b' }} title={advertencias.join('\n')}>
            ⚠ {advertencias.length} advertencia{advertencias.length > 1 ? 's' : ''}
          </span>
        )}

        <button
          onClick={handleGuardar}
          disabled={guardando}
          style={btnToolbar('#2563eb')}
        >
          {guardando ? 'Guardando...' : 'Guardar borrador'}
        </button>
        <button
          onClick={handlePublicar}
          disabled={!puedePublicarAhora || publicando}
          title={!puedePublicarAhora ? errores.join('\n') : 'Publicar flujo'}
          style={btnToolbar('#059669', !puedePublicarAhora || publicando)}
        >
          {publicando ? 'Publicando...' : 'Publicar flujo'}
        </button>
      </div>

      {/* Toast */}
      {toast && (
        <div style={{
          position: 'fixed', top: 16, right: 16, zIndex: 9999,
          background: toast.tipo === 'error' ? '#fef2f2' : '#f0fdf4',
          border: `1px solid ${toast.tipo === 'error' ? '#fca5a5' : '#86efac'}`,
          color: toast.tipo === 'error' ? '#dc2626' : '#16a34a',
          padding: '10px 16px', borderRadius: 6, fontSize: 13, maxWidth: 360,
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        }}>
          {toast.mensaje}
        </div>
      )}

      {/* Editor body */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <NodePanel tieneInicio={tieneInicio} />

        <div ref={reactFlowWrapper} style={{ flex: 1 }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onInit={setReactFlowInstance}
            onNodeClick={onNodeClick}
            onEdgeClick={onEdgeClick}
            onPaneClick={onPaneClick}
            nodeTypes={NODE_TYPES}
            fitView
            deleteKeyCode="Delete"
          >
            <Background />
            <Controls />
            <MiniMap nodeStrokeWidth={3} />
          </ReactFlow>
        </div>

        <PropertiesPanel
          selectedNode={selectedNode}
          selectedEdge={selectedEdge}
          nodes={nodes}
          onUpdateNode={onUpdateNode}
          onUpdateEdge={onUpdateEdge}
        />
      </div>
    </div>
  );
}

function btnToolbar(color, disabled = false) {
  return {
    padding: '6px 14px',
    background: disabled ? '#e2e8f0' : color,
    color: disabled ? '#94a3b8' : '#fff',
    border: 'none',
    borderRadius: 5,
    fontSize: 12,
    fontWeight: 600,
    cursor: disabled ? 'not-allowed' : 'pointer',
  };
}
