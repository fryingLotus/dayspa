import { useBaseURL } from "~/service/baseURL";

// Function to create a PayPal payment
export const createPayPalPayment = async (
  appointmentId: number,
  services: any[],
  token: string,
) => {
  try {
    const baseUrl = useBaseURL();

    // Make the API call to create the PayPal payment
    const { data } = await useFetch<{
      success: boolean;
      data: { payment_id: string; approval_url: string };
    }>(`${baseUrl}api/paypal/create_payment/`, {
      method: "POST",
      headers: {
        Authorization: `${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ appointment_id: appointmentId, services }),
    });

    if (data.value?.success) {
      // Return payment ID and approval URL on success
      return data.value.data;
    }
    console.error("Error creating PayPal payment:", data.value?.message);
    throw new Error("Error creating PayPal payment" || data.value?.message);
  } catch (error) {
    console.error("Error in createPayPalPayment:", error);
    throw new Error("Error processing PayPal payment creation");
  }
};

// Function to execute the PayPal payment
export const executePayPalPayment = async (
  paymentId: string,
  payerId: string,
  token: string,
) => {
  try {
    const baseUrl = useBaseURL();

    console.log("Initiating API call to execute PayPal payment:", {
      paymentId,
      payerId,
    });

    // API call to execute PayPal payment
    const { data } = await useFetch<{
      success: boolean;
      data: { payment_id: string; state: string };
      message?: string;
    }>(`${baseUrl}api/paypal/execute_payment/`, {
      method: "POST",
      headers: {
        Authorization: `${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ payment_id: paymentId, payer_id: payerId }),
    });

    console.log("Response from execute_payment API:", data.value);

    if (data.value?.success) {
      return data.value.data;
    }

    const errorMsg = data.value?.message || "Payment execution failed.";
    console.error("Error executing PayPal payment:", errorMsg);
    throw new Error(errorMsg);
  } catch (error) {
    console.error("Error in executePayPalPayment function:", error);
    throw new Error(
      "Error processing PayPal payment execution. Please try again.",
    );
  }
};
