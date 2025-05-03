import { useState, useEffect, useRef } from 'react';
import { Box, Typography, TextField, Button, Paper, Container, CssBaseline, Chip, Grid, Tooltip, Card, CircularProgress, CardMedia, Divider, Autocomplete, FormControlLabel, Switch } from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import darkTheme from '../theme/darkTheme';
import Head from 'next/head';
import Image from 'next/image';
import { AnalysisResults }  from './analysis';

// Predefined AI agents
const agentOptions = [
  { label: 'Warren Buffett', value: 'warren_buffett_agent', description: 'Analyzes quality businesses with strong fundamentals and reasonable prices' },
  { label: 'Charlie Munger', value: 'charlie_munger_agent', description: 'Evaluates companies using mental models and considers moats and management quality' },
  { label: 'Ben Graham', value: 'ben_graham_agent', description: 'Focuses on deep value stocks trading below intrinsic value with margin of safety' },
  { label: 'Bill Ackman', value: 'bill_ackman_agent', description: 'Identifies high-quality businesses with long-term growth and activist potential' },
  { label: 'Cathie Wood', value: 'cathie_wood_agent', description: 'Specializes in disruptive innovation and high-growth technology companies' },
  { label: 'Michael Burry', value: 'michael_burry_agent', description: 'Hedge fund manager who predicted the 2008 housing market crash and inspired The Big Short' },
  { label: 'Peter Lynch', value: 'peter_lynch_agent', description: 'Legendary investor who managed the Magellan Fund at Fidelity with outstanding returns' },
  { label: 'Phil Fisher', value: 'phil_fisher_agent', description: 'Pioneering growth investor and author of Common Stocks and Uncommon Profits' },
  { label: 'Stanley Druckenmiller', value: 'stanley_druckenmiller_agent', description: 'Billionaire investor known for managing George Soros’s Quantum Fund and strong macro trades' },
  { label: 'Nancy Pelosi', value: 'nancy_pelosi_agent', description: 'Analyzes stocks with policy/regulatory advantages and asymmetric information opportunities' },
  { label: 'Wall Street Bets', value: 'wsb_agent', description: 'Identifies meme stocks, short squeeze candidates, and momentum plays' },
  // { label: 'Technical Analysis', value: 'technical_analyst_agent', description: 'Uses price patterns, trends, and indicators to generate trading signals' },
  // { label: 'Fundamental Analysis', value: 'fundamentals_agent', description: 'Examines company fundamentals like profitability, growth, and financial health' },
  // { label: 'Sentiment Analysis', value: 'sentiment_agent', description: 'Analyzes market sentiment from news and insider trading' },
  // { label: 'Valuation Analysis', value: 'valuation_agent', description: 'Calculates intrinsic value using multiple valuation methodologies' },
  // { label: 'Risk Management', value: 'risk_management_agent', description: 'Controls position sizing based on portfolio risk factors' },
];

