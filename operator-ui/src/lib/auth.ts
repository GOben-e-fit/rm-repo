import NextAuth from 'next-auth';
import Keycloak from 'next-auth/providers/keycloak';

/**
 * Auth.js v5 Konfiguration mit Keycloak-OIDC.
 * Phase 1 stub — Realm/Client müssen im Keycloak (`keycloak.ben-e-fit.ai`) angelegt werden.
 */
export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Keycloak({
      clientId: process.env.AUTH_KEYCLOAK_ID ?? '',
      clientSecret: process.env.AUTH_KEYCLOAK_SECRET ?? '',
      issuer: process.env.AUTH_KEYCLOAK_ISSUER ?? '',
    }),
  ],
  callbacks: {
    async session({ session, token }) {
      // TODO Phase 1: tenant_id + roles + groups aus Keycloak-Claims in Session-Objekt heben
      session.user.id = token.sub ?? '';
      return session;
    },
    async jwt({ token, profile }) {
      // TODO Phase 1: groups + tenant claim mappen
      if (profile) {
        token.email = profile.email;
      }
      return token;
    },
  },
  pages: {
    signIn: '/login',
  },
});
