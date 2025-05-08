import { runAsk } from '../../utils/api';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
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