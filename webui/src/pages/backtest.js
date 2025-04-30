import { useState } from 'react';
import { Box, Typography, Card, CardContent, TextField, Button, FormControlLabel, Checkbox, Grid, Divider, Tab, Tabs, CircularProgress, Alert, Chip } from '@mui/material';
import { Timeline as TimelineIcon, Insights as InsightsIcon, BarChart as BarChartIcon } from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts';

// Sample backtest results data
const mockBacktestData = {
  performance: [
    { date: '2023-09-01', portfolio: 100000, benchmark: 100000 },
    { date: '2023-09-08', portfolio: 102300, benchmark: 101200 },
    { date: '2023-09-15', portfolio: 101500, benchmark: 100800 },
    { date: '2023-09-22', portfolio: 103800, benchmark: 102300 },
    { date: '2023-09-29', portfolio: 106200, benchmark: 103100 },
    { date: '2023-10-06', portfolio: 105100, benchmark: 102700 },
    { date: '2023-10-13', portfolio: 108700, benchmark: 104500 },
    { date: '2023-10-20', portfolio: 109500, benchmark: 105200 },
    { date: '2023-10-27', portfolio: 112000, benchmark: 106800 },
  ],
  stats: {
    totalReturn: 12.0,
    annualizedReturn: 42.3,
    volatility: 18.7,
    sharpeRatio: 2.26,
    maxDrawdown: -4.32,
    winRate: 67.5,
    benchmarkReturn: 6.8,
  },
  trades: [
    { date: '2023-09-05', ticker: 'AAPL', action: 'buy', quantity: 10, price: 178.5, value: 1785 },
    { date: '2023-09-12', ticker: 'MSFT', action: 'buy', quantity: 5, price: 312.8, value: 1564 },
    { date: '2023-09-19', ticker: 'GOOGL', action: 'buy', quantity: 8, price: 138.2, value: 1105.6 },
    { date: '2023-09-26', ticker: 'AAPL', action: 'sell', quantity: 3, price: 186.4, value: 559.2 },
    { date: '2023-10-03', ticker: 'AMZN', action: 'buy', quantity: 12, price: 127.2, value: 1526.4 },
    { date: '2023-10-10', ticker: 'MSFT', action: 'sell', quantity: 2, price: 328.5, value: 657 },
    { date: '2023-10-17', ticker: 'TSLA', action: 'buy', quantity: 6, price: 245.3, value: 1471.8 },
    { date: '2023-10-24', ticker: 'AMZN', action: 'sell', quantity: 5, price: 132.8, value: 664 },
  ],
  analysts: {
    'warren_buffett_agent': { accuracy: 72.4, profitContribution: 38.2 },
    'charlie_munger_agent': { accuracy: 68.9, profitContribution: 21.7 },
    'cathie_wood_agent': { accuracy: 57.3, profitContribution: 15.4 },
    'technical_analyst_agent': { accuracy: 63.2, profitContribution: 12.8 },
    'fundamentals_agent': { accuracy: 70.5, profitContribution: 11.9 },
  }
};