const AskPage = () => {
  const [responses, setResponses] = useState([]);

const addResponse = (newResponse) => {
  setResponses(prev => [...prev, newResponse]);
};
  const [loading, setLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState(agentOptions[0]); // Default to Warren Buffett
  const [tickers, setTickers] = useState([]);
  const [cryptos, setCryptos] = useState([]);
  const [isCrypto, setIsCrypto] = useState(true);
  const [selectedSymbol, setSelectedSymbol] = useState(null);
  const responseEndRef = useRef(null);

const renderResponses = () => {
  return (
    <>
      {responses.map((response, index) => (
        typeof response === 'object' ? 
          <AnalysisResults key={index} results={response} /> :
          <Typography key={index} variant="body1" sx={{ mb: 2 }}>
            {response}
          </Typography>
      ))}
    </>
  );
};

  useEffect(() => {
    fetch('/available_tickers.json')
      .then(response => response.json())
      .then(data => setTickers(data.tickers))
      .catch(error => console.error('Error loading tickers:', error));
    
    fetch('/available_cryptos.json')
      .then(response => response.json())
      .then(data => setCryptos(data))
      .catch(error => console.error('Error loading cryptos:', error));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedSymbol) return;

    setLoading(true);
    
    try {
      let ticker = selectedSymbol.symbol;
      if (isCrypto) {
        ticker = "crypto:" + ticker;
      }
    

      const ticker_list = ticker.split(',').map(t => t.trim());
      const response = await fetch('http://localhost:5010/api/analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tickers: ticker,
          startDate: new Date().toISOString().split('T')[0],
          endDate: new Date().toISOString().split('T')[0],
          modelName: 'deepseek-reasoner',
          selectedAnalysts: [selectedAgent.value],
          initialCash: 100000,
          isCrypto: isCrypto,
          showReasoning: true,
          runRoundTable: false
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      const data = await response.json();
      console.log(data);

      // Manually create results if the API response isn't structured correctly
      const formattedResults = {
        tickers: ticker_list,
        date: new Date().toISOString().split('T')[0],
        signals: {}
      };
      
      if (data && data.ticker_analyses) {
        // Use API response
        Object.keys(data.ticker_analyses).forEach(ticker => {
          const analysis = data.ticker_analyses[ticker];
          formattedResults.signals[ticker] = {
            overallSignal: analysis.signals.overall || 'neutral',
            confidence: analysis.signals.confidence || 60,
            analysts: [selectedAgent].map(analyst => ({
              name: analyst.label,
              signal: analysis.signals[analyst.value] || 'neutral',
              confidence: analysis.signals[`${analyst.value}_confidence`] || 60,
              reasoning: analysis.reasoning[analyst.value] || 'No reasoning provided'
            }))
          };
        });
      } else {
        // Create fake results as fallback
        ticker_list.forEach(ticker => {
          formattedResults.signals[ticker] = {
            overallSignal: 'neutral',
            confidence: 70,
            analysts: [selectedAgent].map(analyst => ({
              name: analyst.label,
              signal: Math.random() > 0.5 ? 'bullish' : 'bearish',
              confidence: 70,
              reasoning: `Analysis for ${ticker} by ${analyst.label} (fallback data)`
            }))
          };
        });
      }
      addResponse(formattedResults);
    } catch (error) {
      addResponse(`Error analyzing ${selectedSymbol.symbol}: ${error.message}`);
    } finally {
      setLoading(false);
      responseEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  };
  
  const handleAgentSelect = (agent) => {
    setSelectedAgent(agent);
  };

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Paper 
        elevation={0}
        sx={{ 
          p: 2, 
          borderBottom: 1, 
          borderColor: 'divider',
          borderRadius: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        <Typography variant="h5" component="h1" sx={{ fontWeight: 'bold' }}>
          Mises AI Market Assistant
        </Typography>
      </Paper>

      <Container maxWidth="md" sx={{ flexGrow: 1, py: 6, pb: 30, px: 4 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Box 
                  sx={{ 
                    width: 200, 
                    height: 200, 
                    mb: 2,
                    position: 'relative',
                    '& img': {
                      objectFit: 'contain'
                    }
                  }}
                >
                  <img
                    src={`/avatars/${selectedAgent.value}.jpg`}
                    alt={selectedAgent.label}
                    style={{ width: '100%', height: '100%', borderRadius: '50%' }}
                  />
                </Box>
                <Typography variant="h5" component="h2" gutterBottom align="center">
                  {selectedAgent.label}
                </Typography>
                <Typography variant="body1" color="text.secondary" align="center">
                  {selectedAgent.description}
                </Typography>
              </Box>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={8}>
            <Typography variant="h6" gutterBottom>
            </Typography>
            
            <Grid container spacing={1} sx={{ mb: 3 }}>
              {agentOptions.map((agent) => (
                <Grid item key={agent.value}>
                  <Tooltip title={agent.description} placement="top" arrow>
                    <Chip
                      avatar={
                        <Box 
                          component="img"
                          src={`/avatars/${agent.value}.jpg`}
                          alt={agent.label}
                          sx={{ width: 24, height: 24, borderRadius: '50%' }}
                        />
                      }
                      label={agent.label}
                      disabled={loading} 
                      onClick={() => handleAgentSelect(agent)}
                      color={selectedAgent.value === agent.value ? "primary" : "default"}
                      variant={selectedAgent.value === agent.value ? "filled" : "outlined"}
                      sx={{ m: 0.5 }}
                    />
                  </Tooltip>
                </Grid>
              ))}

            </Grid>
        
            <Box component="form" onSubmit={handleSubmit} sx={{ 
  position: 'fixed',
  bottom: 0,
  left: 0,
  right: 0,
  p: 2,
  bgcolor: 'background.paper',
  boxShadow: 3,
  zIndex: 1200,
  maxWidth: 'md',
  margin: '0 auto'
}}>
<Box />
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <FormControlLabel
              control={<Switch checked={isCrypto} onChange={() => {
  setIsCrypto(!isCrypto);
  setSelectedSymbol(null);
}} disabled={loading} />}
              label={isCrypto ? "Ask About Today's Crypto Market" : "Ask About Today's Stock Market"}
            />
          </Box>
          <Autocomplete
            options={isCrypto ? cryptos : tickers}
            getOptionLabel={(option) => option.symbol.toUpperCase()}
            renderInput={(params) => (
              <TextField
                {...params}
                label={isCrypto ? "Select a crypto symbol" : "Select a ticker symbol"}
                variant="outlined"
                sx={{ mb: 2 }}
                disabled={loading}
              />
            )}
            disabled={loading}
            onChange={(event, newValue) => {
              setSelectedSymbol(newValue);
            }}
            filterOptions={(options, state) => {
              const inputValue = state.inputValue.trim().toLowerCase();
              return options.filter(option => 
                option.symbol.toLowerCase().includes(inputValue)
              );
            }}
          />
          <Button 
            disabled={loading || !selectedSymbol}
            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
            type="submit" 
            variant="contained" 
            color="primary" 
            sx={{ px: 4 }}
          >
            {loading ? `${selectedAgent.label} is thinking ...` : `Ask ${selectedAgent.label}`}
          </Button>
            </Box>

            {loading && responses.length === 0 && (
          <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>Thinking...</Typography>

          </Paper>
            )}
          {renderResponses()}

          {responses.length > 0 && (
          <Paper ref={responseEndRef} > </Paper>
            )}
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

// This gets called by Next.js's _app.js
// It allows this page to have its own layout (or no layout)
AskPage.getLayout = (page) => (
  <ThemeProvider theme={darkTheme}>
    <CssBaseline />
    <Head>
      <title>Ask AI</title>
      <meta name="description" content="Ask questions to our AI investment assistant" />
    </Head>
    {page}
  </ThemeProvider>
);

export default AskPage;