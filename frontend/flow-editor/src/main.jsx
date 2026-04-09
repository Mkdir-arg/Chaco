import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import 'reactflow/dist/style.css';

const rootEl = document.getElementById('flow-editor-root');
if (rootEl) {
  const config = window.flowEditorConfig || {};
  ReactDOM.createRoot(rootEl).render(
    <React.StrictMode>
      <App
        programaId={config.programaId}
        programaNombre={config.programaNombre}
        apiDefinicionUrl={config.apiDefinicionUrl}
        apiPublicarUrl={config.apiPublicarUrl}
      />
    </React.StrictMode>
  );
}
