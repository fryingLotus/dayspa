<template>
  <div class="bg-background text-foreground">
    <header class="bg-primary text-primary-foreground py-12">
      <div class="container mx-auto px-4">
        <h1 class="text-4xl font-bold mb-2">About Serenity Spa</h1>
        <p class="text-xl">Relax, Rejuvenate, Revitalize</p>
      </div>
    </header>

    <main class="container mx-auto px-4 py-12">
      <section class="mb-12">
        <h2 class="text-3xl font-semibold mb-4">Our Story</h2>
        <p class="text-lg mb-4">
          Founded with a passion for wellness, Serenity Spa has been providing
          guests with a tranquil escape since 2010. Our mission is to offer the
          finest spa experiences that nurture the mind, body, and soul.
        </p>
        <p class="text-lg">
          From our humble beginnings, we have grown to become a destination for
          relaxation and self-care. We believe in the power of touch, soothing
          therapies, and a peaceful environment to help you unwind, rejuvenate,
          and recharge.
        </p>
      </section>

      <section>
        <h2 class="text-3xl font-semibold mb-6">Our Team</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card v-for="member in teamMembers" :key="member.name">
            <CardHeader>
              <Avatar class="w-24 h-24 mx-auto mb-4">
                <AvatarImage :src="member.avatar" :alt="member.name" />
                <AvatarFallback>{{ getInitials(member.name) }}</AvatarFallback>
              </Avatar>
              <CardTitle>{{ member.name }}</CardTitle>
              <CardDescription>{{ member.role }}</CardDescription>
            </CardHeader>
            <CardContent>
              <p>{{ member.bio }}</p>
            </CardContent>
          </Card>
        </div>
      </section>
    </main>

    <footer class="bg-muted py-6 mt-12">
      <div class="container mx-auto px-4 text-center">
        <p>&copy; 2024 Serenity Spa. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

// Define types for team members
interface TeamMember {
  name: string;
  role: string;
  bio: string;
  avatar: string;
}

const teamMembers: TeamMember[] = [
  {
    name: "Jane Doe",
    role: "Founder & Spa Director",
    bio: "With over 15 years of experience in wellness and spa services, Jane founded Serenity Spa to help people relax and heal in a peaceful environment.",
    avatar: "https://randomuser.me/api/portraits/women/75.jpg",
  },
  {
    name: "John Smith",
    role: "Lead Therapist",
    bio: "John specializes in deep tissue and aromatherapy massages, with a passion for tailoring each session to meet the unique needs of our guests.",
    avatar: "https://randomuser.me/api/portraits/men/45.jpg",
  },
  {
    name: "Emily Brown",
    role: "Head of Wellness",
    bio: "Emily is a certified wellness coach dedicated to guiding clients toward holistic health through mind-body practices, nutrition, and stress management.",
    avatar: "https://randomuser.me/api/portraits/women/55.jpg",
  },
];

// Method to get initials from name
const getInitials = (name: string): string => {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("");
};
</script>

<style scoped>
/* Add any scoped styles for the component here */
</style>
