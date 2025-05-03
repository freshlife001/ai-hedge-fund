# Active Context: AI Hedge Fund Web Interface

## Current Work Focus

### Standalone Pages
We've implemented a pattern for creating standalone pages that don't use the main application layout with the sidebar navigation. This is achieved using Next.js's `getLayout` pattern:

1. Pages can define their own custom layout by implementing a `getLayout` function
2. The `_app.js` file checks for this function and uses it when available
3. This allows for specialized pages like the Ask page to have a focused, distraction-free interface

The AI Hedge Fund Web Interface is currently in development with a focus on implementing the core features outlined in the project brief. The application provides a modern web interface for AI-driven investment analysis, backtesting, and portfolio management.

## Recent Changes

- Established the Memory Bank documentation structure
- Analyzed existing codebase to understand the application architecture
- Documented the project's purpose, technical context, and system patterns

## Next Steps

1. **Feature Completion**
   - Ensure all planned features are fully implemented
   - Complete any missing functionality in analysis, backtest, and round-table pages
   - Implement history tracking for past analyses

2. **UI/UX Improvements**
   - Enhance data visualizations for better readability
   - Improve responsive design for mobile devices
   - Refine user flows for complex operations

3. **API Integration**
   - Ensure robust error handling for API calls
   - Implement loading states for better user experience
   - Add caching mechanisms for frequently accessed data

## Active Decisions and Considerations

1. **UI Framework**
   - Using Material UI for consistent design language
   - Dark theme implementation for better readability of financial data
   - Considering additional UI components for specialized financial displays

2. **Data Visualization**
   - Using Recharts as primary charting library
   - Chart.js and React-Chartjs-2 available for specific visualization needs
   - Need to standardize chart styling across the application

3. **State Management**
   - Currently using local component state
   - May need to consider more robust state management if complexity increases
   - Evaluating whether context API would be beneficial for shared state

## Important Patterns and Preferences

1. **Code Organization**
   - Page-based structure following Next.js conventions
   - Component-based architecture with reusable UI elements
   - Utility functions centralized in dedicated files

2. **Styling Approach**
   - Material UI's styling system with theme customization
   - Consistent spacing and typography throughout the application
   - Dark theme as default for financial data visualization

3. **API Integration**
   - Centralized API utilities in `src/utils/api.js`
   - Consistent error handling patterns
   - Axios for HTTP requests with configurable base URL

## Learnings and Project Insights

1. **Financial Data Visualization**
   - Complex financial data requires thoughtful visualization
   - Multiple chart types needed for different metrics
   - Interactive elements enhance user understanding

2. **AI Integration Challenges**
   - Balancing between showing AI reasoning and keeping UI clean
   - Managing potential latency from AI processing
   - Presenting multiple AI perspectives in an understandable way

3. **User Experience Considerations**
   - Financial analysis tools need to be both powerful and accessible
   - Step-based workflows help manage complexity
   - Clear presentation of results is critical for user understanding

This active context document captures the current state of development, ongoing decisions, and important considerations for the AI Hedge Fund Web Interface project. It serves as a living document that will be updated as the project evolves.