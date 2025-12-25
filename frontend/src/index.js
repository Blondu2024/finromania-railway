import React from "react";
import ReactDOM from "react-dom/client";
import { HelmetProvider } from 'react-helmet-async';
import { Toaster } from 'react-hot-toast';
import "@/index.css";
import App from "@/App";
import { initGA } from './utils/analytics';

// Initialize Google Analytics
initGA();

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <HelmetProvider>
      <App />
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </HelmetProvider>
  </React.StrictMode>,
);
