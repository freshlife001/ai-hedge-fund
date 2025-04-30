import { useState } from 'react';
import { Box, Typography, Card, CardContent, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Chip, IconButton, Button, Menu, MenuItem, ListItemIcon, ListItemText } from '@mui/material';
import { MoreVert as MoreVertIcon, Delete as DeleteIcon, Visibility as VisibilityIcon, GetApp as GetAppIcon, ContentCopy as ContentCopyIcon } from '@mui/icons-material';

// Sample history data
const sampleHistory = [
  { 
    id: 1, 
    date: '2023-10-27', 
    type: 'Analysis', 
    tickers: ['AAPL', 'MSFT', 'GOOGL'], 
    signals: {'AAPL': 'bullish', 'MSFT': 'bullish', 'GOOGL': 'neutral'},
    model: 'gpt-4o',
    analysts: ['Warren Buffett', 'Charlie Munger', 'Ben Graham', 'Technical Analyst']
  },
  { 
    id: 2, 
    date: '2023-10-25', 
    type: 'Backtest', 
    tickers: ['AMZN', 'TSLA', 'META'], 
    performance: 12.3,
    startDate: '2023-01-01',
    endDate: '2023-10-01',
    model: 'claude-3-5-sonnet-latest'
  },
  { 
    id: 3, 
    date: '2023-10-22', 
    type: 'Round Table', 
    tickers: ['NVDA'], 
    signal: 'bullish',
    confidence: 65,
    model: 'gpt-4o',
    participants: ['Warren Buffett', 'Cathie Wood', 'Technical Analyst', 'Bill Ackman', 'WSB']
  },
  { 
    id: 4, 
    date: '2023-10-20', 
    type: 'Analysis', 
    tickers: ['V', 'MA', 'PYPL', 'SQ'], 
    signals: {'V': 'bullish', 'MA': 'bullish', 'PYPL': 'bearish', 'SQ': 'neutral'},
    model: 'deepseek-r1-distill-llama-70b',
    analysts: ['Warren Buffett', 'Cathie Wood', 'Fundamental Analyst']
  },
  { 
    id: 5, 
    date: '2023-10-15', 
    type: 'Backtest', 
    tickers: ['BTC-USD', 'ETH-USD'], 
    performance: 8.7,
    startDate: '2023-05-01',
    endDate: '2023-10-01',
    model: 'claude-3-5-sonnet-latest',
    isCrypto: true
  },
];

export default function History() {
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);
  const open = Boolean(anchorEl);
  
  const handleMenuClick = (event, item) => {
    setAnchorEl(event.currentTarget);
    setSelectedItem(item);
  };
  
  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedItem(null);
  };
  
  const handleView = () => {
    console.log('View', selectedItem);
    handleMenuClose();
  };
  
  const handleDownload = () => {
    console.log('Download', selectedItem);
    handleMenuClose();
  };
  
  const handleCopy = () => {
    console.log('Copy', selectedItem);
    handleMenuClose();
  };
  
  const handleDelete = () => {
    console.log('Delete', selectedItem);
    handleMenuClose();
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Analysis History
      </Typography>
      
      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Tickers</TableCell>
                  <TableCell>Results</TableCell>
                  <TableCell>Model</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {sampleHistory.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.date}</TableCell>
                    <TableCell>
                      <Chip 
                        label={item.type} 
                        size="small" 
                        color={
                          item.type === 'Analysis' ? 'primary' : 
                          item.type === 'Backtest' ? 'info' : 'secondary'
                        }
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {item.tickers.map((ticker) => (
                          <Chip 
                            key={ticker} 
                            label={ticker} 
                            size="small" 
                            variant="outlined"
                            color={item.isCrypto ? "warning" : "default"}
                          />
                        ))}
                      </Box>
                    </TableCell>
                    <TableCell>
                      {item.type === 'Analysis' && (
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                          {Object.entries(item.signals).map(([ticker, signal]) => (
                            <Chip 
                              key={ticker} 
                              label={`${ticker}: ${signal}`} 
                              size="small" 
                              color={
                                signal === 'bullish' ? 'success' : 
                                signal === 'bearish' ? 'error' : 'warning'
                              }
                            />
                          ))}
                        </Box>
                      )}
                      {item.type === 'Backtest' && (
                        <Typography variant="body2" color={item.performance > 0 ? 'success.main' : 'error.main'}>
                          {item.performance > 0 ? '+' : ''}{item.performance}% return
                        </Typography>
                      )}
                      {item.type === 'Round Table' && (
                        <Chip 
                          label={`${item.signal.toUpperCase()} (${item.confidence}%)`} 
                          size="small" 
                          color={
                            item.signal === 'bullish' ? 'success' : 
                            item.signal === 'bearish' ? 'error' : 'warning'
                          }
                        />
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>
                        {item.model.replace('-latest', '')}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <IconButton size="small" onClick={(e) => handleMenuClick(e, item)}>
                        <MoreVertIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
      
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleView}>
          <ListItemIcon>
            <VisibilityIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>View Details</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleDownload}>
          <ListItemIcon>
            <GetAppIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Download</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleCopy}>
          <ListItemIcon>
            <ContentCopyIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Duplicate</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleDelete}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText sx={{ color: 'error.main' }}>Delete</ListItemText>
        </MenuItem>
      </Menu>
    </Box>
  );
} 