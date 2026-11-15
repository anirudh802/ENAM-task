import { useState, useEffect } from 'react';
import { api } from '../services/api';

function urlBase64ToUint8Array(base64String: string) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export function useWebPush() {
  const [isSupported, setIsSupported] = useState(true);
  const [permission, setPermission] = useState<NotificationPermission>('granted');
  const [isSubscribed, setIsSubscribed] = useState(() => {
    const saved = localStorage.getItem('finn-push-active');
    return saved !== null ? saved === 'true' : true;
  });
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if ('serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window) {
      setIsSupported(true);
      setPermission(Notification.permission);
      navigator.serviceWorker.ready.then(reg => {
        reg.pushManager.getSubscription().then(sub => {
          if (sub) {
            setIsSubscribed(true);
            localStorage.setItem('finn-push-active', 'true');
          }
        });
      });
    }
  }, []);

  const subscribe = async () => {
    if (!isSupported) return false;
    setIsLoading(true);
    try {
      const perm = await Notification.requestPermission();
      setPermission(perm);
      if (perm !== 'granted') {
        setIsLoading(false);
        return false;
      }

      const reg = await navigator.serviceWorker.ready;
      const { public_key } = await api.getVapidKey();
      const applicationServerKey = urlBase64ToUint8Array(public_key);

      const subscription = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey,
      });

      await api.subscribePush(subscription.toJSON() as any);
      setIsSubscribed(true);
      setIsLoading(false);
      return true;
    } catch (err) {
      console.error('Failed to subscribe to Web Push:', err);
      setIsLoading(false);
      return false;
    }
  };

  const triggerTestAlert = async () => {
    try {
      await api.sendTestPush();
      return true;
    } catch (err) {
      console.error('Test notification failed:', err);
      return false;
    }
  };

  return {
    isSupported,
    permission,
    isSubscribed,
    isLoading,
    subscribe,
    triggerTestAlert,
  };
}
