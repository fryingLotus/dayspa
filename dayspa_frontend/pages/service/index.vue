<script setup lang="ts">
import { ref, computed } from "vue";
import { useCartStore } from "~/stores/cart";
import { fetchServices } from "~/service/service";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import {
  Pagination,
  PaginationEllipsis,
  PaginationFirst,
  PaginationLast,
  PaginationList,
  PaginationListItem,
  PaginationNext,
  PaginationPrev,
} from "~/components/ui/pagination";
import { toast } from "vue-sonner";
const services = ref<Service[]>([]);
const cartStore = useCartStore();

// Pagination state
const currentPage = ref(1);
const pageSize = ref(10);
const totalServices = ref(0);

// Fetch services data
const loadServices = async (page: number) => {
  try {
    const { services: fetchedServices, count } = await fetchServices(
      page,
      pageSize.value,
    );
    services.value = fetchedServices;
    totalServices.value = count;
    currentPage.value = page;
  } catch (error) {
    console.error(error);
  }
};

loadServices(1);

// Check if a service is already in the cart
const isServiceInCart = (serviceId: number): boolean => {
  return cartStore.services.some((service) => service.id === serviceId);
};

// Add service to cart
const addToCart = (service: Service) => {
  if (!isServiceInCart(service.id)) {
    cartStore.addService(service);
    toast.success(`${service.service_name} has been added to cart`);
  } else {
    alert("You can only book one of each service.");
  }
};
</script>

<template>
  <div class="max-w-6xl mx-auto p-4">
    <h1 class="text-2xl font-semibold mb-4">Our Services</h1>

    <!-- Services Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
      <Card v-for="service in services" :key="service.id" class="w-full">
        <CardHeader>
          <CardTitle>{{ service.service_name }}</CardTitle>
        </CardHeader>
        <CardContent>
          <img
            :src="service.service_image_url || '/placeholder.jpg'"
            alt="Service Image"
            class="w-full h-48 object-cover rounded-md mb-4"
          />
          <div class="space-y-2">
            <p class="text-sm text-muted-foreground">
              Price: ${{ service.price }}
            </p>
            <p class="text-sm text-muted-foreground">
              Duration: {{ service.duration }} mins
            </p>
          </div>
        </CardContent>
        <CardFooter class="flex justify-between">
          <Button
            :disabled="isServiceInCart(service.id)"
            @click="addToCart(service)"
            class="w-full md:w-auto"
          >
            Add to Cart
          </Button>
          <!-- View Service Detail Button -->
          <NuxtLink :to="`/service/${service.id}`">
            <Button variant="outline" class="w-full md:w-auto">
              View Service Detail
            </Button>
          </NuxtLink>
        </CardFooter>
      </Card>
    </div>

    <!-- Shadcn Pagination -->
    <Pagination
      v-slot="{ page }"
      :total="totalServices"
      :sibling-count="1"
      show-edges
      :default-page="1"
    >
      <PaginationList
        v-slot="{ items }"
        class="flex items-center gap-1 mt-8 justify-center"
      >
        <PaginationFirst @click="loadServices(1)" />
        <PaginationPrev @click="loadServices(page - 1)" />

        <template v-for="(item, index) in items" :key="index">
          <PaginationListItem
            v-if="item.type === 'page'"
            :value="item.value"
            as-child
          >
            <Button
              class="w-10 h-10 p-0"
              :variant="item.value === page ? 'default' : 'outline'"
              @click="loadServices(item.value)"
            >
              {{ item.value }}
            </Button>
          </PaginationListItem>
          <PaginationEllipsis v-else :index="index" />
        </template>

        <PaginationNext @click="loadServices(page + 1)" />
        <PaginationLast
          @click="loadServices(Math.ceil(totalServices / pageSize))"
        />
      </PaginationList>
    </Pagination>
  </div>
</template>
