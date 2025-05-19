import { verifyToken } from '../../utils/auth';
import { v4 as uuidv4 } from 'uuid';
import fs from 'fs';
import path from 'path';

// Define the storage directory for conversations
const STORAGE_DIR = path.join(process.cwd(), 'data', 'conversations');

// Ensure the storage directory exists
if (!fs.existsSync(STORAGE_DIR)) {
  fs.mkdirSync(STORAGE_DIR, { recursive: true });
}

export default async function handler(req, res) {
  // Handle GET request to retrieve a conversation by ID
  if (req.method === 'GET') {
    try {
      // Get conversation ID from query parameters
      const { id } = req.query;
      
      if (!id) {
        return res.status(400).json({ message: 'Conversation ID is required' });
      }
      
      // Validate UUID format
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
      if (!uuidRegex.test(id)) {
        return res.status(400).json({ message: 'Invalid conversation ID format' });
      }

      // Construct file path
      const filePath = path.join(STORAGE_DIR, `${id}.json`);
      
      // Check if file exists
      if (!fs.existsSync(filePath)) {
        return res.status(404).json({ message: 'Conversation not found' });
      }

      // Read and parse the conversation file
      const conversationData = fs.readFileSync(filePath, 'utf8');
      const conversation = JSON.parse(conversationData);

      // Return the conversation data
      return res.status(200).json({
        success: true,
        conversation
      });
    } catch (error) {
      console.error('Error retrieving conversation:', error);
      return res.status(500).json({ message: 'Internal server error' });
    }
  }
  
  // Handle POST request to save a new conversation
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    // Verify authentication
    const token = req.cookies.jwtToken;
    if (!token) {
      return res.status(401).json({ message: 'No token provided' });
    }

    const verified = verifyToken(token);
    if (!verified) {
      return res.status(401).json({ message: 'Invalid token' });
    }

    // Generate a unique conversation ID
    const conversationId = uuidv4();
    
    // Get conversation data from request body
    const { messages, agent, ticker, isCrypto } = req.body;
    
    if (!messages || !Array.isArray(messages)) {
      return res.status(400).json({ message: 'Invalid conversation data' });
    }

    // Create conversation object with timestamp
    const conversation = {
      id: conversationId,
      timestamp: new Date().toISOString(),
      messages,
      agent, ticker, isCrypto
    };

    // Save conversation to file
    const filePath = path.join(STORAGE_DIR, `${conversationId}.json`);
    fs.writeFileSync(filePath, JSON.stringify(conversation, null, 2));

    // Return success with the conversation ID
    res.status(200).json({
      success: true,
      conversationId,
      message: 'Conversation saved successfully'
    });
  } catch (error) {
    console.error('Error saving conversation:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
}