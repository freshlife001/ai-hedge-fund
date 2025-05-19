import { verifyToken, decodeUserFromToken } from '../../../utils/auth';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const token = req.cookies.jwtToken;
    if (!token) {
      return res.status(401).json({ message: 'No token provided' });
    }

    const verified = verifyToken(token);
    if (!verified) {
      return res.status(401).json({ message: 'Invalid token' });
    }

    // Return user info from decoded token
    res.status(200).json({
      user: decodeUserFromToken(token),
    });
  } catch (error) {
    console.error('Error in /api/auth/me:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
}