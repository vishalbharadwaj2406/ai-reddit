// Beautiful login modal with Google OAuth and enhanced UI
'use client';

import { useState } from 'react';
import { signIn, useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { MessageCircle, Chrome, Sparkles, Users, Zap, Globe } from 'lucide-react';

export default function LoginModal() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { status } = useSession();
  const router = useRouter();

  // Redirect if already authenticated
  if (status === 'authenticated') {
    router.push('/conversations');
    return null;
  }

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await signIn('google', {
        callbackUrl: '/conversations',
        redirect: false,
      });
      
      if (result?.error) {
        setError('Google login failed. Please try again.');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // For demo purposes, we'll simulate a login
      // In a real app, this would call your demo login endpoint
      await new Promise(resolve => setTimeout(resolve, 1000));
      router.push('/conversations');
    } catch (err) {
      setError('Demo login failed. Please try again.');
      console.error('Demo login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 pointer-events-none">
        <div 
          className="absolute inset-0 opacity-40"
          style={{
            background: `
              radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.15) 0%, transparent 50%),
              radial-gradient(circle at 80% 20%, rgba(168, 85, 247, 0.15) 0%, transparent 50%),
              radial-gradient(circle at 40% 40%, rgba(236, 72, 153, 0.1) 0%, transparent 50%)
            `,
            animation: 'royalFlow 25s ease-in-out infinite'
          }}
        />
        
        {/* Floating Particles */}
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-2 h-2 bg-white opacity-20 rounded-full animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${3 + Math.random() * 4}s`
            }}
          />
        ))}
      </div>

      {/* Main Login Card */}
      <div className="relative z-10 w-full max-w-lg px-6">
        <div className="glass-card rounded-3xl p-8 shadow-2xl border border-white/20">
          {/* Header */}
          <div className="text-center mb-10">
            <div className="w-20 h-20 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-purple-500/25">
              <MessageCircle className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-white mb-3 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              AI Social
            </h1>
            <p className="text-gray-300 text-lg">Connect through intelligent conversations</p>
            <div className="flex items-center justify-center gap-2 mt-3">
              <Sparkles className="w-4 h-4 text-yellow-400" />
              <span className="text-sm text-gray-400">Powered by advanced AI</span>
              <Sparkles className="w-4 h-4 text-yellow-400" />
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-500/20 border border-red-500/40 rounded-xl animate-fadeInUp">
              <p className="text-red-300 text-sm text-center">{error}</p>
            </div>
          )}

          {/* Google Login Button */}
          <button
            onClick={handleGoogleLogin}
            disabled={isLoading}
            className={`w-full py-4 px-6 rounded-xl font-semibold text-white transition-all duration-300 mb-4 ${
              isLoading
                ? 'bg-gray-600 cursor-not-allowed'
                : 'bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 hover:scale-105 active:scale-95 shadow-lg hover:shadow-red-500/25'
            }`}
          >
            {isLoading ? (
              <div className="flex items-center justify-center gap-3">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Connecting to Google...</span>
              </div>
            ) : (
              <div className="flex items-center justify-center gap-3">
                <Chrome className="w-5 h-5" />
                <span>Continue with Google</span>
              </div>
            )}
          </button>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-600"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-3 bg-transparent text-gray-400">or</span>
            </div>
          </div>

          {/* Demo Login Button */}
          <button
            onClick={handleDemoLogin}
            disabled={isLoading}
            className={`w-full py-4 px-6 rounded-xl font-semibold text-white transition-all duration-300 ${
              isLoading
                ? 'bg-gray-600 cursor-not-allowed'
                : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 hover:scale-105 active:scale-95 shadow-lg hover:shadow-blue-500/25'
            }`}
          >
            {isLoading ? (
              <div className="flex items-center justify-center gap-3">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Loading demo...</span>
              </div>
            ) : (
              <div className="flex items-center justify-center gap-3">
                <Zap className="w-5 h-5" />
                <span>Try Demo Experience</span>
              </div>
            )}
          </button>

          {/* Features Showcase */}
          <div className="mt-8 space-y-4">
            <h3 className="text-white font-semibold text-center mb-6">
              <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                What awaits you
              </span>
            </h3>
            
            <div className="grid grid-cols-1 gap-4">
              {[
                { icon: MessageCircle, text: 'AI-powered conversations that adapt to your interests', color: 'from-blue-400 to-cyan-400' },
                { icon: Users, text: 'Connect with like-minded individuals worldwide', color: 'from-purple-400 to-pink-400' },
                { icon: Globe, text: 'Share insights and transform chats into posts', color: 'from-green-400 to-blue-400' }
              ].map((feature, index) => (
                <div key={index} className="flex items-center gap-4 p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-all duration-200">
                  <div className={`w-10 h-10 rounded-lg bg-gradient-to-r ${feature.color} flex items-center justify-center flex-shrink-0`}>
                    <feature.icon className="w-5 h-5 text-white" />
                  </div>
                  <p className="text-gray-300 text-sm leading-relaxed">{feature.text}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Privacy Notice */}
          <div className="mt-8 text-center">
            <p className="text-gray-500 text-xs leading-relaxed">
              By continuing, you agree to our terms of service and privacy policy.
              <br />
              Your conversations are private and secure.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-6">
          <p className="text-gray-500 text-xs">
            Built with Next.js, NextAuth, and ❤️
          </p>
        </div>
      </div>
    </div>
  );
}
