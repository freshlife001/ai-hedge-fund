import { Box, Typography, Button, Card, CardContent, Grid } from '@mui/material';
import { Assessment as AssessmentIcon } from '@mui/icons-material';
import Link from 'next/link';

export default function Home() {
  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <Box>
          <Link href="/analysis" passHref legacyBehavior>
            <Button 
              variant="contained" 
              color="primary" 
              component="a"
              startIcon={<AssessmentIcon />}
            >
              New Analysis
            </Button>
          </Link>
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Welcome to Hedge Fund AI
              </Typography>
              <Typography variant="body1">
                This platform provides AI-powered investment analysis combining multiple strategies and analyst personas.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
} 