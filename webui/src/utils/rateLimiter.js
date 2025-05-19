import { verifyToken } from './auth';
import { parse } from 'cookie';
import { promises as fs } from 'fs';
import path from 'path';

const RATE_LIMIT_FILE = path.join(process.cwd(), 'rate-limits.json');
const MAX_CALLS_PER_USER = 10;
const WINDOW_MS = 24 * 60 * 60 * 1000; // 24 hours

async function loadRateLimits() {
  try {
    const data = await fs.readFile(RATE_LIMIT_FILE, 'utf-8');
    return JSON.parse(data);
  } catch (err) {
    return {};
  }
}

async function saveRateLimits(limits) {
  await fs.writeFile(RATE_LIMIT_FILE, JSON.stringify(limits));
}

export async function checkRateLimit(req) {
  const cookies = parse(req.headers.cookie || '');
  const token = cookies.jwtToken;
  if (!token || !verifyToken(token)) {
    return { allowed: false, status: 401, message: 'Unauthorized' };
  }

  const decoded = verifyToken(token);
  const userId = decoded.user.id;
  const now = Date.now();
  
  const limits = await loadRateLimits();
  const userLimit = limits[userId] || { count: 0, lastReset: now };

  // Reset counter if window has passed
  if (now - userLimit.lastReset > WINDOW_MS) {
    userLimit.count = 0;
    userLimit.lastReset = now;
  }

  // Check limit
  if (userLimit.count >= MAX_CALLS_PER_USER) {
    return { 
      allowed: false, 
      status: 429, 
      message: 'Rate limit exceeded. Please try again later.' 
    };
  }

  // Increment count
  userLimit.count += 1;
  limits[userId] = userLimit;
  await saveRateLimits(limits);

  return { allowed: true };
}