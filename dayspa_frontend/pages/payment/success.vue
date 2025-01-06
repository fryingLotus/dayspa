<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { executePayPalPayment } from "~/service/paypal";
import { useCartStore } from "~/stores/cart";
import {
  Card,
  CardHeader,
  CardContent,
  CardFooter,
  CardTitle,
} from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { Check, X } from "lucide-vue-next";

const { token } = useAuth();
const paymentStatus = ref<"pending" | "success" | "error">("pending");
const errorMessage = ref("");
const isProcessing = ref(false); // Mutex to prevent race conditions
const route = useRoute();
const cartStore = useCartStore();

// Reusable retry function
const retry = async <T,>(
  fn: () => Promise<T>,
  retries = 3,
  delay = 1000,
): Promise<T> => {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      console.warn(
        `Attempt ${attempt} failed. Retrying in ${delay}ms...`,
        error,
      );

      if (attempt === retries) {
        console.error(`All ${retries} attempts failed.`);
        throw error;
      }

      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }
  throw new Error("Retry mechanism failed.");
};

const processPayment = async () => {
  if (isProcessing.value) {
    console.warn("Payment processing already in progress.");
    return; // Prevent overlapping executions
  }

  const paymentId = route.query.paymentId as string;
  const payerId = route.query.PayerID as string;

  console.log("Attempting to process payment:", { paymentId, payerId });

  if (!paymentId || !payerId) {
    console.error("Missing payment details:", { paymentId, payerId });
    paymentStatus.value = "error";
    errorMessage.value = "Payment details are incomplete. Please try again.";
    return;
  }

  isProcessing.value = true; // Lock execution
  try {
    console.log("Executing PayPal payment...");
    const paymentResult = await retry(
      () => executePayPalPayment(paymentId, payerId, token.value),
      3, // Number of retries
      2000, // Delay in milliseconds
    );

    console.log("Payment executed successfully:", paymentResult);
    paymentStatus.value = "success";
  } catch (error) {
    console.error("Error during payment processing:", error);
    paymentStatus.value = "error";
    errorMessage.value =
      error instanceof Error ? error.message : "An unknown error occurred.";
  } finally {
    isProcessing.value = false; // Unlock execution
  }
};

// Trigger on page load
onMounted(processPayment);
definePageMeta({
  middleware: "auth",
});
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <Card class="w-full max-w-2xl">
      <CardHeader>
        <CardTitle class="text-2xl font-bold text-center">
          Payment
          {{
            paymentStatus === "success"
              ? "Successful"
              : paymentStatus === "error"
                ? "Failed"
                : "Processing"
          }}
        </CardTitle>
      </CardHeader>
      <CardContent class="space-y-6">
        <Alert
          :variant="paymentStatus === 'success' ? 'default' : 'destructive'"
        >
          <template v-if="paymentStatus === 'success'">
            <Check class="h-4 w-4 text-green-500" />
          </template>
          <template v-else-if="paymentStatus === 'error'">
            <X class="h-4 w-4 text-red-500" />
          </template>
          <div>
            <AlertTitle>
              {{
                paymentStatus === "success"
                  ? "Payment Confirmed"
                  : paymentStatus === "error"
                    ? "Payment Failed"
                    : "Processing Payment"
              }}
            </AlertTitle>
            <AlertDescription>
              <template v-if="paymentStatus === 'success'">
                Your payment has been successfully processed.
              </template>
              <template v-else-if="paymentStatus === 'error'">
                {{ errorMessage }}
              </template>
              <template v-else>
                Please wait while we process your payment.
              </template>
            </AlertDescription>
          </div>
        </Alert>

        <template v-if="paymentStatus === 'success'">
          <div class="space-y-2">
            <h3 class="text-lg font-semibold">Appointment Detail</h3>
            <Separator />
            <div class="flex justify-between">
              <span>Date:</span>
              <span class="font-medium">{{
                new Date().toLocaleDateString()
              }}</span>
            </div>
            <div class="flex justify-between">
              <span>Total Amount:</span>
              <span class="font-medium"
                >${{ cartStore.totalPrice.toFixed(2) }}</span
              >
            </div>
            <div>
              <h3 class="text-lg font-semibold mt-4">Services</h3>
              <Separator />
              <ul>
                <li
                  v-for="service in cartStore.services"
                  :key="service.id"
                  class="flex justify-between py-2"
                >
                  <span>{{ service.service_name }}</span>
                  <span>${{ parseFloat(service.price).toFixed(2) }}</span>
                </li>
              </ul>
            </div>
          </div>
        </template>
      </CardContent>
      <CardFooter v-if="paymentStatus !== 'pending'" class="flex gap-4">
        <NuxtLink to="/">
          <Button v-if="paymentStatus === 'success'" class="w-full">
            Return to Homepage
          </Button>
        </NuxtLink>

        <Button
          v-if="paymentStatus === 'error'"
          variant="outline"
          class="w-full"
          :disabled="isProcessing"
          @click="processPayment"
        >
          {{ isProcessing ? "Retrying..." : "Retry Payment" }}
        </Button>
      </CardFooter>
    </Card>
  </div>
</template>
