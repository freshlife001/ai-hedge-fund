import { runAnalysis } from '../../utils/api';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
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