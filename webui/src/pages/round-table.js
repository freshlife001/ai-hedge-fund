import { useState } from 'react';
import { Box, Typography, Card, CardContent, TextField, Button, Chip, Grid, CircularProgress, Paper, Avatar, IconButton, Divider, FormControlLabel, Checkbox } from '@mui/material';
import { Send as SendIcon, BarChart as BarChartIcon, Person as PersonIcon, Assessment as AssessmentIcon, Download as DownloadIcon } from '@mui/icons-material';

// Sample AI personas with their characteristics
const personas = [
  { id: 'warren_buffett_agent', name: 'Warren Buffett', avatar: '👴', color: '#85bb65', style: 'Value investing legend and CEO of Berkshire Hathaway' },
  { id: 'charlie_munger_agent', name: 'Charlie Munger', avatar: '👨‍🦳', color: '#4a7c59', style: 'Buffett\'s right-hand man and mental model enthusiast' },
  { id: 'ben_graham_agent', name: 'Ben Graham', avatar: '🧓', color: '#3a5f3a', style: 'Father of value investing, focus on margin of safety' },
  { id: 'cathie_wood_agent', name: 'Cathie Wood', avatar: '👩‍💼', color: '#c04c8a', style: 'Disruptive innovation investor, founder of ARK Invest' },
  { id: 'bill_ackman_agent', name: 'Bill Ackman', avatar: '👨‍💼', color: '#4169e1', style: 'Activist investor with high conviction bets' },
  { id: 'nancy_pelosi_agent', name: 'Nancy Pelosi', avatar: '👩‍⚖️', color: '#008080', style: 'Focuses on policy & information asymmetry advantages' },
  { id: 'wsb_agent', name: 'WSB', avatar: '🚀', color: '#ff4500', style: 'Meme stock enthusiast, looks for moonshots and short squeezes' },
  { id: 'technical_analyst_agent', name: 'Technical Analyst', avatar: '📊', color: '#ffa500', style: 'Chart pattern expert, focuses on price action' },
  { id: 'fundamentals_agent', name: 'Fundamental Analyst', avatar: '📈', color: '#ffffff', style: 'Examines financial statements and business metrics' },
  { id: 'sentiment_agent', name: 'Sentiment Analyst', avatar: '📰', color: '#9370db', style: 'Focuses on news sentiment and public perception' },
  { id: 'valuation_agent', name: 'Valuation Analyst', avatar: '💰', color: '#4682b4', style: 'Specialized in determining intrinsic value with multiple methods' },
];

