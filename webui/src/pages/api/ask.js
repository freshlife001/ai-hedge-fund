import { runAsk } from '../../utils/api';
import { verifyToken } from '../../utils/auth';
import { checkRateLimit } from '../../utils/rateLimiter';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  // Check rate limit and authentication
  const rateLimit = await checkRateLimit(req);
  if (!rateLimit.allowed) {
    return res.status(rateLimit.status).json({ message: rateLimit.message });
  }

  try {
    const {
      ticker,
      question,
      modelName,
      selectedAgent,
      isCrypto,
      context
    } = req.body;

    const results = await runAsk({
      ticker,
      question,
      modelName,
      selectedAgent,
      isCrypto,
      context
    });

    res.status(200).json(results);
  } catch (error) {
    console.error('Ask error:', error);
    res.status(500).json({ message: error.message });
  }
}