<script setup lang="ts">
import { toTypedSchema } from "@vee-validate/zod";
import * as z from "zod";
import { useForm } from "vee-validate";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";

const { signUp } = useAuth();

// Zod validation schema
const signUpSchema = z
  .object({
    first_name: z.string().min(1, { message: "First name is required" }),
    last_name: z.string().min(1, { message: "Last name is required" }),
    email: z.string().email({ message: "Invalid email address" }),
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
    password2: z.string(),
  })
  .refine((data) => data.password === data.password2, {
    message: "Passwords do not match",
    path: ["password2"],
  });

// Convert Zod schema to Vee-Validate schema
const validationSchema = toTypedSchema(signUpSchema);

// Initialize form with Vee-Validate
const { handleSubmit, errors, defineField } = useForm({
  validationSchema: validationSchema,
});

// Define form fields
const [first_name, first_nameProps] = defineField("first_name");
const [last_name, last_nameProps] = defineField("last_name");
const [email, emailProps] = defineField("email");
const [password, passwordProps] = defineField("password");
const [password2, password2Props] = defineField("password2");

// Submit handler
const onSubmit = handleSubmit(async (values) => {
  try {
    // Include password2 in the submission
    let res = await signUp({ ...values }, { callbackUrl: "/" });
    console.log("Signup Result:", res);
  } catch (error) {
    console.error("Signup Error:", error);
  }
});
</script>

<template>
  <div class="flex items-center justify-center min-h-screen">
    <Card class="mx-auto max-w-sm">
      <CardHeader>
        <CardTitle class="text-xl"> Sign Up </CardTitle>
        <CardDescription>
          Enter your information to create an account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit="onSubmit" class="grid gap-4">
          <div class="grid grid-cols-2 gap-4">
            <FormField name="first_name">
              <FormItem>
                <FormLabel>First name</FormLabel>
                <FormControl>
                  <Input
                    v-model="first_name"
                    v-bind="first_nameProps"
                    placeholder="Max"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            </FormField>

            <FormField name="last_name">
              <FormItem>
                <FormLabel>Last name</FormLabel>
                <FormControl>
                  <Input
                    v-model="last_name"
                    v-bind="last_nameProps"
                    placeholder="Robinson"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            </FormField>
          </div>

          <FormField name="email">
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input
                  type="email"
                  v-model="email"
                  v-bind="emailProps"
                  placeholder="m@example.com"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          </FormField>

          <div class="grid gap-4 sm:grid-cols-2">
            <FormField name="password">
              <FormItem>
                <FormLabel>Password</FormLabel>
                <FormControl>
                  <Input
                    type="password"
                    v-model="password"
                    v-bind="passwordProps"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            </FormField>

            <FormField name="password2">
              <FormItem>
                <FormLabel>Confirm Password</FormLabel>
                <FormControl>
                  <Input
                    type="password"
                    v-model="password2"
                    v-bind="password2Props"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            </FormField>
          </div>

          <Button type="submit" class="w-full"> Create an account </Button>
          <Button variant="outline" class="w-full">
            Sign up with GitHub
          </Button>
          <div class="mt-4 text-center text-sm">
            Already have an account?
            <NuxtLink to="/login" class="underline"> Sign In </NuxtLink>
          </div>
        </form>
      </CardContent>
    </Card>
  </div>
</template>
