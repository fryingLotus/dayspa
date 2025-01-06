<script setup lang="ts">
import { Button } from "~/components/ui/button";
import { fetchServiceById } from "~/service/service";
import { useCartStore } from "~/stores/cart";
import { toast } from "vue-sonner";
const route = useRoute();
const { data: service, error } = await useLazyAsyncData("service", () =>
  fetchServiceById(route.params.id as string),
);
const cartStore = useCartStore();

if (error.value) {
  console.error("Error fetching service:", error.value);
}

// Function to check if the service is already in the cart
const isServiceInCart = (serviceId: number): boolean => {
  return cartStore.services.some((service) => service.id === serviceId);
};
const addToCart = (service: Service) => {
  if (!isServiceInCart(service.id)) {
    cartStore.addService(service);
    toast.success(`${service.service_name} has been added to cart`);
  } else {
    alert("You can only book one of each service.");
  }
};
console.log("service data", service.value);
</script>

<template>
  <section class="w-full py-12 md:py-24 lg:py-32">
    <div class="container px-4 md:px-6">
      <div class="grid gap-12 lg:grid-cols-2">
        <!-- Product Image -->
        <div>
          <img
            :src="service?.service_image_url || '/placeholder.svg'"
            alt="Product Image"
            width="500"
            height="600"
            class="mx-auto aspect-[5/6] overflow-hidden rounded-xl object-cover object-center sm:w-full"
          />
        </div>

        <!-- Product Details -->
        <div class="flex flex-col justify-start space-y-4">
          <h2 class="text-5xl font-bold tracking-tighter">
            {{ service?.service_name }}
          </h2>
          <p class="text-3xl font-semibold text-zinc-700 dark:text-zinc-300">
            {{ service?.price }} $
          </p>
          <p class="text-xl text-zinc-500 dark:text-zinc-400">
            {{ service?.description }}
          </p>

          <!-- Add to Cart Button -->
          <Button
            :disabled="!service || isServiceInCart(service.id)"
            @click="addToCart(service)"
            class="w-full md:w-auto"
          >
            Add to Cart
          </Button>
        </div>
      </div>

      <!-- Related Products (optional) -->
    </div>
  </section>
</template>
