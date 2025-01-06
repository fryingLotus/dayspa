<script setup lang="ts">
import { reactive, watchEffect } from "vue";
import { changePassword, updateUser } from "~/service/user"; // Import your updateUser function

import { toast } from "vue-sonner";
// Fetch user data from the useAuth function
const { data, token } = useAuth();

// Reactive form to bind user data
const userForm = reactive({
  first_name: data?.value.data.first_name || "", // Use default empty string if data is not loaded
  last_name: data?.value.data.last_name || "", // Same for last_name
});

const passwordForm = reactive({
  email: data.value?.data.email,
  old_password: "",
  new_password: "",
});
// Watch for changes in user data and update the form
watchEffect(() => {
  if (data) {
    userForm.first_name = data.value.data.first_name;
    userForm.last_name = data.value.data.last_name;
  }
});

// Method to handle user update
const handleUpdate = async () => {
  try {
    // Call the updateUser function with the form data and token
    const updatedUser = await updateUser(
      { first_name: userForm.first_name, last_name: userForm.last_name },
      token.value,
    );
    toast.success("Succesfully updated user");
  } catch (error) {
    console.error("Error updating user:", error);
    toast.error("Failed to update user");
  }
};

const updatePassword = async () => {
  try {
    const res = await changePassword(
      {
        email: passwordForm.email,
        new_password: passwordForm.new_password,
        old_password: passwordForm.old_password,
      },
      token.value,
    );

      toast.success("Successfully changed user password!");
  } catch (error) {
    toast.error("Password don't match", error.message);
  }
};
</script>

<template>
  <div class="flex min-h-screen w-full flex-col">
    <main
      class="flex min-h-[calc(100vh_-_theme(spacing.16))] flex-1 flex-col gap-4 bg-muted/40 p-4 md:gap-8 md:p-10"
    >
      <div class="mx-auto grid w-full max-w-6xl gap-2">
        <h1 class="text-3xl font-semibold">Settings</h1>
      </div>
      <div
        class="mx-auto grid w-full max-w-6xl items-start gap-6 md:grid-cols-[180px_1fr] lg:grid-cols-[250px_1fr]"
      >
        <nav class="grid gap-4 text-sm text-muted-foreground">
          <a href="#" class="font-semibold text-primary"> General </a>
        </nav>
        <div class="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>User Name</CardTitle>
              <CardDescription>Used to identify your username</CardDescription>
            </CardHeader>
            <CardContent>
              <form class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <!-- First Name and Last Name in a 2-column layout -->
                <Input v-model="userForm.first_name" placeholder="First Name" />
                <Input v-model="userForm.last_name" placeholder="Last Name" />
              </form>
            </CardContent>
            <CardFooter class="border-t px-6 py-4">
              <!-- Bind the handleUpdate method to the Save button -->
              <Button @click="handleUpdate">Save</Button>
            </CardFooter>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Change Password</CardTitle>
              <CardDescription>
                You can change your password here
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input v-model="passwordForm.old_password" />

                <Input v-model="passwordForm.new_password" />
              </form>
            </CardContent>
            <CardFooter class="border-t px-6 py-4">
              <Button @click="updatePassword">Save</Button>
            </CardFooter>
          </Card>
        </div>
      </div>
    </main>
  </div>
</template>
