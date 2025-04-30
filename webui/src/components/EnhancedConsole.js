import { useState, useEffect, useRef } from 'react';
import { Paper, Typography, IconButton, Box } from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import dynamic from 'next/dynamic';

// Import Draggable component
const Draggable = dynamic(() => import('react-draggable'), { ssr: false });

// Our client-side only component
function ConsoleComponent() {
  const [messages, setMessages] = useState(['Ritadel console initialized']);
  const [connected, setConnected] = useState(false);
  const consoleRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 600, height: 400 });
  
  // WebSocket connection
  useEffect(() => {
    console.log('Console mounted');
    
    try {
      const ws = new WebSocket(`ws://${window.location.hostname}:5010/ws/logs`);
      
      ws.onopen = () => {
        setConnected(true);
        setMessages(prev => [...prev, 'WebSocket connected']);
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setMessages(prev => [...prev, data.message]);
          
          // Auto-scroll
          if (consoleRef.current) {
            consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
          }
        } catch (e) {
          setMessages(prev => [...prev, `Error parsing: ${event.data}`]);
        }
      };
      
      ws.onerror = () => {
        setConnected(false);
        setMessages(prev => [...prev, 'WebSocket error']);
      };
      
      ws.onclose = () => {
        setConnected(false);
        setMessages(prev => [...prev, 'WebSocket closed']);
      };
      
      return () => ws.close();
    } catch (error) {
      setMessages(prev => [...prev, `WebSocket setup error: ${error.message}`]);
    }
  }, []);
  
  // Add this function to color-code log messages
  const formatMessageWithColors = (msg) => {
    if (typeof msg !== 'string') return msg;
    
    // Add color coding for common log patterns
    return msg
      .replace(/error|exception|failed|failure/gi, match => `<span style="color: #ff5555;">${match}</span>`)
      .replace(/warning|warn/gi, match => `<span style="color: #ffaa55;">${match}</span>`)
      .replace(/success|completed|done/gi, match => `<span style="color: #55ff55;">${match}</span>`)
      .replace(/starting|begin|analyzing/gi, match => `<span style="color: #55aaff;">${match}</span>`);
  }
  
  return (
    <Draggable
      handle=".console-handle"
      defaultPosition={{ x: 20, y: 20 }}
    >
      <Paper 
        elevation={5}
        sx={{
          position: 'fixed',
          top: 20,
          left: 20,
          width: dimensions.width,
          height: dimensions.height,
          zIndex: 9999,
          resize: 'both',
          overflow: 'hidden',
          backgroundColor: '#0D1117',
          color: '#33ff33',
          border: '1px solid #33ff33',
          borderRadius: '4px',
          fontFamily: '"Courier New", Courier, monospace',
          boxShadow: '0 0 20px rgba(0, 255, 0, 0.1)',
          minWidth: '300px',
          minHeight: '200px',
          maxWidth: '90vw',
          maxHeight: '80vh',
          transformOrigin: 'top left',
          '&::after': {
            content: '""',
            position: 'absolute',
            bottom: 0,
            right: 0,
            width: '15px',
            height: '15px',
            cursor: 'nwse-resize',
            backgroundImage: 'linear-gradient(135deg, transparent 50%, #33ff33 50%)',
            opacity: 0.8,
            zIndex: 10,
            pointerEvents: 'none'
          }
        }}
      >
        <Box 
          className="console-handle"
          sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            bgcolor: '#161B22',
            p: 1,
            borderBottom: '1px solid #33ff33',
            cursor: 'move'
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography sx={{ 
              color: '#33ff33', 
              fontWeight: 'bold',
              fontFamily: '"Courier New", Courier, monospace',
              display: 'flex',
              alignItems: 'center',
              '&::before': {
                content: '">"',
                marginRight: '8px',
                fontWeight: 'bold'
              }
            }}>
              ritadel console {connected ? '(Connected)' : '(Disconnected)'}
            </Typography>
          </Box>
          <IconButton size="small" sx={{ color: '#33ff33' }} onClick={() => setMessages([])}>
            <CloseIcon fontSize="small" />
          </IconButton>
        </Box>
        
        <Box 
          ref={consoleRef}
          sx={{ 
            height: 'calc(100% - 40px)', 
            overflowY: 'auto', 
            p: 1.5,
            '&::-webkit-scrollbar': {
              width: '8px',
            },
            '&::-webkit-scrollbar-track': {
              backgroundColor: '#0D1117',
            },
            '&::-webkit-scrollbar-thumb': {
              backgroundColor: '#33ff33',
              borderRadius: '4px',
              opacity: 0.5,
            }
          }}
        >
          {messages.map((msg, i) => (
            <Typography 
              key={i} 
              variant="body2" 
              sx={{ 
                fontSize: '13px',
                fontFamily: '"Courier New", Courier, monospace',
                lineHeight: 1.6,
                opacity: 0.9,
                mb: 0.5,
                position: 'relative',
                paddingLeft: '14px',
                '&::before': {
                  content: '"$"',
                  position: 'absolute',
                  left: 0,
                  color: '#33ff33',
                }
              }}
              dangerouslySetInnerHTML={{ __html: formatMessageWithColors(msg) }}
            />
          ))}
        </Box>
      </Paper>
    </Draggable>
  );
}

// Export with SSR disabled
export default dynamic(() => Promise.resolve(ConsoleComponent), { ssr: false }); 