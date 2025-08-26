/**
 * SSR Verification Test
 * 
 * This script verifies that the auth store can be safely imported
 * and initialized in a server-side environment without errors.
 */

// Mock the server environment
const originalWindow = global.window;
const originalLocalStorage = global.localStorage;

// Remove window and localStorage to simulate SSR
delete global.window;
delete global.localStorage;

console.log('🧪 Testing SSR safety...');

try {
  // This should not throw any errors now
  const { useAuthStore } = require('../lib/stores/authStore.production.ts');
  
  console.log('✅ Auth store imported successfully in SSR environment');
  
  // Try to get initial state
  const initialState = useAuthStore.getState();
  
  console.log('✅ Initial state retrieved:', {
    isAuthenticated: initialState.isAuthenticated,
    deviceId: initialState.deviceId, // Should be null in SSR
    user: initialState.user,
  });
  
  console.log('🎉 SSR test PASSED - No localStorage errors!');
  
} catch (error) {
  console.error('❌ SSR test FAILED:', error.message);
  process.exit(1);
} finally {
  // Restore original environment
  global.window = originalWindow;
  global.localStorage = originalLocalStorage;
}

console.log('✅ SSR verification complete');
