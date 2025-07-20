import { NextAuthConfig } from 'next-auth'
import Google from 'next-auth/providers/google'

export const authConfig = {
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
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
        token.user = user
      }
      return token
    },
    async session({ session, token }) {
      if (token.user) {
        session.user = token.user as any
      }
      return session
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
} satisfies NextAuthConfig
