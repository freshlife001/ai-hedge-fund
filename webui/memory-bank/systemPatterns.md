# System Patterns: AI Hedge Fund Web Interface

## System Architecture

The AI Hedge Fund Web Interface follows a client-side rendering architecture using Next.js as the frontend framework. The application communicates with a backend API that handles the AI analysis and data processing.

```
┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │
│  Next.js        │      │  Backend API    │
│  Frontend       │◄────►│  (AI Analysis)  │
│                 │      │                 │
└─────────────────┘      └─────────────────┘
```

## Key Technical Decisions

1. **Next.js Framework**
   - Provides server-side rendering capabilities when needed
   - Enables client-side navigation for smooth user experience
   - Simplifies routing and page management

2. **Material UI Component Library**
   - Consistent design language across the application
   - Responsive components that work across devices
   - Dark theme implementation for better readability of financial data

3. **API Integration Pattern**
   - Centralized API utilities in `src/utils/api.js`
   - Consistent error handling and response processing
   - Axios for HTTP requests with configurable base URL

4. **State Management**
   - Local component state for UI elements
   - Form state managed within relevant page components
   - API response data stored in component state

## Design Patterns

1. **Page-Based Organization**
   - Each major feature has its own page component
   - Pages follow consistent layout structure
   - Common UI elements extracted to shared components

2. **Layout Component Pattern**
   - Shared layout wrapper (`Layout.js`) for consistent UI
   - Navigation sidebar with responsive behavior
   - Content area with appropriate padding and structure

3. **Data Visualization Pattern**
   - Chart components from Recharts library
   - Consistent color schemes and styling
   - Responsive sizing based on viewport

4. **Form Handling Pattern**
   - Controlled components for form inputs
   - Step-based forms for complex workflows
   - Validation before submission

## Component Relationships

1. **Layout Hierarchy**
   ```
   _app.js
     └── ThemeProvider
         └── Layout
             ├── AppBar/Toolbar
             ├── Drawer/Navigation
             └── Content Area
                 └── Page Components
   ```

2. **Page Structure**
   - Each page follows similar structure:
     - Header section with title and actions
     - Content section with cards/forms
     - Results section when applicable

3. **Console Component**
   - `EnhancedConsole` provides debugging capabilities
   - Implemented as a floating UI element
   - Can be toggled on/off as needed

## Critical Implementation Paths

1. **Analysis Workflow**
   - User input → API request → Processing → Results display
   - Multiple analyst selection and configuration
   - Results presentation with reasoning

2. **Backtest Visualization**
   - Historical data processing
   - Performance metrics calculation
   - Chart rendering with interactive elements

3. **Round Table Discussion**
   - AI persona selection
   - Discussion generation through API
   - Structured presentation of dialogue

This document outlines the key architectural patterns and design decisions that shape the AI Hedge Fund Web Interface, providing a foundation for understanding the system's structure and organization.