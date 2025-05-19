import { TwitterApi } from 'twitter-api-v2';
import { serialize, parse } from 'cookie';
import { generateToken } from '../../../../utils/auth';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { code, state } = req.query;
  const cookies = parse(req.headers.cookie || '');
  
  if (!cookies.twitter_code_verifier || !cookies.twitter_state || state !== cookies.twitter_state) {
    return res.status(400).json({ error: 'Invalid state or missing code verifier' });
  }

  const client = new TwitterApi({
    clientId: process.env.TWITTER_CLIENT_ID,
    clientSecret: process.env.TWITTER_CLIENT_SECRET
  });

  try {
    const { accessToken, refreshToken } = await client.loginWithOAuth2({
      code,
      codeVerifier: cookies.twitter_code_verifier,
      redirectUri: `${process.env.NEXT_PUBLIC_BASE_URL}/api/auth/x/callback`
    });

    // Get user profile from Twitter
    const twitterClient = new TwitterApi(accessToken);
    const { data: userData } = await twitterClient.v2.me({
      'user.fields': 'id,name,username,profile_image_url,verified'
    });
    console.log(userData);
    // Generate JWT token
    const jwtToken = generateToken({
      id: userData.id,
      username: userData.username,
      name: userData.name,
      twitterAccessToken: accessToken,
      twitterAvatar: userData.profile_image_url
    });
    
    // Store tokens securely
    res.setHeader('Set-Cookie', [
      serialize('twitter_access_token', accessToken, {
        path: '/',
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        maxAge: 60 * 60 * 24 * 7 // 1 week
      }),
      serialize('twitter_refresh_token', refreshToken, {
        path: '/',
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        maxAge: 60 * 60 * 24 * 30 // 1 month
      })
    ]);

    // Redirect to success page
    const redirectPath = req.cookies.twitter_redirect || '/';
    res.setHeader('Set-Cookie', [
        serialize('twitter_redirect', '', {
        path: '/',
        expires: new Date(0)
      }),
      serialize('jwtToken', jwtToken, {
        path: '/',
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        maxAge: 60 * 60 * 24 * 30 // 1 month
      })
    ]);
    return res.redirect(redirectPath);
  } catch (error) {
    console.error('Twitter callback error:', error);
    return res.status(500).json({ error: 'Failed to authenticate with Twitter' });
  }
}