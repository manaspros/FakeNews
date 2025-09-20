import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

// Components
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import CompanyDetail from './pages/CompanyDetail';
import Analysis from './pages/Analysis';
import News from './pages/News';
import Settings from './pages/Settings';

// Context
import { WebSocketProvider } from './context/WebSocketContext';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <WebSocketProvider>
        <Router>
          <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc' }}>
            <Navbar />
            <main className="main-content">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/company/:companyName" element={<CompanyDetail />} />
                <Route path="/analysis" element={<Analysis />} />
                <Route path="/news" element={<News />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </main>
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
              }}
            />
          </div>
        </Router>
      </WebSocketProvider>
    </QueryClientProvider>
  );
}

export default App;
