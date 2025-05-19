import { useState, useEffect, useRef } from 'react';
import { Box, Typography, TextField, Button, Paper, Container, CssBaseline, Chip, Grid, Tooltip, Card, CircularProgress, CardMedia, Divider, FormControlLabel, Switch } from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import darkTheme from '../theme/darkTheme';
import Head from 'next/head';
import Image from 'next/image';
import { AnalysisResults }  from './analysis';
import { useRouter } from 'next/router';

// Predefined AI agents
export const agentOptions = [
  { label: 'Warren Buffett', value: 'warren_buffett_agent', description: 'Analyzes quality businesses with strong fundamentals and reasonable prices'},
  { label: 'Charlie Munger', value: 'charlie_munger_agent', description: 'Evaluates companies using mental models and considers moats and management quality'},
  { label: 'Ben Graham', value: 'ben_graham_agent', description: 'Focuses on deep value stocks trading below intrinsic value with margin of safety'},
  { label: 'Bill Ackman', value: 'bill_ackman_agent', description: 'Identifies high-quality businesses with long-term growth and activist potential'},
  { label: 'Cathie Wood', value: 'cathie_wood_agent', description: 'Specializes in disruptive innovation and high-growth technology companies'},
  { label: 'Michael Burry', value: 'michael_burry_agent', description: 'Hedge fund manager who predicted the 2008 housing market crash and inspired The Big Short' },
  { label: 'Peter Lynch', value: 'peter_lynch_agent', description: 'Legendary investor who managed the Magellan Fund at Fidelity with outstanding returns' },
  { label: 'Phil Fisher', value: 'phil_fisher_agent', description: 'Pioneering growth investor and author of Common Stocks and Uncommon Profits' },
  { label: 'Stanley Druckenmiller', value: 'stanley_druckenmiller_agent', description: "Billionaire investor known for managing George Soros's Quantum Fund and strong macro trades"},
  { label: 'Nancy Pelosi', value: 'nancy_pelosi_agent', description: 'Analyzes stocks with policy/regulatory advantages and asymmetric information opportunities'},
  { label: 'Wall Street Bets', value: 'wsb_agent', description: 'Identifies meme stocks, short squeeze candidates, and momentum plays'},
  // { label: 'Technical Analysis', value: 'technical_analyst_agent', description: 'Uses price patterns, trends, and indicators to generate trading signals' },
  // { label: 'Fundamental Analysis', value: 'fundamentals_agent', description: 'Examines company fundamentals like profitability, growth, and financial health' },
  // { label: 'Sentiment Analysis', value: 'sentiment_agent', description: 'Analyzes market sentiment from news and insider trading' },
  // { label: 'Valuation Analysis', value: 'valuation_agent', description: 'Calculates intrinsic value using multiple valuation methodologies' },
  // { label: 'Risk Management', value: 'risk_management_agent', description: 'Controls position sizing based on portfolio risk factors' },
];


