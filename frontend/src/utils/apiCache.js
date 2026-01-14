/**
 * Simple in-memory cache for API responses
 * Reduces duplicate API calls and improves performance
 */

const cache = new Map();
const CACHE_DURATION = 30000; // 30 seconds

class APICache {
  set(key, data) {
    cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  get(key) {
    const item = cache.get(key);
    if (!item) return null;
    
    // Check if cache is still valid
    if (Date.now() - item.timestamp > CACHE_DURATION) {
      cache.delete(key);
      return null;
    }
    
    return item.data;
  }

  clear() {
    cache.clear();
  }

  clearByPrefix(prefix) {
    for (const key of cache.keys()) {
      if (key.startsWith(prefix)) {
        cache.delete(key);
      }
    }
  }
}

export const apiCache = new APICache();

/**
 * Fetch with cache support
 * @param {string} url - API URL
 * @param {object} options - fetch options
 * @param {number} cacheDuration - cache duration in ms (default: 30s)
 */
export async function cachedFetch(url, options = {}, cacheDuration = 30000) {
  const cacheKey = `${url}_${JSON.stringify(options)}`;
  
  // Check cache first
  const cached = apiCache.get(cacheKey);
  if (cached) {
    return cached;
  }
  
  // Fetch from API
  const response = await fetch(url, options);
  
  if (response.ok) {
    const data = await response.json();
    apiCache.set(cacheKey, data);
    return data;
  }
  
  throw new Error(`HTTP ${response.status}`);
}
