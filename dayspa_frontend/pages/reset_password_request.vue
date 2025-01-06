<template>
  <div class="flex items-center justify-center min-h-screen">
    <Card class="w-full max-w-md">
      <CardHeader>
        <CardTitle>Forgot Password</CardTitle>
        <CardDescription>
          Enter your email address and we'll send you a link to reset your
          password.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit.prevent="handleSubmit">
          <div class="grid w-full items-center gap-4">
            <div class="flex flex-col space-y-1.5">
              <Input
                v-model="email"
                id="email"
                placeholder="Enter your email"
                type="email"
                autocomplete="email"
                required
              />
            </div>
          </div>
        </form>
      </CardContent>
      <CardFooter class="flex flex-col space-y-4">
        <Button class="w-full" @click="handleSubmit" :disabled="loading">
          <span v-if="!loading">Send Reset Link</span>
          <span v-else>Sending...</span>
        </Button>
        <NuxtLink
          to="/login"
          class="flex items-center text-sm text-muted-foreground hover:text-primary"
        >
          <ArrowLeft class="mr-2 h-4 w-4" />
          Back to Login
        </NuxtLink>
      </CardFooter>
    </Card>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { requestPasswordReset } from "~/service/user"; // Import your API function

import { toast } from "vue-sonner";
import { ArrowLeft } from "lucide-vue-next";

// Data
const email = ref("");
const loading = ref(false);
const router = useRouter();

// Submit handler
const handleSubmit = async () => {
  if (!email.value) {
    alert("Please enter your email address.");
    return;
  }

  try {
    loading.value = true;
    const response = await requestPasswordReset(email.value); // Call the API
    email.value = ""; // Clear the input
    toast.success("Password reset link sent successfully.");
  } catch (error) {
    console.error("Error sending password reset link:", error);
    alert("An error occurred. Please try again later.");
    toast.error(error || "An error occured. Please try again later");
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* Add custom styles if needed */
</style>
