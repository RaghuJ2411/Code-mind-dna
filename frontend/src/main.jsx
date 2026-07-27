import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './styles.css';
import { RecruiterWorkflowProvider } from './context/RecruiterWorkflowContext';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <RecruiterWorkflowProvider>
        <App />
      </RecruiterWorkflowProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
