<script setup lang="ts">
import { useCartStore } from "~/stores/cart";

import { computed, ref } from "vue";

import type { DateValue } from "@internationalized/date";

import {
  createAppointment,
  validateAppointmentCoupon,
} from "~/service/appointment";
import { createPayPalPayment } from "~/service/paypal";
import { toast } from "vue-sonner";
import { createCashPayment } from "~/service/cash";

const cartStore = useCartStore();

const totalPrice = computed(() => cartStore.totalPrice);
const totalItems = computed(() => cartStore.totalItems);
const totalDuration = computed(() => cartStore.totalDuration);
const { data, token, status } = useAuth();
const userId = data.value?.data.id; // The id of the user
const couponCode = ref("");
const selectedDate = ref<DateValue | null>(null);
const selectedTime = ref();
const selectedPaymentMethod = ref("");

const clearCoupon = () => {
  cartStore.clearCoupon();
  couponCode.value = "";
  toast.success("Coupon has been cleared!");
};

const removeFromCart = (index: number) => {
  cartStore.removeService(index);
  toast.success("You have removed the service succesfully!");
};
const router = useRouter();
const getServicePrice = (serviceId: number) => {
  const service = cartStore.services.find((s) => s.id === serviceId);
  if (!service) return 0;

  const discount = cartStore.couponInfo.discount_percentage;
  const price = parseFloat(service.price);
  const discountedPrice = discount ? price - (price * discount) / 100 : price;

  return discountedPrice;
};
const validateCoupon = async () => {
  if (!couponCode.value) {
    cartStore.clearCoupon();
    return;
  }

  try {
    const couponValidation = await validateAppointmentCoupon(
      {
        services: cartStore.services.map((service) => service.id),
        coupon_code: couponCode.value,
      },
      token.value,
    );
    console.log("Coupon Validation Response:", couponValidation.data);

    if (couponValidation.success && couponValidation.data) {
      // Use the applyCoupon method from the store to apply the coupon
      cartStore.setCouponInfo(couponValidation.data);
      toast.success("Coupon applied successfully!");
    }
  } catch (error) {
    cartStore.clearCoupon();
    toast.error("Invalid coupon code");
  }
};
console.log("Total Price in Component:", totalPrice.value);

const proceedToCheckout = async () => {
  if (!selectedDate.value || !selectedTime.value) {
    console.error("Date and time must be selected.");
    return;
  }

  const dateStr = selectedDate.value.toString();
  const timeStr = selectedTime.value;

  const [year, month, day] = dateStr.split("-");
  const [hours, minutes] = timeStr.split(":");

  const appointmentDateTime = new Date(
    `${year}-${month}-${day}T${hours}:${minutes}:00`,
  );

  const appointmentData = {
    user: userId,
    appointment_time: appointmentDateTime.toISOString(),
    services: cartStore.services.map((service) => service.id),
  };
  if (status.value === "unauthenticated") {
    router.push("/login");
    return;
  }
  // Wrap the whole checkout process in toast.promise
  toast.promise(
    async () => {
      const appointmentResponse = await createAppointment(
        appointmentData,
        token.value,
        couponCode.value,
      );

      if (appointmentResponse) {
        if (selectedPaymentMethod.value === "cash") {
          // Handle cash payment
          console.log("Cash payment selected. Proceeding with cash service.");
          const cashPayment = await createCashPayment(
            appointmentResponse.id,
            token.value,
          );
          router.push("appointment/");
          console.log("cash payment", cashPayment);
        } else if (selectedPaymentMethod.value === "paypal") {
          // Handle PayPal payment
          const paypalPayment = await createPayPalPayment(
            appointmentResponse.id,
            cartStore.services,
            token.value,
          );

          if (paypalPayment.approval_url) {
            window.location.href = paypalPayment.approval_url;
          }
        } else {
          console.error("Invalid payment method selected.");
        }
      }
    },
    {
      loading: "Processing your checkout...",
      success: () => "Checkout successful!",
      error: (error: any) => `Error: ${error.message || "An error occurred"}`,
    },
  );
};
</script>

