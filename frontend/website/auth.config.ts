import { NextAuthConfig } from 'next-auth'
import Google from 'next-auth/providers/google'

export const authConfig = {
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      authorization: {
        params: {
          scope: "openid email profile",
          prompt: "select_account",
        },
      },
    })
  ],
  pages: {
    signIn: '/',
    error: '/',
  },
  callbacks: {
    async jwt({ token, account, user }) {
      if (account && user) {
        token.accessToken = account.access_token
        token.idToken = account.id_token  // Store Google ID token for backend auth
        token.user = user
      }
      return token
    },
    async session({ session, token }) {
      if (token.user) {
        session.user = token.user as any
      }
      // Pass tokens to session for backend authentication
      if (token.accessToken) {
        (session as any).accessToken = token.accessToken
      }
      if (token.idToken) {
        (session as any).idToken = token.idToken  // This is what backend needs
      }
      return session
    },
    async redirect({ url, baseUrl }) {
      // Ensure redirects work properly in development
      if (url.startsWith('/')) return `${baseUrl}${url}`
      if (new URL(url).origin === baseUrl) return url
      return baseUrl
    },
  },
  debug: process.env.NODE_ENV === 'development',
  secret: process.env.NEXTAUTH_SECRET,
} satisfies NextAuthConfig