export const agentOptionsForCrypto = [
  { label: 'Elon Musk', value: 'elon_musk_crypto_agent', description: 'Tesla, SpaceX, Dogecoin advocate; crypto-influential tech visionary.'},
  { label: 'Justin Sun', value: 'justin_sun_crypto_agent', description: 'The controversial founder of Tron (TRX), BitTorrent, and HTX exchange, known for aggressive marketing and crypto partnerships.'},
  { label: 'Donald Trump', value: 'donald_trump_crypto_agent', description: 'A businessman, media personality, and the 45th and 47th U.S. President, known for his unconventional politics and rhetoric.'},
  { label: 'Satoshi Nakamoto', value: 'satoshi_nakamoto_crypto_agent', description: 'The pseudonymous creator of Bitcoin, who introduced the cryptocurrency in 2008 and remains unidentified to date.'},
  { label: 'Robert Kiyosaki', value: 'robert_kiyosaki_crypto_agent', description: 'Author of Rich Dad Poor Dad, advocates Bitcoin, viewing it as protection against inflation, economic collapse, and fiat currency risks'},
  { label: 'Warren Buffett', value: 'warren_buffett_agent', description: 'Analyzes quality businesses with strong fundamentals and reasonable prices'},
  { label: 'Changpeng Zhao', value: 'changpeng_zhao_crypto_agent', description: 'Chinese crypto investor and analyst; crypto-influenced investor.'},
  { label: 'Vitalik Buterin', value: 'vitalik_buterin_crypto_agent', description: 'Ethereum and cryptocurrency pioneer; visionary investor.'},
  { label: 'Cathie Wood', value: 'cathie_wood_crypto_agent', description: 'Specializes in disruptive innovation and high-growth technology companies'},
  { label: 'Wall Street Bets', value: 'wsb_agent', description: 'Identifies meme stocks, short squeeze candidates, and momentum plays'},

  { label: 'Andre Cronje', value: 'andre_cronje_crypto_agent', description: 'Creator of Yearn Finance and multiple DeFi protocols, known for innovative smart contract designs.'},
  { label: 'Arthur Hayes', value: 'arthur_hayes_crypto_agent', description: 'Co-founder of BitMEX exchange, known for macro crypto analysis and derivatives expertise.'},
  { label: 'Barry Silbert', value: 'barry_silbert_crypto_agent', description: 'Founder of Digital Currency Group and Grayscale Investments, early institutional crypto advocate.'},
  { label: 'Brian Armstrong', value: 'brian_armstrong_crypto_agent', description: 'CEO of Coinbase, focused on regulatory-compliant crypto adoption and infrastructure.'},
  { label: 'Hayden Adams', value: 'hayden_adams_crypto_agent', description: 'Creator of Uniswap, pioneer of automated market maker (AMM) decentralized exchanges.'},
  { label: 'Jack Dorsey', value: 'jack_dorsey_crypto_agent', description: 'Twitter co-founder now focused on Bitcoin through Block (Square) and Lightning Network development.'},
  { label: 'Joseph Lubin', value: 'joseph_lubin_crypto_agent', description: 'Ethereum co-founder and founder of ConsenSys, focused on enterprise blockchain adoption.'},
  { label: 'Michael Saylor', value: 'michael_saylor_crypto_agent', description: 'MicroStrategy CEO who transformed the company into a Bitcoin-focused treasury reserve asset.'},
  { label: 'Su Zhu', value: 'su_zhu_crypto_agent', description: 'Co-founder of Three Arrows Capital, known for macro crypto trading strategies and market cycles.'},

  // { label: 'Technical Analysis', value: 'technical_analyst_agent', description: 'Uses price patterns, trends, and indicators to generate trading signals' },
  // { label: 'Fundamental Analysis', value: 'fundamentals_agent', description: 'Examines company fundamentals like profitability, growth, and financial health' },
  // { label: 'Sentiment Analysis', value: 'sentiment_agent', description: 'Analyzes market sentiment from news and insider trading' },
  // { label: 'Valuation Analysis', value: 'valuation_agent', description: 'Calculates intrinsic value using multiple valuation methodologies' },
  // { label: 'Risk Management', value: 'risk_management_agent', description: 'Controls position sizing based on portfolio risk factors' },
];





const AskPage = () => {
  const [loading, setLoading] = useState(false);
  const [isCrypto, setIsCrypto] = useState(true);
  const router = useRouter();

  const filteredAgents = !isCrypto? agentOptions : agentOptionsForCrypto;
  const [selectedAgent, setSelectedAgent] = useState(filteredAgents[0]); // Default to Warren Buffett
  

  const handleSubmit = async (e) => {
    e.preventDefault();
    //router.push(`/conversation?agent=${selectedAgent.value}&isCrypto=${isCrypto}`);
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
          Mises AI Trading Assistant
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
              {filteredAgents.map((agent) => (
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
  margin: '0 auto',
  
}}>
<Box />
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 , justifyContent: 'center', gap: 2}}>
            <FormControlLabel
              control={<Switch checked={isCrypto} onChange={() => {
  const newIsCrypto = !isCrypto;
  setIsCrypto(newIsCrypto);
  
  // If current agent doesn't support crypto, select the first one that does
  if (newIsCrypto ) {
    setSelectedAgent(agentOptionsForCrypto[0]);
  } else  {
    setSelectedAgent(agentOptions[0]);
  }
}} disabled={loading} />}
              label={isCrypto ? "Ask About Today's Crypto Market" : "Ask About Today's Stock Market"}
            />
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 , justifyContent: 'center'}}>
          <Button 
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <img src="/x-logo.svg" alt="X" width={20} height={20} />}
            type="submit" 
            variant="contained" 
            color="primary"
            onClick={() => {
    const redirectPath = `/conversation?agent=${selectedAgent.value}&isCrypto=${isCrypto}`;
    window.location.href = `/api/auth/x?redirect=${encodeURIComponent(redirectPath)}`;
  }} 
            sx={{ px: 4 }}
          >
            {loading ? `${selectedAgent.label} is typing ...` : `Signin with X to Ask ${selectedAgent.label}`}
          </Button>
          </Box>

            </Box>

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
      <meta name="description" content="Ask questions to our AI Trading Assistant" />
    </Head>
    {page}
  </ThemeProvider>
);

export default AskPage;