<script setup lang="ts">
import { ref } from "vue";
import { fetchAppointments } from "~/service/appointment";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "~/components/ui/table";
const { token } = useAuth();
const appointments = ref<Appointment[]>([]);
const loadAppointments = async () => {
  try {
    const { appointments: fetchedAppointments, count } =
      await fetchAppointments(token.value);
    appointments.value = fetchedAppointments;
    // Do something with fetchedAppointments and count
    console.log(fetchedAppointments, count);
  } catch (error) {
    console.error("Error loading appointments:", error);
  }
};

loadAppointments();
const formatPrice = (price: number) => {
  return price.toFixed(2);
};
console.log("Token", token.value);
</script>

<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">Appointments</h2>
    <div class="overflow-x-auto">
      <Table class="w-full">
        <TableHeader>
          <TableRow class="">
            <TableHead class="font-semibold text-sm uppercase">ID</TableHead>
            <TableHead class="font-semibold text-sm uppercase"
              >Services</TableHead
            >
            <TableHead class="font-semibold text-sm uppercase">Time</TableHead>
            <TableHead class="font-semibold text-sm uppercase"
              >Status</TableHead
            >
            <TableHead class="font-semibold text-sm uppercase"
              >Coupon</TableHead
            >
            <TableHead class="font-semibold text-sm uppercase"
              >Original</TableHead
            >
            <TableHead class="font-semibold text-sm uppercase"
              >Discount</TableHead
            >
            <TableHead class="font-semibold text-sm uppercase">Total</TableHead>
            <TableHead class="font-semibold text-sm uppercase"
              >Payment Method</TableHead
            >
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow
            v-for="(appointment, index) in appointments"
            :key="appointment.id"
            class="transition-colors"
          >
            <TableCell class="font-medium">{{ index + 1 }}</TableCell>
            <TableCell>
              <ul class="list-disc list-inside">
                <li
                  v-for="service in appointment.services"
                  :key="service.id"
                  class="text-sm"
                >
                  {{ service.service_name }}
                </li>
              </ul>
            </TableCell>
            <TableCell class="text-sm">
              {{ new Date(appointment.appointment_time).toLocaleString() }}
            </TableCell>
            <TableCell>
              <span
                class="px-2 py-1 text-xs font-semibold rounded-full"
                :class="{
                  'bg-green-100 text-green-800':
                    appointment.status === 'Confirmed',
                  'bg-yellow-100 text-yellow-800':
                    appointment.status === 'Pending',
                  'bg-red-100 text-red-800': appointment.status === 'Cancelled',
                }"
              >
                {{ appointment.status }}
              </span>
            </TableCell>
            <TableCell>
              <span
                v-if="appointment.coupon"
                class="text-sm text-blue-600 font-medium"
              >
                {{ appointment.coupon.display_name }}
              </span>
              <span v-else class="text-sm">No Coupon</span>
            </TableCell>
            <TableCell class="text-sm">
              ${{ formatPrice(appointment.price_breakdown.base_total) }}
            </TableCell>
            <TableCell class="text-sm text-red-600">
              -${{ formatPrice(appointment.price_breakdown.total_discount) }}
            </TableCell>
            <TableCell class="text-sm font-semibold">
              ${{ formatPrice(appointment.price_breakdown.final_total) }}
            </TableCell>
            <TableCell class="text-sm font-semibold">
              <span v-if="appointment.payment_method">
                {{ appointment.payment_method }}
              </span>
              <span v-else>No payment method provided</span>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  </div>
</template>

<style scoped></style>
