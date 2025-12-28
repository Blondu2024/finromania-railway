/**
 * Push Notifications Utility for FinRomania
 * Handles service worker registration and push subscription management
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Check if push notifications are supported
export const isPushSupported = () => {
  return 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;
};

// Get current notification permission status
export const getPermissionStatus = () => {
  if (!isPushSupported()) return 'unsupported';
  return Notification.permission; // 'granted', 'denied', or 'default'
};

// Register service worker
export const registerServiceWorker = async () => {
  if (!('serviceWorker' in navigator)) {
    console.warn('Service workers not supported');
    return null;
  }

  try {
    const registration = await navigator.serviceWorker.register('/sw.js');
    console.log('Service Worker registered:', registration.scope);
    return registration;
  } catch (error) {
    console.error('Service Worker registration failed:', error);
    return null;
  }
};

// Get VAPID public key from server
const getVapidPublicKey = async () => {
  try {
    const response = await fetch(`${API_URL}/api/push/vapid-key`);
    if (!response.ok) throw new Error('Failed to get VAPID key');
    const data = await response.json();
    return data.publicKey;
  } catch (error) {
    console.error('Error getting VAPID key:', error);
    return null;
  }
};

// Convert VAPID key to Uint8Array
const urlBase64ToUint8Array = (base64String) => {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
};

// Request notification permission and subscribe
export const subscribeToPush = async (token) => {
  if (!isPushSupported()) {
    return { success: false, error: 'Push notifications not supported' };
  }

  try {
    // Request permission
    const permission = await Notification.requestPermission();
    if (permission !== 'granted') {
      return { success: false, error: 'Permission denied' };
    }

    // Get service worker registration
    const registration = await navigator.serviceWorker.ready;

    // Get VAPID public key
    const vapidPublicKey = await getVapidPublicKey();
    if (!vapidPublicKey) {
      return { success: false, error: 'Could not get VAPID key' };
    }

    // Subscribe to push
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
    });

    // Send subscription to server
    const response = await fetch(`${API_URL}/api/push/subscribe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        endpoint: subscription.endpoint,
        keys: {
          p256dh: btoa(String.fromCharCode.apply(null, new Uint8Array(subscription.getKey('p256dh')))),
          auth: btoa(String.fromCharCode.apply(null, new Uint8Array(subscription.getKey('auth'))))
        }
      })
    });

    if (!response.ok) {
      throw new Error('Failed to save subscription on server');
    }

    console.log('Push subscription successful');
    return { success: true, subscription };

  } catch (error) {
    console.error('Error subscribing to push:', error);
    return { success: false, error: error.message };
  }
};

// Unsubscribe from push notifications
export const unsubscribeFromPush = async (token) => {
  try {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();

    if (subscription) {
      // Unsubscribe locally
      await subscription.unsubscribe();

      // Notify server
      await fetch(`${API_URL}/api/push/unsubscribe`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          endpoint: subscription.endpoint,
          keys: {}
        })
      });
    }

    return { success: true };
  } catch (error) {
    console.error('Error unsubscribing from push:', error);
    return { success: false, error: error.message };
  }
};

// Check if currently subscribed
export const isSubscribed = async () => {
  if (!isPushSupported()) return false;

  try {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();
    return subscription !== null;
  } catch (error) {
    console.error('Error checking subscription:', error);
    return false;
  }
};

// Get subscription status from server
export const getPushStatus = async (token) => {
  try {
    const response = await fetch(`${API_URL}/api/push/status`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) throw new Error('Failed to get push status');
    return await response.json();
  } catch (error) {
    console.error('Error getting push status:', error);
    return { subscribed: false, subscription_count: 0 };
  }
};

// Send test notification
export const sendTestNotification = async (token) => {
  try {
    const response = await fetch(`${API_URL}/api/push/test`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || 'Failed to send test');
    }
    return await response.json();
  } catch (error) {
    console.error('Error sending test notification:', error);
    return { success: false, error: error.message };
  }
};

// Initialize push notifications on app load
export const initializePushNotifications = async () => {
  if (!isPushSupported()) {
    console.log('Push notifications not supported');
    return false;
  }

  try {
    await registerServiceWorker();
    return true;
  } catch (error) {
    console.error('Error initializing push:', error);
    return false;
  }
};
