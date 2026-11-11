import { useState, useEffect } from 'react';

function useOnlineStatus() {
  // Manage current online status with state
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  
  useEffect(() => {
    // Function to execute when switching to online
    function handleOnline() {
      setIsOnline(true);
      console.log('Internet connection restored!');
    }
    
    // Function to execute when switching to offline
    function handleOffline() {
      setIsOnline(false);
      console.log('Internet connection lost.');
    }
    
    // Register event listeners
    // These functions execute when browser detects online/offline status changes
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    // Remove event listeners when component unmounts
    // This is essential to prevent memory leaks
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []); // Empty array: execute once when component mounts
  
  return isOnline;
}

export default useOnlineStatus;