/**
 * Debug utilities for troubleshooting API calls and blog publishing
 */

export const debugPost = {
  /**
   * Test the post creation payload
   */
  validatePayload: (payload: any) => {
    console.group('🔍 Validating Post Payload');
    console.log('Payload:', payload);
    
    const required = ['title', 'content'];
    const optional = ['messageId', 'tags', 'isConversationVisible'];
    
    const missing = required.filter(field => !payload[field]);
    if (missing.length > 0) {
      console.error('❌ Missing required fields:', missing);
      return false;
    }
    
    console.log('✅ All required fields present');
    
    // Check payload structure
    const expectedFields = [...required, ...optional];
    const unexpectedFields = Object.keys(payload).filter(field => !expectedFields.includes(field));
    
    if (unexpectedFields.length > 0) {
      console.warn('⚠️ Unexpected fields (might cause issues):', unexpectedFields);
    }
    
    console.groupEnd();
    return true;
  },

  /**
   * Log API response details
   */
  logResponse: (response: any, endpoint: string) => {
    console.group('📡 API Response Debug');
    console.log('Endpoint:', endpoint);
    console.log('Response type:', typeof response);
    console.log('Response:', response);
    
    if (response && typeof response === 'object') {
      if ('success' in response) {
        console.log('✅ Wrapped response detected');
        console.log('Success:', response.success);
        console.log('Data:', response.data);
        console.log('Message:', response.message);
        console.log('Error Code:', response.errorCode);
      } else {
        console.log('📦 Direct response (not wrapped)');
      }
    }
    
    console.groupEnd();
  },

  /**
   * Log error details for debugging
   */
  logError: (error: any, context: string) => {
    console.group('❌ Error Debug');
    console.log('Context:', context);
    console.log('Error type:', typeof error);
    console.log('Error:', error);
    
    if (error && typeof error === 'object') {
      console.log('Error keys:', Object.keys(error));
      
      // Check for common error patterns
      if ('response' in error) {
        console.log('Response Error:', error.response);
        if (error.response && error.response.data) {
          console.log('Response Data:', error.response.data);
        }
      }
      
      if ('detail' in error) {
        console.log('Detail:', error.detail);
      }
      
      if ('message' in error) {
        console.log('Message:', error.message);
      }
      
      if ('status' in error) {
        console.log('Status:', error.status);
      }
    }
    
    console.groupEnd();
  }
};

/**
 * Network request debugger
 */
export const debugNetwork = {
  /**
   * Log outgoing request details
   */
  logRequest: (method: string, url: string, data?: any) => {
    console.group(`🌐 ${method} Request`);
    console.log('URL:', url);
    if (data) {
      console.log('Payload:', data);
      console.log('Payload JSON:', JSON.stringify(data, null, 2));
    }
    console.log('Timestamp:', new Date().toISOString());
    console.groupEnd();
  }
};
