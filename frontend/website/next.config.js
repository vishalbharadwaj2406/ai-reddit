/** @type {import('next').NextConfig} */
const nextConfig = {
  // Standard Next.js configuration for cross-origin backend
  images: {
    unoptimized: true,
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
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    formats: ['image/webp', 'image/avif'],
  },
  
  trailingSlash: false,
  
  // Standard webpack configuration
  webpack: (config, { isServer }) => {
    // Standard optimizations only
    config.watchOptions = {
      ...config.watchOptions,
      ignored: /node_modules/,
      poll: process.platform === 'win32' ? 1000 : false,
    };
    
    return config;
  },
}

module.exports = nextConfig