// Sample round table conversation
const sampleConversation = [
  { speaker: 'Moderator', message: 'Welcome to today\'s investment round table where we\'ll be discussing NVIDIA (NVDA). Let\'s begin with initial positions from each analyst.', avatar: '🎙️', color: '#888888' },
  { speaker: 'Warren Buffett', message: 'I have to admit, NVDA is out of my usual circle of competence. The semiconductor business changes rapidly, making it hard to predict the next decade. However, their moat through CUDA and their execution has been admirable. I\'m neutral but watching closely.', avatar: '👴', color: '#85bb65' },
  { speaker: 'Cathie Wood', message: 'NVDA is perfectly positioned at the center of the AI revolution. Their GPUs are essential infrastructure for training models, and demand continues to outstrip supply. This is a strong buy for the five-year horizon.', avatar: '👩‍💼', color: '#c04c8a' },
  { speaker: 'Technical Analyst', message: 'The chart shows strong momentum with consistently higher lows. RSI indicates it\'s overbought, but the MACD remains bullish. Moving averages show solid uptrend support.', avatar: '📊', color: '#ffa500' },
  { speaker: 'Bill Ackman', message: 'Their operating leverage is impressive. As revenue grows, more falls to the bottom line. With AI spending just beginning, they\'re positioned for years of growth. My concern is valuation - they\'re priced for perfection.', avatar: '👨‍💼', color: '#4169e1' },
  { speaker: 'WSB', message: 'NVDA to the moon! 🚀🚀🚀 Jensen is playing 4D chess and bears keep getting wrecked. AI hype train has no brakes and NVDA has diamond hands on the GPU market!', avatar: '🚀', color: '#ff4500' },
  { speaker: 'Charlie Munger', message: 'I\'m concerned about the multiple. It prices in not just success but dominance, which attracts competition. Remember the dot-com bubble lesson: revolutionaries rarely get rich. Those who make picks and shovels profit, but even they face margin compression eventually.', avatar: '👨‍🦳', color: '#4a7c59' },
  { speaker: 'Sentiment Analyst', message: 'News sentiment is overwhelmingly positive. Analyst coverage shows 85% buy ratings with consistently rising price targets. Insider selling is present but looks like normal diversification rather than a bearish signal.', avatar: '📰', color: '#9370db' },
  { speaker: 'Valuation Analyst', message: 'On traditional metrics, NVDA looks extremely expensive at 40x sales and 100x earnings. However, DCF models with 35% growth for 5 years followed by gradual deceleration can justify current prices. Still, the margin of safety is minimal.', avatar: '💰', color: '#4682b4' },
  { speaker: 'Ben Graham', message: 'This is pure speculation, not investment. No margin of safety, no reasonable P/E, and no history of returning capital to shareholders. A Graham investor must avoid this regardless of the growth story.', avatar: '🧓', color: '#3a5f3a' },
  { speaker: 'Nancy Pelosi', message: 'Legislative outlook is favorable. The CHIPS Act and government AI initiatives provide secular support. Defense contracts add stability. Regulatory headwinds from China sanctions are a concern but should be manageable.', avatar: '👩‍⚖️', color: '#008080' },
  { speaker: 'Moderator', message: 'Let\'s wrap up with final signals and confidence levels.', avatar: '🎙️', color: '#888888' },
  { speaker: 'Warren Buffett', message: 'Neutral, 50% confidence. Too much uncertainty around long-term competitive advantage.', avatar: '👴', color: '#85bb65' },
  { speaker: 'Ben Graham', message: 'Bearish, 95% confidence. Not an investment by any fundamental measure.', avatar: '🧓', color: '#3a5f3a' },
  { speaker: 'Cathie Wood', message: 'Bullish, 90% confidence. This is the backbone of AI infrastructure for years to come.', avatar: '👩‍💼', color: '#c04c8a' },
  { speaker: 'Technical Analyst', message: 'Bullish, 75% confidence. Trend remains strong despite overbought conditions.', avatar: '📊', color: '#ffa500' },
  { speaker: 'Charlie Munger', message: 'Bearish, 70% confidence. Price implies impossibly perfect execution.', avatar: '👨‍🦳', color: '#4a7c59' },
  { speaker: 'Moderator', message: 'Our consensus signal is BULLISH with 65% confidence. The bull case is driven by AI infrastructure leadership and growth outlook, while the bear case centers on valuation concerns and competitive risks.', avatar: '🎙️', color: '#888888' },
];

