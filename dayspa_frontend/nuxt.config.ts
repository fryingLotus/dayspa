// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: [
    "@nuxtjs/tailwindcss",
    "@vueuse/nuxt",
    "shadcn-nuxt",
    "@nuxtjs/color-mode",
    "@sidebase/nuxt-auth",
    "@pinia/nuxt",
    "pinia-plugin-persistedstate/nuxt",
    "@nuxt/icon",
    "nuxt-vue3-google-signin",
  ],
  compatibilityDate: "2024-11-01",
  googleSignIn: {
    clientId:
      "216506309638-8t8vo5j2mbtopsa4enkq8cm25tq5ija6.apps.googleusercontent.com",
  },
  devtools: {
    enabled: true,
    // Add these additional options
    timeline: {
      enabled: true,
    },
  },
  runtimeConfig: {
    public: {
      NUXT_PUBLIC_API_URL: process.env.NUXT_PUBLIC_API_URL, // This should correctly pull in the env variable
    },
  },
  shadcn: {
    prefix: "",
    componentDir: "./components/ui",
  },
  auth: {
    baseURL: process.env.NUXT_PUBLIC_API_URL,
    provider: {
      type: "local",
      endpoints: {
        signIn: { path: "api/auth/login/", method: "post" },
        signOut: { path: "api/auth/logout/", method: "post" }, // You might need to implement this
        signUp: { path: "api/auth/register/", method: "post" },
        getSession: { path: "api/auth/me/", method: "get" },
      },
      session: {
        dataType: {
          id: "string | number",
          first_name: "string",
          last_name: "string",
          email: "string",
        },
      },
      pages: {
        login: "/login",
      },
      token: {
        signInResponseTokenPointer: "/data/access_token",
        type: "Bearer",
        headerName: "Authorization",
        maxAgeInSeconds: 60 * 60 * 2,
      },
      // Add a transform to extract user data
      // transform: {
      //     user: (response) => response.data?.user || null
      // }
    },
    // enableSessionRefreshPeriodically: 5000,
    // enableSessionRefreshOnWindowFocus: true,
    sessionRefresh: {
      enableOnWindowFocus: true,
    },
    globalAppMiddleware: false,
  },
});
