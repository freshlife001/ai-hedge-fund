import { runAnalysis } from '../../utils/api';
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
      tickers,
      modelName,
      selectedAnalysts,
      initialCash,
      isCrypto,
      showReasoning,
      runRoundTable
    } = req.body;

    const results = await runAnalysis({
      tickers,
      modelName,
      selectedAnalysts,
      initialCash,
      isCrypto,
      showReasoning,
      runRoundTable
    });

    res.status(200).json(results);
  } catch (error) {
    console.error('Analysis error:', error);
    res.status(500).json({ message: error.message });
  }
}