export default function RoundTable() {
  const [tickers, setTickers] = useState('');
  const [selectedPersonas, setSelectedPersonas] = useState(['warren_buffett_agent', 'charlie_munger_agent', 'cathie_wood_agent']);
  const [isRunning, setIsRunning] = useState(false);
  const [conversation, setConversation] = useState(null);
  const [result, setResult] = useState(null);
  const [showAllPersonas, setShowAllPersonas] = useState(false);

  const handleTogglePersona = (personaId) => {
    if (selectedPersonas.includes(personaId)) {
      setSelectedPersonas(selectedPersonas.filter(id => id !== personaId));
    } else {
      setSelectedPersonas([...selectedPersonas, personaId]);
    }
  };

  const handleSelectAllPersonas = () => {
    if (selectedPersonas.length === personas.length) {
      setSelectedPersonas([]);
    } else {
      setSelectedPersonas(personas.map(p => p.id));
    }
  };

  const handleRunRoundTable = () => {
    setIsRunning(true);
    
    // Simulate API call delay
    setTimeout(() => {
      setIsRunning(false);
      setConversation(sampleConversation);
      setResult({
        signal: 'bullish',
        confidence: 65,
        reasoning: 'The AI revolution provides strong secular tailwinds for NVDA, with its dominant GPU position and software ecosystem (CUDA) creating significant barriers to entry. While valuation concerns are valid, the company\'s growth trajectory and market leadership justify a premium multiple.',
        consensus_view: 'NVDA is well-positioned to benefit from AI infrastructure buildout over the next several years.',
        dissenting_opinions: 'Value-oriented analysts believe the current price reflects unrealistic expectations and leaves no margin of safety. Concerns about competition and cyclicality were also raised.'
      });
    }, 3000);
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Investment Round Table
      </Typography>
      
      {!conversation ? (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Configure Round Table Discussion
            </Typography>
            
            <TextField
              label="Ticker Symbol"
              fullWidth
              margin="normal"
              placeholder="AAPL"
              value={tickers}
              onChange={(e) => setTickers(e.target.value)}
              helperText="Enter a single ticker for in-depth discussion"
            />
            
            <Box sx={{ my: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="subtitle1">Select AI Personas for Discussion</Typography>
                <Button 
                  size="small" 
                  onClick={handleSelectAllPersonas}
                >
                  {selectedPersonas.length === personas.length ? 'Deselect All' : 'Select All'}
                </Button>
              </Box>
              
              <Box sx={{ maxHeight: '300px', overflowY: 'auto', pr: 1 }}>
                <Grid container spacing={2}>
                  {personas.map((persona) => (
                    <Grid item xs={12} sm={6} md={4} key={persona.id}>
                      <Card 
                        variant="outlined"
                        sx={{ 
                          cursor: 'pointer',
                          bgcolor: selectedPersonas.includes(persona.id) ? 'action.selected' : 'background.paper',
                          borderColor: selectedPersonas.includes(persona.id) ? 'primary.main' : 'divider',
                          '&:hover': {
                            borderColor: 'primary.main',
                          },
                        }}
                        onClick={() => handleTogglePersona(persona.id)}
                      >
                        <CardContent sx={{ py: 2, '&:last-child': { pb: 2 } }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                            <Avatar 
                              sx={{ 
                                bgcolor: persona.color,
                                width: 36,
                                height: 36,
                                fontSize: '1.2rem',
                              }}
                            >
                              {persona.avatar}
                            </Avatar>
                            <Box>
                              <Typography variant="subtitle2">
                                {persona.name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {persona.style}
                              </Typography>
                            </Box>
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            </Box>
            
            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                variant="contained"
                onClick={handleRunRoundTable}
                disabled={!tickers || selectedPersonas.length < 2 || isRunning}
                startIcon={isRunning ? <CircularProgress size={20} color="inherit" /> : <PersonIcon />}
              >
                {isRunning ? 'Generating Discussion...' : 'Start Round Table'}
              </Button>
            </Box>
          </CardContent>
        </Card>
      ) : (
        <Box>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Round Table Results: {tickers}</Typography>
                <Chip 
                  label={result.signal.toUpperCase()} 
                  color={
                    result.signal === 'bullish' ? 'success' : 
                    result.signal === 'bearish' ? 'error' : 'warning'
                  }
                  sx={{ fontWeight: 'bold' }}
                />
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary">Confidence Level</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ flexGrow: 1, bgcolor: 'background.paper', height: 10, borderRadius: 5, overflow: 'hidden' }}>
                    <Box 
                      sx={{ 
                        height: '100%', 
                        width: `${result.confidence}%`,
                        bgcolor: 
                          result.signal === 'bullish' ? 'success.main' : 
                          result.signal === 'bearish' ? 'error.main' : 'warning.main',
                        borderRadius: 5
                      }} 
                    />
                  </Box>
                  <Typography variant="body2">{result.confidence}%</Typography>
                </Box>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary">Reasoning</Typography>
                <Typography variant="body2">{result.reasoning}</Typography>
              </Box>
              
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary">Consensus View</Typography>
                    <Typography variant="body2">{result.consensus_view}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary">Dissenting Opinions</Typography>
                    <Typography variant="body2">{result.dissenting_opinions}</Typography>
                  </Box>
                </Grid>
              </Grid>
              
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                <Button 
                  startIcon={<DownloadIcon />}
                  size="small"
                >
                  Export Results
                </Button>
              </Box>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Discussion Transcript
              </Typography>
              
              <Box sx={{ mb: 3, maxHeight: '500px', overflowY: 'auto', pr: 1 }}>
                {conversation.map((message, index) => (
                  <Box key={index} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5 }}>
                      <Avatar 
                        sx={{ 
                          bgcolor: message.color,
                          width: 36,
                          height: 36,
                          fontSize: '1.2rem',
                        }}
                      >
                        {message.avatar}
                      </Avatar>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="subtitle2" sx={{ color: message.color }}>
                          {message.speaker}
                        </Typography>
                        <Typography variant="body2">
                          {message.message}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                ))}
              </Box>
              
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                <Button
                  variant="outlined"
                  onClick={() => {
                    setConversation(null);
                    setResult(null);
                  }}
                >
                  New Discussion
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Box>
      )}
    </Box>
  );
} 