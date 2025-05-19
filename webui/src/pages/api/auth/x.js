import { TwitterApi } from 'twitter-api-v2';
import { serialize, parse } from 'cookie';
import { verifyToken } from '../../../utils/auth';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Check for valid JWT token
  const cookies = parse(req.headers.cookie || '');
  const token = cookies.jwtToken;
  if (token && verifyToken(token)) {
    return res.redirect(req.query.redirect || '/');
  }
  const client = new TwitterApi({
    clientId: process.env.TWITTER_CLIENT_ID,
    clientSecret: process.env.TWITTER_CLIENT_SECRET
  });

  try {
    const { url, codeVerifier, state } = client.generateOAuth2AuthLink(
      `${process.env.NEXT_PUBLIC_BASE_URL}/api/auth/x/callback`,
      { scope: ['tweet.read', 'users.read', 'offline.access'] }
    );

    res.setHeader('Set-Cookie', [
      serialize('twitter_code_verifier', codeVerifier, {
        path: '/',
        httpOnly: true,
        maxAge: 60 * 10, // 10 minutes
      }),
      serialize('twitter_state', state, {
        path: '/',
        httpOnly: true,
        maxAge: 60 * 10, // 10 minutes
      }),
      serialize('twitter_redirect', req.query.redirect || '/', {
        path: '/',
        httpOnly: true,
        maxAge: 60 * 10 // 10 minutes
      })
    ]);

    return res.redirect(url);
  } catch (error) {
    console.error('Twitter auth error:', error);
    return res.status(500).json({ error: 'Failed to initiate Twitter auth' });
  }
}