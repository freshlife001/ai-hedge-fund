import { useState, useEffect, useRef } from 'react';
import { Paper, Typography, IconButton, Box } from '@mui/material';
import { Close as CloseIcon, DragIndicator as DragIcon, Remove as MinimizeIcon } from '@mui/icons-material';
import dynamic from 'next/dynamic';

// Create a non-SSR version of the Draggable component
const Draggable = dynamic(
  () => import('react-draggable'),
  { ssr: false } // This ensures the component only renders on the client side
);

// Use dynamic import with no SSR for the entire component
const FloatingConsoleComponent = () => {
  const [logs, setLogs] = useState([]);
  const [isMinimized, setIsMinimized] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const consoleRef = useRef(null);
  
  // Add a local debug message immediately
  useEffect(() => {
    setLogs([
      { level: 'info', message: 'Console initialized. Waiting for WebSocket connection...' },
      { level: 'info', message: `Attempting to connect to: ws://${window.location.hostname}:5010/ws/logs` }
    ]);
    
    // Set initial position
    setPosition({
      x: window.innerWidth - 520,
      y: window.innerHeight - 320
    });
    
    // Handle window resize
    const handleResize = () => {
      setPosition(prev => ({
        x: Math.min(prev.x, window.innerWidth - 500),
        y: Math.min(prev.y, window.innerHeight - 300)
      }));
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  // WebSocket connection
  useEffect(() => {
    let ws;
    
    try {
      ws = new WebSocket(`ws://${window.location.hostname}:5010/ws/logs`);
      
      ws.onopen = () => {
        setLogs(prev => [...prev, { level: 'success', message: 'WebSocket connected successfully' }]);
      };
      
      ws.onmessage = (event) => {
        try {
          const log = JSON.parse(event.data);
          setLogs(prev => [...prev, log]);
          
          // Auto-scroll
          if (consoleRef.current) {
            consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
          setLogs(prev => [...prev, { 
            level: 'error', 
            message: `Error parsing message: ${error.message}\nRaw: ${event.data}` 
          }]);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setLogs(prev => [...prev, { level: 'error', message: 'WebSocket connection error' }]);
      };
      
      ws.onclose = () => {
        setLogs(prev => [...prev, { level: 'warning', message: 'WebSocket connection closed' }]);
      };
    } catch (error) {
      console.error('WebSocket setup error:', error);
      setLogs(prev => [...prev, { level: 'error', message: `WebSocket setup error: ${error.message}` }]);
    }
    
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);
  
  return (
    <Draggable
      handle=".drag-handle"
      position={position}
      onStop={(e, data) => {
        const x = Math.max(0, Math.min(data.x, window.innerWidth - 500));
        const y = Math.max(0, Math.min(data.y, window.innerHeight - 300));
        setPosition({ x, y });
      }}
    >
      <Paper
        sx={{
          position: 'fixed',
          bottom: 20,
          right: 20,
          width: isMinimized ? 200 : 500,
          height: isMinimized ? 40 : 300,
          zIndex: 9999,
          overflow: 'hidden',
          resize: 'both',
          backgroundColor: 'background.paper',
          border: '2px solid #3f51b5', // More prominent border
          borderColor: 'primary.main',
          boxShadow: 3,
        }}
      >
        <Box
          className="drag-handle"
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            p: 1,
            borderBottom: '1px solid',
            borderColor: 'divider',
            backgroundColor: 'primary.dark',
            color: 'white',
            cursor: 'move',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <DragIcon fontSize="small" sx={{ mr: 1 }} />
            <Typography variant="subtitle2">Console Output</Typography>
          </Box>
          <Box>
            <IconButton size="small" onClick={() => setIsMinimized(!isMinimized)} sx={{ color: 'white' }}>
              <MinimizeIcon fontSize="small" />
            </IconButton>
            <IconButton size="small" onClick={() => setLogs([])} sx={{ color: 'white' }}>
              <CloseIcon fontSize="small" />
            </IconButton>
          </Box>
        </Box>
        
        {!isMinimized && (
          <Box
            ref={consoleRef}
            sx={{
              p: 1,
              height: 'calc(100% - 40px)',
              overflowY: 'auto',
              fontFamily: 'monospace',
              fontSize: '0.85rem',
              whiteSpace: 'pre-wrap',
              backgroundColor: '#1e1e1e',
              color: '#d4d4d4',
            }}
          >
            {logs.length === 0 ? (
              <Box sx={{ p: 2, color: '#666' }}>No console output yet...</Box>
            ) : (
              logs.map((log, index) => (
                <Box 
                  key={index}
                  sx={{ 
                    mb: 0.5,
                    color: log.level === 'error' ? '#f44336' : 
                           log.level === 'warning' ? '#ff9800' : 
                           log.level === 'success' ? '#4caf50' : 
                           '#d4d4d4'
                  }}
                >
                  {log.message}
                </Box>
              ))
            )}
          </Box>
        )}
      </Paper>
    </Draggable>
  );
};

// Export a non-SSR version of the component
export default dynamic(() => Promise.resolve(FloatingConsoleComponent), { ssr: false }); 