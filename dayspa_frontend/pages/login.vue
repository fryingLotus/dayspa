<script setup lang="ts">
import { walkUpBindingElementsAndPatterns } from "typescript";
import { ref } from "vue";
import {
  GoogleSignInButton,
  type CredentialResponse,
} from "vue3-google-signin";

// Form data
const formData = reactive({
  email: "",
  password: "",
});
const router = useRouter();

const { setToken, token } = useAuthState();
const { getSession, signIn } = useAuth();
// Google sign-in success callback
const handleLoginSuccess = async (response: CredentialResponse) => {
  const { credential } = response; // Google access token
  console.log("Access Token", credential);

  try {
    // Send the access token to the backend using $fetch
    const res = await $fetch(`http://127.0.0.1:8001/api/google/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ token: credential }), // Sending the token to the backend
    });

    if (res.success) {
      // Successfully signed in, save tokens
      console.log("res", res);
      const accessToken = res.data.access_token;

      // Use Sidebase's `setToken` to store the token
      setToken(accessToken);
      await getSession();
      console.log("token", token.value);

      console.log("Logged in successfully:", res);
      router.push("/");
    } else {
      console.error("Login failed:", res.message);
    }
  } catch (error) {
    console.error("Error during backend request:", error);
  }
};
// Google sign-in error callback
const handleLoginError = () => {
  console.error("Login failed");
};

// Login form submission
const login = async (e: Event) => {
  try {
    console.log("formData", formData);
    e.preventDefault();
    let res = await signIn(
      { ...formData },
      { callbackUrl: "/" }, // Where the user will be redirected after a successiful login
    );

    console.log("res", res);
  } catch (error) {
    console.log("error", error);
  }
};
</script>

<template>
  <div class="flex items-center justify-center min-h-screen">
    <Card class="mx-auto max-w-sm">
      <CardHeader>
        <CardTitle class="text-2xl">Login</CardTitle>
        <CardDescription>
          Enter your email below to login to your account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit.prevent="login" class="grid gap-4">
          <div class="grid gap-2">
            <Label for="email">Email</Label>
            <Input
              id="email"
              type="email"
              v-model="formData.email"
              placeholder="m@example.com"
              required
            />
          </div>
          <div class="grid gap-2">
            <div class="flex items-center">
              <Label for="password">Password</Label>
              <NuxtLink
                to="reset_password_request"
                class="ml-auto inline-block text-sm underline"
              >
                Forgot your password?
              </NuxtLink>
            </div>
            <Input
              id="password"
              type="password"
              v-model="formData.password"
              required
            />
          </div>
          <Button type="submit" class="w-full">Login</Button>

          <!-- Google Sign-In Button -->
          <GoogleSignInButton
            @success="handleLoginSuccess"
            @error="handleLoginError"
          />
        </form>
        <div class="mt-4 text-center text-sm">
          Don't have an account?
          <NuxtLink to="register">Sign Up</NuxtLink>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
