<script setup lang="ts">
import { toTypedSchema } from "@vee-validate/zod";
import * as z from "zod";
import { useForm } from "vee-validate";
import { resetPassword } from "~/service/user";
import { useRoute, useRouter } from "vue-router";

// Zod validation schema for password change
const passwordChangeSchema = z
  .object({
    password: z
      .string()
      .min(8, { message: "Password must be at least 8 characters" })
      .regex(/[A-Z]/, {
        message: "Password must contain at least one uppercase letter",
      })
      .regex(/[a-z]/, {
        message: "Password must contain at least one lowercase letter",
      })
      .regex(/[0-9]/, { message: "Password must contain at least one number" }),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

// Convert Zod schema to Vee-Validate schema
const validationSchema = toTypedSchema(passwordChangeSchema);

// Initialize form with Vee-Validate
const { handleSubmit, errors, defineField } = useForm({
  validationSchema,
});

// Define form fields
const [password, passwordProps] = defineField("password");
const [confirmPassword, confirmPasswordProps] = defineField("confirmPassword");

// Get the token from the route parameters
const route = useRoute();
const router = useRouter();
const token = route.params.token as string; // Access token from route params

// Submit handler
const onSubmit = handleSubmit(async (values) => {
  try {
    if (!token) {
      console.error("Token is missing");
      throw new Error("Reset token is required.");
    }

    // Call the resetPassword API
    const response = await resetPassword(token, values.password);

    if (response) {
      console.log("Password reset successfully:", response);
      alert("Your password has been reset successfully.");
      router.push("/login"); // Redirect to login page after successful reset
    }
  } catch (error) {
    console.error("Error resetting password:", error);
    alert("Failed to reset password. Please try again.");
  }
});
</script>

<template>
  <div class="flex items-center justify-center min-h-screen">
    <Card class="mx-auto max-w-sm">
      <CardHeader>
        <CardTitle class="text-xl">Change Password</CardTitle>
        <CardDescription>Enter your new password below.</CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit="onSubmit" class="grid gap-4">
          <FormField name="password">
            <FormItem>
              <FormLabel>New Password</FormLabel>
              <FormControl>
                <Input
                  type="password"
                  v-model="password"
                  v-bind="passwordProps"
                  placeholder="Enter new password"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <FormField name="confirmPassword">
            <FormItem>
              <FormLabel>Confirm Password</FormLabel>
              <FormControl>
                <Input
                  type="password"
                  v-model="confirmPassword"
                  v-bind="confirmPasswordProps"
                  placeholder="Confirm new password"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <Button type="submit" class="w-full">Change Password</Button>
        </form>
      </CardContent>
    </Card>
  </div>
</template>