<template>
  <div class="w-full min-h-screen max-w-3xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
    <div class="space-y-8">
      <!-- Shopping Cart Card -->
      <Card class="w-full">
        <CardHeader>
          <CardTitle>Your Shopping Cart</CardTitle>
        </CardHeader>
        <CardContent>
          <!-- Cart Table -->
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Product</TableHead>
                <TableHead>Price</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead class="hidden sm:table-cell">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow
                v-for="(service, index) in cartStore.services"
                :key="service.id"
              >
                <TableCell>{{ service.service_name }}</TableCell>
                <TableCell
                  >${{ getServicePrice(service.id).toFixed(2) }}</TableCell
                >
                <TableCell>{{ service.duration }} mins</TableCell>
                <TableCell class="sm:table-cell">
                  <Button
                    variant="ghost"
                    size="icon"
                    @click="removeFromCart(index)"
                  >
                    <Icon name="iconamoon:trash-thin" size="22" />
                    <span class="sr-only">Remove item</span>
                  </Button>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>

        <Separator />
        <CardFooter
          class="flex flex-col mt-3 sm:flex-row justify-between items-center sm:items-start sm:space-x-4"
        >
          <div class="text-lg font-semibold">
            <div>
              Total Price:
              <span class="text-green-500">${{ totalPrice.toFixed(2) }}</span>
            </div>
            <div>Total Duration: {{ totalDuration }} mins</div>
            <div>Total Items: {{ totalItems }}</div>
          </div>
        </CardFooter>
      </Card>

      <!-- Appointment Date and Time Selection -->
      <Card class="w-full">
        <CardHeader>
          <CardTitle>Schedule Your Appointment</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <Label for="date" class="block mb-2">Select Date</Label>
              <Datepicker v-model="selectedDate" class="w-full" />
            </div>
            <div>
              <Label for="time" class="block mb-2">Select Time</Label>
              <Input
                v-model="selectedTime"
                type="time"
                id="time"
                class="w-full"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Payment Method Selection -->
      <Card class="w-full">
        <CardHeader>
          <CardTitle>Payment Method</CardTitle>
        </CardHeader>
        <CardContent>
          <RadioGroup
            v-model="selectedPaymentMethod"
            default-value="cash"
            class="flex space-x-4"
          >
            <div class="flex items-center space-x-2">
              <RadioGroupItem id="cash" value="cash" />
              <Label for="cash">Cash</Label>
            </div>
            <div class="flex items-center space-x-2">
              <RadioGroupItem id="paypal" value="paypal" />
              <Label for="paypal">PayPal</Label>
            </div>
          </RadioGroup>
        </CardContent>
      </Card>

      <!-- Coupon Code Section -->
      <Card class="w-full">
        <CardHeader>
          <CardTitle>Enter Coupon Code</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="flex w-full max-w-sm items-center gap-1.5">
            <Input v-model="couponCode" placeholder="Enter Coupon" />
            <Button @click="validateCoupon">Submit</Button>
          </div>
          <div v-if="cartStore.couponInfo.code" class="mt-2">
            <p>
              <strong>Coupon Applied:</strong> {{ cartStore.couponInfo.code }}
            </p>
            <p>
              <strong>Discount:</strong>
              {{ cartStore.couponInfo.discount_percentage }}%
            </p>
            <p>
              <strong>Total Price With Discount:</strong> ${{
                cartStore.couponInfo.discount_amount?.toFixed(2)
              }}
            </p>
            <Button variant="destructive" @click="clearCoupon"
              >Clear Coupon</Button
            >
          </div>
        </CardContent>
      </Card>
      <!-- Checkout Button -->
      <div class="mt-6">
        <AlertDialog>
          <AlertDialogTrigger>
            <Button class="w-full">Proceed to Checkout</Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
              <AlertDialogDescription>
                You're about to pay ${{ totalPrice.toFixed(2) }}
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction @click="proceedToCheckout">
                Continue
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  </div>
</template>
