import { useState, useEffect, useRef } from 'react';
import { Box, Typography, TextField, Button, Paper, Container, CssBaseline, Chip, Grid, Tooltip, Card, CircularProgress, Avatar, List, ListItem, ListItemAvatar, ListItemText, Divider, Autocomplete } from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import darkTheme from '../theme/darkTheme';
import Head from 'next/head';
import { Send as SendIcon } from '@mui/icons-material';
import { useRouter } from 'next/router';
import { agentOptions, agentOptionsForCrypto } from './ask';


const ConversationPage = () => {
  const router = useRouter();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [tickers, setTickers] = useState([]);
  const [cryptos, setCryptos] = useState([]);
  const [isCrypto, setIsCrypto] = useState(router.query.isCrypto === 'true');
  const [selectedTicker, setSelectedTicker] = useState(null);
  const messagesEndRef = useRef(null);
  const [tickerSelectFixed, setTickerSelectFixed] = useState(true);
  
  const tickerSelectStyles = {
    position: 'sticky',
    top: 0,
    zIndex: 10,
    backgroundColor: 'background.paper',
    padding: '2px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  };

  // Load tickers and cryptos data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const tickersRes = await fetch('/available_tickers.json');
        const cryptosRes = await fetch('/available_cryptos.json');
        
        const tickersData = await tickersRes.json();
        setTickers(tickersData.tickers);
        
        const cryptosData = await cryptosRes.json();
        // Filter out duplicate symbols if needed
        setCryptos(cryptosData);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };
    fetchData();
  }, []);

  // Parse query parameters and set initial state
  useEffect(() => {
    if (!router.isReady) return;
    
    const { agent, ticker, isCrypto } = router.query;
    
    setIsCrypto(isCrypto === 'true');
    
    // Only set agent and add system message if we haven't done it yet
    if (!selectedAgent) {
      let agentToUse;
      const availableAgents = isCrypto ? agentOptionsForCrypto : agentOptions;
      
      if (agent) {
        const foundAgent = availableAgents.find(a => a.value === agent);
        agentToUse = foundAgent || availableAgents[0]; // Use found agent or default to first
      } else {
        agentToUse = availableAgents[0]; // Default to first agent
      }
      
      setSelectedAgent(agentToUse);
      
      // Add system message about the agent only once
      setMessages(prev => {
        // Only add if no messages exist yet
        if (prev.length === 0) {
          return [{
            id: Date.now(),
            text: `Hi`,
            sender: 'ai',
            agent: selectedAgent,
            timestamp: new Date().toISOString()
          }];
        }
        return prev;
      });
    }
    
    // Set ticker if provided in URL and we have data loaded
    if (ticker) {
      const symbolsToSearch = isCrypto ? cryptos : tickers;
      
      if (symbolsToSearch.length > 0 && !selectedTicker) {
        const foundTicker = symbolsToSearch.find(t => t.symbol === ticker);
        if (foundTicker) {
          setSelectedTicker(foundTicker);
        }
      }
    }
  }, [router.isReady, router.query, tickers, cryptos, isCrypto, selectedAgent, selectedTicker]);
  
  // Scroll to bottom of messages when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Update document title when agent or ticker changes
  useEffect(() => {
    if (!selectedAgent) return;
    
    const assetType = isCrypto ? 'Crypto' : 'Stock';
    
    const title = selectedTicker
      ? `${selectedAgent.label} on ${selectedTicker.symbol} ${assetType} - AI Investment Conversation`
      : `${selectedAgent.label} - AI Investment Conversation`;
      
    document.title = title;
  }, [selectedAgent, selectedTicker, isCrypto]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || !selectedAgent) return;

    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);
    
    try {
      // Prepare request body with ticker information if available
      const requestBody = {
        ticker: selectedTicker ? selectedTicker.symbol : null,
        question: inputMessage,
        selectedAgent: selectedAgent.value,
        isCrypto: isCrypto,
        modelName: 'deepseek-chat',
        context: messages
          .filter(m => m.sender !== 'system')
          .slice(-10) // Only include last 10 messages
          .map(m => ({
            role: m.sender === 'user' ? 'user' : 'assistant',
            content: m.text
          }))
      };
      
      // Add ticker to request if selected
      if (selectedTicker) {
        requestBody.ticker = selectedTicker.symbol;
        requestBody.isCrypto = isCrypto;
      }
      
      // Make API call to get AI response
      const response = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });
      const data = await response.json();
      console.log(data);
      
      const aiMessage = {
        id: Date.now(),
        text: data.answer,
        sender: 'ai',
        agent: selectedAgent,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, aiMessage]);
      setLoading(false);
      
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: `Error: ${error.message}`,
        sender: 'system',
        timestamp: new Date().toISOString()
      }]);
      setLoading(false);
    }
  };
  
  const handleTickerChange = async (event, newValue) => {
    setSelectedTicker(newValue);
    if (newValue) {
      let ticker = newValue.symbol;
      if (isCrypto) {
            ticker = "crypto:" + ticker;
      }
      
      // Update URL with new ticker
      router.push({
        pathname: router.pathname,
        query: { ...router.query, ticker: newValue.symbol, isCrypto: isCrypto }
      }, undefined, { shallow: true });
      
      // Add system message about ticker change
      const assetType = isCrypto ? 'cryptocurrency' : 'stock';
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: `analyzing ${newValue.symbol}`,
        sender: 'system',
        timestamp: new Date().toISOString()
      }]);
      
      setLoading(true);
      // Fetch analysis for the new ticker
      try {
        const response = await fetch('/api/analysis', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tickers: ticker,
            modelName: 'deepseek-reasoner',
            selectedAnalysts: [selectedAgent.value],
            initialCash: 100000,
            isCrypto: isCrypto,
            showReasoning: true,
            runRoundTable: false
          })
        });
        
        const data = await response.json();
        console.log(data);
        const analysis = data.ticker_analyses[ticker]
        const signal = analysis.signals[selectedAgent.value] || 'neutral'
        const confidence = analysis.signals[`${selectedAgent.value}_confidence`] || 60
        const reasoning = analysis.reasoning[selectedAgent.value]
        setMessages(prev => [...prev, {
          id: Date.now(),
          text: `${signal} for ${newValue.symbol} with ${confidence}% confidence.\n ${reasoning} `|| `Analysis for ${newValue.symbol}`,
          sender: 'ai',
          agent: selectedAgent,
          timestamp: new Date().toISOString()
        }]);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching analysis:', error);
        setMessages(prev => [...prev, {
          id: Date.now(),
          text: `Error fetching analysis for ${newValue.symbol}`,
          sender: 'system',
          timestamp: new Date().toISOString()
        }]);
        setLoading(false);
      }
    }
  };
  
  // Handle toggling between crypto and stock modes
  const handleCryptoToggle = (event) => {
    const newIsCrypto = event.target.checked;
    setIsCrypto(newIsCrypto);
    setSelectedTicker(null); // Reset selected ticker when switching modes
    
    // Update available agents based on crypto mode
    const availableAgents = newIsCrypto ? agentOptionsForCrypto : agentOptions;
    
    // If current agent isn't available in the new mode, switch to first available
    if (selectedAgent && !availableAgents.some(a => a.value === selectedAgent.value)) {
      const newAgent = availableAgents[0];
      setSelectedAgent(newAgent);
      
      // Add system message about agent change
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: `Switched to ${newAgent.label} for ${newIsCrypto ? 'cryptocurrency' : 'stock'} analysis`,
        sender: 'system',
        timestamp: new Date().toISOString()
      }]);
    }
    
    // Update URL with new crypto parameter
    router.push({
      pathname: router.pathname,
      query: { ...router.query, isCrypto: newIsCrypto, ticker: undefined }
    }, undefined, { shallow: true });
    
    // Add system message about mode change
    setMessages(prev => [...prev, {
      id: Date.now(),
      text: `Switched to ${newIsCrypto ? 'cryptocurrency' : 'stock'} analysis mode`,
      sender: 'system',
      timestamp: new Date().toISOString()
    }]);
  };

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>


      <Container maxWidth="md" sx={{ flexGrow: 1, py: 4, px: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Mode Selection and Ticker Selection */}
        <Box sx={{ mb: 0 }}>
          
          <Autocomplete
            id="ticker-select" style={tickerSelectStyles}
            options={isCrypto ? cryptos : tickers}
            getOptionLabel={(option) => `${isCrypto ? option.name :option.symbol}`}
            value={selectedTicker}
            onChange={handleTickerChange}
            disabled={loading}
            renderInput={(params) => (
              <TextField
                {...params}
                label={`Select a ${isCrypto ? 'crypto' : 'ticker'}`}
                variant="outlined"
                fullWidth
              />
            )}
            sx={{ mb: 2 }}
          />
        </Box>
        
        {/* Chat Messages */}
        <Paper 
          elevation={2} 
          sx={{ 
            flexGrow: 1, 
            mb: 6, 
            p: 0, 
            maxHeight: 'calc(100vh - 180px)',
            overflow: 'auto',
            display: 'flex',
            flexDirection: 'column'
          }}
        >
          {messages.length === 0 ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
              <Typography variant="body1" color="text.secondary" align="center">
                Start a conversation with {selectedAgent?.label || 'Investment Expert'}
              </Typography>
              <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
                Ask about investment strategies, market analysis, or specific stocks
              </Typography>
            </Box>
          ) : (
            <List sx={{ width: '100%', p: 0 }}>
              {messages.map((message) => (
                <ListItem 
                  key={message.id}
                  alignItems="flex-start"
                  sx={{
                    flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
                    mb: 2,
                    p: 1
                  }}
                >
                  <ListItemAvatar sx={{ minWidth: 40, mr: 1, ml:1 }}>
                    {message.sender === 'user' ? (
                      <Avatar sx={{ bgcolor: 'primary.main' }}>U</Avatar>
                    ) : message.sender === 'system' ? (
                      <Avatar sx={{ bgcolor: 'grey.500' }}>S</Avatar>
                    ) : (
                      <Avatar 
                        src={`/avatars/${message.agent?.value || selectedAgent.value}.jpg`}
                        alt={message.agent?.label || selectedAgent.label}
                      />
                    )}
                  </ListItemAvatar>
                  
                  <ListItemText
                    primary={
                      <Typography 
                        variant="subtitle2"
                        component="span"
                        color="text.secondary"
                      >
                        {message.sender === 'user' ? 'You' : 
                         message.sender === 'system' ? 'System' : 
                         message.agent?.label || selectedAgent.label}
                      </Typography>
                    }
                    secondary={
                      <Paper 
                        elevation={0} 
                        sx={{ 
                          p: 1.5, 
                          mt: 0.5,
                          bgcolor: message.sender === 'user' ? 'primary.dark' : 
                                  message.sender === 'system' ? 'grey.800' : 'background.paper',
                          borderRadius: 2,
                          maxWidth: '80%',
                          display: 'inline-block'
                        }}
                      >
                        <Typography 
                          variant="body1" 
                          component="div"
                          sx={{ 
                            color: message.sender === 'user' || message.sender === 'system' ? 
                                  'common.white' : 'text.primary',
                            whiteSpace: 'pre-wrap'
                          }}
                        >
                          {message.text}
                        </Typography>
                      </Paper>
                    }
                    sx={{
                      margin: 0,
                      textAlign: message.sender === 'user' ? 'right' : 'left'
                    }}
                  />
                </ListItem>
              ))}
              <div ref={messagesEndRef} />
            </List>
          )}
          
          {loading && (
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 2, mb:4 ,ml:2}}>
              <CircularProgress size={20} sx={{ mr: 1 }} />
              <Typography variant="body2">{selectedAgent?.label || 'Investment Expert'} is typing...</Typography>
            </Box>
          )}
        </Paper>
        
        {/* Message Input - Fixed at bottom */}
        <Box 
          component="form" 
          onSubmit={handleSendMessage} 
          sx={{ 
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            p: 2,
            bgcolor: 'background.paper',
            boxShadow: 3,
            zIndex: 1200,
            maxWidth: 'md',
            margin: '0 auto',
            display: 'flex', 
            alignItems: 'center'
          }}
        >
          <TextField
            fullWidth
            placeholder={`Ask ${selectedAgent?.label || 'Investment Expert'} about ${selectedTicker ? selectedTicker.symbol : 'investments'}...`}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            disabled={loading}
            variant="outlined"
            sx={{ mr: 1 }}
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading || !inputMessage.trim()}
            endIcon={<SendIcon />}
          >
            Send
          </Button>
        </Box>
      </Container>
    </Box>
  );
};

// This gets called by Next.js's _app.js
// It allows this page to have its own layout (or no layout)
ConversationPage.getLayout = (page) => (
  <ThemeProvider theme={darkTheme}>
    <CssBaseline />
    <Head>
      <title>AI Investment Conversation</title>
      <meta name="description" content="Chat with AI investment experts" />
    </Head>
    {page}
  </ThemeProvider>
);

export default ConversationPage;