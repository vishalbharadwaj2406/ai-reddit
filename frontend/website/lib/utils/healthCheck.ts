import { apiClient, endpoints } from '../config/api.production';

export interface HealthStatus {
  backend: 'healthy' | 'unhealthy' | 'unknown';
  database: 'healthy' | 'unhealthy' | 'unknown';
  message: string;
}

export class HealthChecker {
  
  /**
   * Check backend API health
   */
  async checkBackendHealth(): Promise<HealthStatus> {
    try {
      // Test basic backend health
      const response = await apiClient.get<{ status: string }>(endpoints.health.system);
      
      if (response.success && response.data?.status === 'healthy') {
        return {
          backend: 'healthy',
          database: 'unknown',
          message: 'Backend is running normally'
        };
      } else {
        return {
          backend: 'unhealthy',
          database: 'unknown',
          message: 'Backend responded but status is unhealthy'
        };
      }
      
    } catch (error) {
      console.error('Health check failed:', error);
      
      return {
        backend: 'unhealthy',
        database: 'unknown',
        message: `Backend connection failed: ${error}`
      };
    }
  }

  /**
   * Check database health
   */
  async checkDatabaseHealth(): Promise<HealthStatus> {
    try {
      const response = await apiClient.get<{ status: string; migrated: boolean }>(
        endpoints.health.database
      );
      
      if (response.success && response.data?.status === 'healthy') {
        return {
          backend: 'healthy',
          database: response.data.migrated ? 'healthy' : 'unhealthy',
          message: response.data.migrated 
            ? 'Database is connected and migrated' 
            : 'Database connected but not properly migrated'
        };
      } else {
        return {
          backend: 'healthy',
          database: 'unhealthy',
          message: 'Database health check failed'
        };
      }
      
    } catch (error) {
      console.error('Database health check failed:', error);
      
      return {
        backend: 'unknown',
        database: 'unhealthy', 
        message: `Database health check failed: ${error}`
      };
    }
  }

  /**
   * Comprehensive system health check
   */
  async checkSystemHealth(): Promise<HealthStatus> {
    try {
      // Check backend first
      const backendHealth = await this.checkBackendHealth();
      
      if (backendHealth.backend !== 'healthy') {
        return backendHealth;
      }
      
      // If backend is healthy, check database
      const dbHealth = await this.checkDatabaseHealth();
      
      return {
        backend: 'healthy',
        database: dbHealth.database,
        message: dbHealth.database === 'healthy' 
          ? 'All systems operational'
          : dbHealth.message
      };
      
    } catch (error) {
      return {
        backend: 'unknown',
        database: 'unknown',
        message: `System health check failed: ${error}`
      };
    }
  }
}

// Export singleton instance
export const healthChecker = new HealthChecker(); 