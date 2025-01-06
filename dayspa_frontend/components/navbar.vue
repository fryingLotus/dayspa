<script setup lang="ts">
import { useDark, useToggle } from "@vueuse/core";
import { ref, computed } from "vue";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useCartStore } from "~/stores/cart";
// Importing the ShoppingCart icon from Lucide Vue Next
import { ShoppingCart } from "lucide-vue-next";

const { signOut, token } = useAuth();
const isDark = useDark();
const toggleDark = useToggle(isDark);
const isOpen = ref(false);
const { status } = useAuth();
const cartStore = useCartStore();
const cartItemCount = computed(() => cartStore.totalItems);

const items = ref([
  {
    label: "Home",
    icon: "ph:house-bold",
    to: "/",
  },
  {
    label: "About",
    icon: "ph:info-bold",
    to: "/about",
  },
  {
    label: "Service",
    icon: "ph:info-bold",
    to: "/service/",
  },
  {
    label: "",
    icon: ShoppingCart, // Use the ShoppingCart icon here
    to: "/cart",
  },
]);

const authItems = computed(() => {
  return status.value !== "authenticated"
    ? [
        {
          label: "Sign In",
          icon: "ph:sign-in-bold",
          to: "/login",
        },
        {
          label: "Sign Up",
          icon: "ph:sign-out-bold",
          to: "/register",
        },
      ]
    : [];
});

async function _signOut() {
  try {
    const refreshToken = token?.value;

    if (!refreshToken) {
      console.error("Refresh token is missing.");
      return;
    }

    await signOut({
      callbackUrl: "/login",
      redirect: true,
      external: false,
    });
    console.log("Sign out successful.");
  } catch (error: any) {
    console.error("Error during sign out:", error);
  }
}
</script>

<template>
  <header
    class="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
  >
    <div class="container flex h-16 items-center">
      <!-- Logo -->
      <NuxtLink to="/" class="mr-6 flex items-center space-x-2">
        <Logo />
      </NuxtLink>

      <!-- Desktop Navigation -->
      <nav class="hidden md:flex items-center space-x-6 text-sm font-medium">
        <NuxtLink
          v-for="item in items"
          :key="item.to"
          :to="item.to"
          class="transition-colors hover:text-foreground/80 text-foreground/60 flex items-center text-lg relative"
          :class="{ 'text-foreground': $route.path === item.to }"
        >
          <!-- Use ShoppingCart icon here for cart -->
          <component :is="item.icon" class="mr-2 h-4 w-4" />
          <!-- Use icon component -->
          {{ item.label }}

          <!-- Cart Item Count Badge for Desktop -->
          <span
            v-if="item.to === '/cart' && cartItemCount > 0"
            class="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center"
          >
            {{ cartItemCount }}
          </span>
        </NuxtLink>
      </nav>

      <!-- Right-aligned section -->
      <div class="ml-auto flex items-center space-x-4">
        <!-- Sign In / Sign Up -->
        <div
          v-if="status !== 'authenticated'"
          class="flex items-center space-x-6 text-sm font-medium"
        >
          <NuxtLink
            v-for="item in authItems"
            :key="item.to"
            :to="item.to"
            class="transition-colors hover:text-foreground/80 text-foreground/60 flex items-center text-lg"
            :class="{ 'text-foreground': $route.path === item.to }"
          >
            <Icon :name="item.icon" class="mr-2 h-4 w-4" />
            {{ item.label }}
          </NuxtLink>
        </div>

        <!-- Dark Mode Toggle -->
        <button class="p-2 rounded-md hover:bg-accent" @click="toggleDark()">
          <Icon
            :name="isDark ? 'uil:sun' : 'ph:moon-bold'"
            class="h-5 w-5 flex items-center"
          />
        </button>

        <!-- Authenticated Dropdown Menu -->
        <div v-if="status === 'authenticated'">
          <DropdownMenu>
            <DropdownMenuTrigger>Open</DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuLabel>My Account</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                ><NuxtLink to="/setting/">Settings</NuxtLink></DropdownMenuItem
              >
              <DropdownMenuItem @click="_signOut">Logout</DropdownMenuItem>
              <DropdownMenuItem
                ><NuxtLink to="/appointment/"
                  >Appointments</NuxtLink
                ></DropdownMenuItem
              >
              <DropdownMenuItem>Subscription</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <!-- Mobile menu button -->
        <button
          class="p-2 rounded-md hover:bg-accent md:hidden"
          @click="isOpen = !isOpen"
        >
          <Icon :name="isOpen ? 'ph:x-bold' : 'ph:list-bold'" class="h-5 w-5" />
        </button>
      </div>
    </div>

    <!-- Mobile menu -->
    <div v-show="isOpen" class="md:hidden">
      <nav class="px-2 pt-2 pb-3 space-y-1">
        <NuxtLink
          v-for="item in items"
          :key="item.to"
          :to="item.to"
          class="flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors hover:bg-accent relative"
          :class="{ 'bg-accent': $route.path === item.to }"
          @click="isOpen = false"
        >
          <component :is="item.icon" class="mr-2 h-4 w-4" />
          <!-- Use icon component -->
          {{ item.label }}

          <!-- Cart Item Count Badge for Mobile -->
          <span
            v-if="item.to === '/cart' && cartItemCount > 0"
            class="absolute top-1 right-1 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center"
          >
            {{ cartItemCount }}
          </span>
        </NuxtLink>

        <NuxtLink
          v-for="item in authItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors hover:bg-accent"
          :class="{ 'bg-accent': $route.path === item.to }"
          @click="isOpen = false"
        >
          <Icon :name="item.icon" class="mr-2 h-4 w-4" />
          {{ item.label }}
        </NuxtLink>
      </nav>
    </div>
  </header>
</template>
