export const useBaseURL = () => {
    const config = useRuntimeConfig(); // Access Nuxt runtime config
    return config.public.NUXT_PUBLIC_API_URL; // Access public environment variables
};