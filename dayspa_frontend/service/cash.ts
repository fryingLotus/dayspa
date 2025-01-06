import { useBaseURL } from "~/service/baseURL";

export const createCashPayment = async (
  appointmentId: number,
  token: string,
) => {
  try {
    const baseUrl = useBaseURL();

    // Make the API call to create the PayPal payment
    const response = await useFetch<{
      success: boolean;
    }>(`${baseUrl}api/cash/create_cash_payment/`, {
      method: "POST",
      headers: {
        Authorization: `${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ appointment_id: appointmentId }),
    });
    return response.data.value?.success;
  } catch (error) {
    console.error("Error in createCashPayment:", error);
    throw new Error("Error processing cash creation");
  }
};
