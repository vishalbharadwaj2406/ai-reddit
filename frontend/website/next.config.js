/** @type {import('next').NextConfig} */
const nextConfig = {
  // BFF Pattern: Build for server rendering with FastAPI backend
  images: {
    unoptimized: true, // Simplified for BFF pattern
    remotePatterns: [
      // Google CDN for profile pictures
      {
        protocol: 'https',
        hostname: 'lh3.googleusercontent.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'lh4.googleusercontent.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'lh5.googleusercontent.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'lh6.googleusercontent.com',
        port: '',
        pathname: '/**',
      },
      // Additional Google domains for profile pictures
      {
        protocol: 'https',
        hostname: 'googleusercontent.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'googleapis.com',
        port: '',
        pathname: '/**',
      },
    ],
    // Image optimization settings for external images
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    formats: ['image/webp', 'image/avif'],
  },
  
  // Clean URLs for FastAPI serving
  trailingSlash: false,
  
  // Windows-specific optimizations
  experimental: {
    caseSensitiveRoutes: false,
  },
  
  // Webpack configuration for Windows compatibility
  webpack: (config, { isServer }) => {
    // Fix for Windows symlink issues
    config.watchOptions = {
      ...config.watchOptions,
      ignored: /node_modules/,
      poll: process.platform === 'win32' ? 1000 : false,
    };
    
    return config;
  },
}

module.exports = nextConfig
