import React, { createContext, useContext, useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { io } from 'socket.io-client';

const WebSocketContext = createContext();

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

export const WebSocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    // Create WebSocket connection
    const wsUrl = process.env.NODE_ENV === 'development'
      ? 'ws://localhost:8000/ws'
      : `ws://${window.location.host}/ws`;

    let ws;

    const connect = () => {
      try {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          console.log('WebSocket connected');
          setIsConnected(true);
          setSocket(ws);
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected');
          setIsConnected(false);
          setSocket(null);

          // Attempt to reconnect after 3 seconds
          setTimeout(() => {
            console.log('Attempting to reconnect...');
            connect();
          }, 3000);
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
      } catch (error) {
        console.error('WebSocket connection failed:', error);
        setTimeout(connect, 3000);
      }
    };

    connect();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'alert':
        handleAlert(data);
        break;
      case 'news_update':
        handleNewsUpdate(data);
        break;
      case 'analysis_complete':
        handleAnalysisComplete(data);
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const handleAlert = (data) => {
    const alertMessage = `🚨 ${data.level} Alert: ${data.message}`;

    // Add to alerts list
    const newAlert = {
      id: Date.now(),
      ...data,
      timestamp: new Date().toISOString()
    };
    setAlerts(prev => [newAlert, ...prev.slice(0, 49)]); // Keep last 50 alerts

    // Show toast notification
    if (data.level === 'HIGH') {
      toast.error(alertMessage, { duration: 6000 });
    } else if (data.level === 'MEDIUM') {
      toast(alertMessage, {
        duration: 4000,
        icon: '⚠️',
        style: {
          background: '#f59e0b',
          color: '#fff',
        }
      });
    } else {
      toast.success(alertMessage);
    }
  };

  const handleNewsUpdate = (data) => {
    toast(`📰 Breaking: ${data.headline}`, {
      duration: 5000,
      icon: '📰',
    });
  };

  const handleAnalysisComplete = (data) => {
    toast.success(`✅ Analysis complete for ${data.company}`, {
      duration: 3000,
    });
  };

  const sendMessage = (message) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected');
    }
  };

  const clearAlerts = () => {
    setAlerts([]);
  };

  const removeAlert = (alertId) => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };

  const value = {
    socket,
    isConnected,
    alerts,
    sendMessage,
    clearAlerts,
    removeAlert
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};