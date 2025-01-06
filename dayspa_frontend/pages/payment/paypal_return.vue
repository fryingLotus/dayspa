<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { executePayPalPayment } from "~/service/paypal";

const route = useRoute();
const { token } = useAuth();

const paymentStatus = ref<"pending" | "success" | "error">("pending");
const errorMessage = ref("");

onMounted(async () => {
  try {
    const paymentId = route.query.paymentId as string;
    const payerId = route.query.PayerID as string;

    if (!paymentId || !payerId) {
      throw new Error("Missing payment details");
    }

    const paymentResult = await executePayPalPayment(
      paymentId,
      payerId,
      token.value,
    );

    paymentStatus.value = "success";
  } catch (error) {
    paymentStatus.value = "error";
    errorMessage.value =
      error instanceof Error ? error.message : "Payment failed";
  }
});
</script>

<template>
  <div class="payment-return-container">
    <div v-if="paymentStatus === 'pending'" class="payment-pending">
      <div class="spinner"></div>
      <p>Processing your payment...</p>
    </div>

    <div v-else-if="paymentStatus === 'success'" class="payment-success">
      <div class="success-icon">✓</div>
      <h2>Payment Successful!</h2>
      <p>Thank you for your purchase.</p>
      <router-link to="/appointments" class="btn"
        >View Appointments</router-link
      >
    </div>

    <div v-else-if="paymentStatus === 'error'" class="payment-error">
      <div class="error-icon">✗</div>
      <h2>Payment Failed</h2>
      <p>{{ errorMessage }}</p>
      <router-link to="/checkout" class="btn">Try Again</router-link>
    </div>
  </div>
</template>

<style scoped>
.payment-return-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  text-align: center;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
}

.success-icon,
.error-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.success-icon {
  color: green;
}

.error-icon {
  color: red;
}

.btn {
  display: inline-block;
  padding: 10px 20px;
  margin-top: 20px;
  background-color: #3498db;
  color: white;
  text-decoration: none;
  border-radius: 5px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
