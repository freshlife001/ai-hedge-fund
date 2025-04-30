import { useState } from 'react';
import { Box, Typography, Card, CardContent, TextField, Button, Grid, Switch, FormControlLabel, Divider, Select, MenuItem, FormControl, InputLabel, Alert, Snackbar } from '@mui/material';
import { Save as SaveIcon, Refresh as RefreshIcon } from '@mui/icons-material';

export default function Settings() {
  const [openAIKey, setOpenAIKey] = useState('');
  const [anthropicKey, setAnthropicKey] = useState('');
  const [groqKey, setGroqKey] = useState('');
  const [geminiKey, setGeminiKey] = useState('');
  const [defaultModel, setDefaultModel] = useState('gpt-4o');
  const [saveHistory, setSaveHistory] = useState(true);
  const [backtestDefaults, setBacktestDefaults] = useState({
    initialCapital: 100000,
    marginRequirement: 0.5
  });
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  
  const handleSaveSettings = () => {
    setSnackbarMessage('Settings saved successfully');
    setOpenSnackbar(true);
  };
  
  const handleCloseSnackbar = () => {
    setOpenSnackbar(false);
  };
  
  const handleReset = () => {
    setOpenAIKey('');
    setAnthropicKey('');
    setGroqKey('');
    setGeminiKey('');
    setDefaultModel('gpt-4o');
    setSaveHistory(true);
    setBacktestDefaults({
      initialCapital: 100000,
      marginRequirement: 0.5
    });
    
    setSnackbarMessage('Settings reset to defaults');
    setOpenSnackbar(true);
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Settings
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                API Keys
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <TextField
                  label="OpenAI API Key"
                  fullWidth
                  margin="normal"
                  type="password"
                  value={openAIKey}
                  onChange={(e) => setOpenAIKey(e.target.value)}
                  placeholder="sk-..."
                />
                
                <TextField
                  label="Anthropic API Key"
                  fullWidth
                  margin="normal"
                  type="password"
                  value={anthropicKey}
                  onChange={(e) => setAnthropicKey(e.target.value)}
                  placeholder="sk-ant-..."
                />
                
                <TextField
                  label="Groq API Key"
                  fullWidth
                  margin="normal"
                  type="password"
                  value={groqKey}
                  onChange={(e) => setGroqKey(e.target.value)}
                  placeholder="gsk_..."
                />
                
                <TextField
                  label="Gemini API Key"
                  fullWidth
                  margin="normal"
                  type="password"
                  value={geminiKey}
                  onChange={(e) => setGeminiKey(e.target.value)}
                  placeholder="..."
                />
              </Box>
              
              <Typography variant="h6" gutterBottom>
                Default Model
              </Typography>
              
              <FormControl fullWidth margin="normal">
                <InputLabel>Default LLM Model</InputLabel>
                <Select
                  value={defaultModel}
                  label="Default LLM Model"
                  onChange={(e) => setDefaultModel(e.target.value)}
                >
                  <MenuItem value="gpt-4o">[openai] gpt-4o</MenuItem>
                  <MenuItem value="gpt-4o-mini">[openai] gpt-4o-mini</MenuItem>
                  <MenuItem value="claude-3-5-sonnet-latest">[anthropic] claude-3.5-sonnet</MenuItem>
                  <MenuItem value="claude-3-7-sonnet-latest">[anthropic] claude-3.7-sonnet</MenuItem>
                  <MenuItem value="deepseek-r1-distill-llama-70b">[groq] deepseek-r1 70b</MenuItem>
                  <MenuItem value="llama-3.3-70b-versatile">[groq] llama-3.3 70b</MenuItem>
                  <MenuItem value="gemini-2.0-flash">[gemini] gemini-2.0-flash</MenuItem>
                </Select>
              </FormControl>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Application Settings
              </Typography>
              
              <FormControlLabel
                control={
                  <Switch 
                    checked={saveHistory}
                    onChange={(e) => setSaveHistory(e.target.checked)}
                  />
                }
                label="Save analysis history"
              />
              
              <Divider sx={{ my: 3 }} />
              
              <Typography variant="h6" gutterBottom>
                Backtest Defaults
              </Typography>
              
              <TextField
                label="Initial Capital"
                fullWidth
                margin="normal"
                type="number"
                value={backtestDefaults.initialCapital}
                onChange={(e) => setBacktestDefaults({...backtestDefaults, initialCapital: Number(e.target.value)})}
                InputProps={{
                  startAdornment: '$',
                }}
              />
              
              <TextField
                label="Default Margin Requirement"
                fullWidth
                margin="normal"
                type="number"
                value={backtestDefaults.marginRequirement}
                onChange={(e) => setBacktestDefaults({...backtestDefaults, marginRequirement: Number(e.target.value)})}
                inputProps={{
                  min: 0,
                  max: 1,
                  step: 0.1,
                }}
                helperText="A value of 0.5 means 50% margin is required for short positions"
              />
              
              <Alert severity="info" sx={{ mt: 3 }}>
                These settings are used as defaults for new backtest runs. You can override them when setting up individual backtests.
              </Alert>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 3 }}>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={handleReset}
        >
          Reset to Defaults
        </Button>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={handleSaveSettings}
        >
          Save Settings
        </Button>
      </Box>
      
      <Snackbar
        open={openSnackbar}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        message={snackbarMessage}
      />
    </Box>
  );
} 