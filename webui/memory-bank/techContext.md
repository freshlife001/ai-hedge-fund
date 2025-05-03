# Technical Context: AI Hedge Fund Web Interface

## Technologies Used

### Frontend Framework
- **Next.js** (v14.0.1): React framework for production-grade applications
- **React** (v18.3.1): JavaScript library for building user interfaces

### UI Components
- **Material UI** (v5.16.14): React component library implementing Google's Material Design
- **Emotion** (v11.14.0): CSS-in-JS library used by Material UI
- **MUI Icons** (v5.16.14): Icon set for Material UI

### Data Visualization
- **Chart.js** (v4.4.8): JavaScript charting library
- **React-Chartjs-2** (v5.3.0): React wrapper for Chart.js
- **Recharts** (v2.15.1): Composable charting library built on React components

### HTTP Client
- **Axios** (v1.8.2): Promise-based HTTP client for making API requests

### Animation
- **Framer Motion** (v10.18.0): Animation library for React

### Development Tools
- **TypeScript** (v5.2.2): Typed JavaScript
- **ESLint** (v8.53.0): JavaScript linting utility
- **Tailwind CSS** (v3.3.5): Utility-first CSS framework
- **PostCSS** (v8.4.31): Tool for transforming CSS with JavaScript
- **Autoprefixer** (v10.4.16): PostCSS plugin to parse CSS and add vendor prefixes

## Development Setup

### Package Management
- **Yarn** (v1.22.22): Package manager for JavaScript

### Scripts
- `yarn dev`: Starts development server
- `yarn build`: Builds the application for production
- `yarn start`: Starts the production server
- `yarn lint`: Runs ESLint to check code quality

### Environment
- Development server runs on `http://localhost:3000` by default
- Backend API expected at `http://localhost:5010`

## Technical Constraints

### API Dependencies
- The application relies on a backend API for:
  - AI model access
  - Financial data retrieval
  - Analysis processing
  - Backtesting calculations

### Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- No explicit support for legacy browsers

### Performance Considerations
- Large datasets for financial analysis
- Complex visualizations may impact performance
- AI processing may have latency depending on backend capabilities

## Dependencies

### External Services
- Backend API service (running on port 5010)
- Financial data providers (accessed through backend)
- AI model providers (accessed through backend)

### Internal Dependencies
- Theme configuration in `src/theme/darkTheme.js`
- API utilities in `src/utils/api.js`
- Layout components in `src/components/Layout.js`
- Console utilities in `src/components/EnhancedConsole.js`

## Tool Usage Patterns

### API Calls
```javascript
// Example API call pattern from src/utils/api.js
export const runAnalysis = async (params) => {
  try {
    const response = await api.post('/api/analysis', params);
    return response.data;
  } catch (error) {
    console.error('Error running analysis:', error);
    throw error;
  }
};
```

### Component Structure
```javascript
// Example component structure pattern
export default function ComponentName() {
  // State declarations
  const [data, setData] = useState(null);
  
  // Effect hooks
  useEffect(() => {
    // Data fetching or initialization
  }, []);
  
  // Event handlers
  const handleAction = () => {
    // Action implementation
  };
  
  // Render
  return (
    <Box>
      {/* Component JSX */}
    </Box>
  );
}
```

This technical context document provides an overview of the technologies, development setup, and technical constraints of the AI Hedge Fund Web Interface, serving as a reference for understanding the technical foundation of the project.