export default function Backtest() {
  const [tickers, setTickers] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [initialCapital, setInitialCapital] = useState(100000);
  const [marginRequirement, setMarginRequirement] = useState(0.5);
  const [isCrypto, setIsCrypto] = useState(false);
  const [selectedAnalysts, setSelectedAnalysts] = useState([
    'warren_buffett_agent', 'charlie_munger_agent', 'technical_analyst_agent'
  ]);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [activeTab, setActiveTab] = useState(0);

  const handleRunBacktest = () => {
    setIsRunning(true);
    setError(null);
    
    // Simulate API call delay
    setTimeout(() => {
      setIsRunning(false);
      setResults(mockBacktestData);
    }, 2500);
  };

  const handleChangeTab = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Backtest
      </Typography>
      
      {!results ? (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Backtest Configuration
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Ticker Symbols"
                  fullWidth
                  margin="normal"
                  placeholder="AAPL, MSFT, GOOGL"
                  value={tickers}
                  onChange={(e) => setTickers(e.target.value)}
                  helperText="Enter comma-separated ticker symbols"
                />
                
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <TextField
                    label="Start Date"
                    type="date"
                    fullWidth
                    margin="normal"
                    InputLabelProps={{ shrink: true }}
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                  <TextField
                    label="End Date"
                    type="date"
                    fullWidth
                    margin="normal"
                    InputLabelProps={{ shrink: true }}
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  label="Initial Capital"
                  type="number"
                  fullWidth
                  margin="normal"
                  value={initialCapital}
                  onChange={(e) => setInitialCapital(Number(e.target.value))}
                  InputProps={{
                    startAdornment: '$',
                  }}
                />
                
                <TextField
                  label="Margin Requirement"
                  type="number"
                  fullWidth
                  margin="normal"
                  value={marginRequirement}
                  onChange={(e) => setMarginRequirement(Number(e.target.value))}
                  helperText="A value of 0.5 means 50% margin is required for short positions"
                  inputProps={{
                    min: 0,
                    max: 1,
                    step: 0.1,
                  }}
                />
                
                <FormControlLabel
                  control={
                    <Checkbox 
                      checked={isCrypto}
                      onChange={(e) => setIsCrypto(e.target.checked)}
                    />
                  }
                  label="Analyze cryptocurrency instead of stocks"
                />
              </Grid>
            </Grid>
            
            <Divider sx={{ my: 3 }} />
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                variant="contained"
                onClick={handleRunBacktest}
                disabled={!tickers || !startDate || !endDate || isRunning}
                startIcon={isRunning ? <CircularProgress size={20} color="inherit" /> : <TimelineIcon />}
              >
                {isRunning ? 'Running...' : 'Run Backtest'}
              </Button>
            </Box>
            
            {error && (
              <Alert severity="error" sx={{ mt: 3 }}>
                {error}
              </Alert>
            )}
          </CardContent>
        </Card>
      ) : (
        <Box>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs value={activeTab} onChange={handleChangeTab} aria-label="backtest results tabs">
              <Tab icon={<InsightsIcon />} label="Performance" />
              <Tab icon={<BarChartIcon />} label="Statistics" />
              <Tab icon={<TimelineIcon />} label="Trades" />
            </Tabs>
          </Box>
          
          {/* Performance Tab */}
          {activeTab === 0 && (
            <Box>
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Portfolio Performance
                  </Typography>
                  <Box sx={{ height: 400 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart
                        data={results.performance}
                        margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                      >
                        <defs>
                          <linearGradient id="colorPortfolio" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#3f8cff" stopOpacity={0.8}/>
                            <stop offset="95%" stopColor="#3f8cff" stopOpacity={0}/>
                          </linearGradient>
                          <linearGradient id="colorBenchmark" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.8}/>
                            <stop offset="95%" stopColor="#82ca9d" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <XAxis dataKey="date" />
                        <YAxis 
                          domain={['dataMin - 1000', 'dataMax + 1000']}
                          tickFormatter={(value) => `$${value.toLocaleString()}`}
                        />
                        <CartesianGrid strokeDasharray="3 3" />
                        <Tooltip formatter={(value) => [`$${value.toLocaleString()}`]} />
                        <Legend />
                        <Area 
                          type="monotone" 
                          dataKey="portfolio" 
                          stroke="#3f8cff" 
                          fillOpacity={1} 
                          fill="url(#colorPortfolio)" 
                          name="Portfolio" 
                        />
                        <Area 
                          type="monotone" 
                          dataKey="benchmark" 
                          stroke="#82ca9d" 
                          fillOpacity={1} 
                          fill="url(#colorBenchmark)" 
                          name="Benchmark (SPY)" 
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </Box>
                </CardContent>
              </Card>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Key Metrics
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">Total Return</Typography>
                          <Typography variant="body1" color="success.main">{results.stats.totalReturn}%</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">Annualized Return</Typography>
                          <Typography variant="body1" color="success.main">{results.stats.annualizedReturn}%</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">Volatility</Typography>
                          <Typography variant="body1">{results.stats.volatility}%</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">Sharpe Ratio</Typography>
                          <Typography variant="body1">{results.stats.sharpeRatio}</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">Max Drawdown</Typography>
                          <Typography variant="body1" color="error.main">{results.stats.maxDrawdown}%</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">Win Rate</Typography>
                          <Typography variant="body1">{results.stats.winRate}%</Typography>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Analyst Performance
                      </Typography>
                      <Box sx={{ height: 250 }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart
                            data={Object.entries(results.analysts).map(([name, data]) => ({
                              name: name.replace('_agent', '').split('_').map(
                                word => word.charAt(0).toUpperCase() + word.slice(1)
                              ).join(' '),
                              accuracy: data.accuracy,
                              contribution: data.profitContribution
                            }))}
                            margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
                          >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                            <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                            <Tooltip />
                            <Legend />
                            <Bar yAxisId="left" dataKey="accuracy" name="Accuracy (%)" fill="#8884d8" />
                            <Bar yAxisId="right" dataKey="contribution" name="Profit Contribution (%)" fill="#82ca9d" />
                          </BarChart>
                        </ResponsiveContainer>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}
          
          {/* Statistics Tab */}
          {activeTab === 1 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Return Metrics
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                      <Box>
                        <Typography variant="subtitle2">Total Return</Typography>
                        <Box sx={{ mt: 1, height: 10, bgcolor: 'background.paper', borderRadius: 5, overflow: 'hidden' }}>
                          <Box 
                            sx={{ 
                              height: '100%', 
                              width: `${Math.min(100, Math.max(0, results.stats.totalReturn))}%`,
                              bgcolor: 'success.main',
                              borderRadius: 5
                            }} 
                          />
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
                          <Typography variant="body2" color="text.secondary">Portfolio</Typography>
                          <Typography variant="body2" color="success.main">{results.stats.totalReturn}%</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">Benchmark</Typography>
                          <Typography variant="body2">{results.stats.benchmarkReturn}%</Typography>
                        </Box>
                      </Box>
                      
                      <Box>
                        <Typography variant="subtitle2">Risk-Adjusted Return</Typography>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                          <Typography variant="body2" color="text.secondary">Sharpe Ratio</Typography>
                          <Typography variant="body2">{results.stats.sharpeRatio}</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">Volatility</Typography>
                          <Typography variant="body2">{results.stats.volatility}%</Typography>
                        </Box>
                      </Box>
                      
                      <Box>
                        <Typography variant="subtitle2">Win/Loss Statistics</Typography>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                          <Typography variant="body2" color="text.secondary">Win Rate</Typography>
                          <Typography variant="body2">{results.stats.winRate}%</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">Max Drawdown</Typography>
                          <Typography variant="body2" color="error.main">{results.stats.maxDrawdown}%</Typography>
                        </Box>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              {/* Additional statistics cards can go here */}
            </Grid>
          )}
          
          {/* Trades Tab */}
          {activeTab === 2 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Trade History
                </Typography>
                <Box sx={{ overflowX: 'auto' }}>
                  <Box component="table" sx={{ minWidth: 650, borderCollapse: 'separate', borderSpacing: '0 8px', width: '100%' }}>
                    <Box component="thead">
                      <Box component="tr">
                        <Box component="th" sx={{ textAlign: 'left', pb: 2 }}>Date</Box>
                        <Box component="th" sx={{ textAlign: 'left', pb: 2 }}>Ticker</Box>
                        <Box component="th" sx={{ textAlign: 'left', pb: 2 }}>Action</Box>
                        <Box component="th" sx={{ textAlign: 'right', pb: 2 }}>Quantity</Box>
                        <Box component="th" sx={{ textAlign: 'right', pb: 2 }}>Price</Box>
                        <Box component="th" sx={{ textAlign: 'right', pb: 2 }}>Value</Box>
                      </Box>
                    </Box>
                    <Box component="tbody">
                      {results.trades.map((trade, index) => (
                        <Box component="tr" key={index}>
                          <Box component="td" sx={{ py: 1 }}>{trade.date}</Box>
                          <Box component="td" sx={{ py: 1 }}>{trade.ticker}</Box>
                          <Box component="td" sx={{ py: 1 }}>
                            <Chip 
                              label={trade.action.toUpperCase()} 
                              size="small"
                              color={trade.action === 'buy' ? 'success' : 'error'} 
                              variant="outlined"
                            />
                          </Box>
                          <Box component="td" sx={{ py: 1, textAlign: 'right' }}>{trade.quantity}</Box>
                          <Box component="td" sx={{ py: 1, textAlign: 'right' }}>${trade.price.toFixed(2)}</Box>
                          <Box component="td" sx={{ py: 1, textAlign: 'right' }}>${trade.value.toFixed(2)}</Box>
                        </Box>
                      ))}
                    </Box>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          )}
          
          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
            <Button 
              variant="outlined" 
              onClick={() => setResults(null)}
            >
              New Backtest
            </Button>
          </Box>
        </Box>
      )}
    </Box>
  );
} 