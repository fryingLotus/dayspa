<script setup lang="ts">
import { ref } from "vue";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
const reviews = ref([
  {
    name: "Sophia Carter",
    image: "https://randomuser.me/api/portraits/women/75.jpg",
    rating: 5,
    comment:
      "The spa services are exceptional! Booking appointments has never been this easy. Highly recommend it!",
  },
  {
    name: "Liam Johnson",
    image: "https://randomuser.me/api/portraits/men/45.jpg",
    rating: 4,
    comment:
      "A very user-friendly app. The design is sleek, and the features are helpful. Would love to see more services added.",
  },
  {
    name: "Emily Davis",
    image: "https://randomuser.me/api/portraits/women/55.jpg",
    rating: 5,
    comment:
      "Absolutely wonderful! The app makes managing my spa appointments a breeze. A must-have for spa-goers.",
  },
  {
    name: "James Brown",
    image: "https://randomuser.me/api/portraits/men/35.jpg",
    rating: 3,
    comment:
      "Good app overall, but some features could be improved for a smoother experience.",
  },
  {
    name: "Olivia Wilson",
    image: "https://randomuser.me/api/portraits/women/65.jpg",
    rating: 5,
    comment:
      "Love it! The app exceeded all my expectations. Perfect for organizing spa visits.",
  },
  {
    name: "Noah Martinez",
    image: "https://randomuser.me/api/portraits/men/85.jpg",
    rating: 4,
    comment:
      "Great potential. It’s already good, but I’m excited for the upcoming features!",
  },
]);
</script>

<template>
  <div class="min-h-screen bg-background">
    <!-- Hero Section -->
    <section
      class="relative overflow-hidden py-20 sm:py-32 bg-background border-b"
    >
      <div class="container px-4 md:px-6">
        <div class="flex flex-col items-center space-y-4 text-center">
          <div class="space-y-2">
            <h1
              class="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl"
            >
              Relax, Refresh, and Rejuvenate
            </h1>
            <p class="mx-auto max-w-[700px]">
              Discover effortless spa booking and management with our innovative
              app. Experience relaxation redefined.
            </p>
          </div>
          <div class="space-x-4">
            <NuxtLink to="service/">
              <Button size="lg">Book Now</Button>
            </NuxtLink>
            <Button size="lg" variant="outline">Explore Features</Button>
          </div>
        </div>
      </div>
    </section>

    <!-- Reviews Section -->
    <section class="py-20 sm:py-32">
      <div class="container px-4 md:px-6">
        <div
          class="flex flex-col items-center justify-center space-y-4 text-center"
        >
          <h2
            class="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl"
          >
            What Our Clients Are Saying
          </h2>
          <p class="max-w-[900px]">
            See why our users love the ease and convenience of managing their
            spa visits with our app.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-12">
          <Card
            v-for="review in reviews"
            :key="review.name"
            class="overflow-hidden"
          >
            <CardContent class="p-6">
              <div class="flex items-start space-x-4">
                <Avatar class="h-12 w-12">
                  <AvatarImage :src="review.image" :alt="review.name" />
                  <AvatarFallback>{{ review.name.charAt(0) }}</AvatarFallback>
                </Avatar>
                <div class="space-y-1">
                  <h3 class="font-semibold">{{ review.name }}</h3>
                  <div class="flex">
                    <Icon
                      v-for="star in 5"
                      :key="star"
                      :name="star <= review.rating ? 'ph:star-fill' : 'ph:star'"
                      class="w-4 h-4"
                    />
                  </div>
                </div>
              </div>
              <p class="mt-4">
                {{ review.comment }}
              </p>
            </CardContent>
          </Card>
        </div>

        <div class="flex justify-center mt-12">
          <Button size="lg" variant="outline"> View All Reviews </Button>
        </div>
      </div>
    </section>

    <!-- Additional CTA Section -->
    <section class="py-20">
      <div class="container px-4 md:px-6">
        <div class="flex flex-col items-center space-y-4 text-center">
          <h2 class="text-3xl font-bold tracking-tighter sm:text-4xl">
            Ready to Transform Your Spa Experience?
          </h2>
          <p class="max-w-[600px]">
            Join our growing community of satisfied users. Sign up today and
            simplify your spa visits.
          </p>
          <NuxtLink to="/register">
            <Button size="lg" class="mt-4"> Get Started </Button></NuxtLink
          >
        </div>
      </div>
    </section>
  </div>
</template>
