import { useBaseURL } from "~/service/baseURL";

export const fetchAppointments = async (token?: string | null) => {
  try {
    const baseUrl = useBaseURL();
    // Construct URL without userId
    const url = `${baseUrl}api/appointments/list_appointments/`;

    // Create headers if token is provided
    const options = token
      ? {
          headers: {
            Authorization: `${token}`,
          },
        }
      : {};

    // Pass the options as the second argument to useFetch
    const { data } = await useFetch<MultipleAppointmentResponse>(url, options);

    if (data.value) {
      return {
        appointments: data.value.data,
        count: data.value.data.length,
      };
    }

    return { appointments: [], count: 0 };
  } catch (error) {
    console.error("Error fetching appointments:", error);
    throw new Error("Unable to fetch appointments");
  }
};

// Fetch appointment details by appointment ID
export const fetchAppointmentById = async (id: number) => {
  const baseUrl = useBaseURL();

  const { data } = await useFetch<AppointmentResponse>(
    `${baseUrl}api/appointments/${id}/`,
  );

  if (data.value) {
    return data.value.data;
  }

  return null;
};

// Create a new appointment
export const createAppointment = async (
  appointmentData: Partial<AppointmentCreateRequest>,
  token: string | null,
  coupon_code: string | null,
): Promise<Appointment | null> => {
  const baseUrl = useBaseURL();
  const options = token
    ? {
        headers: {
          Authorization: `${token}`,
        },
      }
    : {};
  const requestBody = {
    ...appointmentData,
    coupon_code, // Include coupon_code in the body
  };

  const { data } = await useFetch<SingleAppointmentResponse>(
    `${baseUrl}api/appointments/create_appointment/`,
    {
      method: "POST",
      body: JSON.stringify(requestBody),
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    },
  );

  if (data.value) {
    return data.value.data;
  }

  return data.value;
};

// Update an existing appointment by ID
export const updateAppointment = async (
  id: number,
  appointmentData: Partial<Appointment>,
) => {
  const baseUrl = useBaseURL();
  const { data } = await useFetch<AppointmentResponse>(
    `${baseUrl}api/appointments/${id}/update_appointment/`,
    {
      method: "PUT",
      body: JSON.stringify(appointmentData),
      headers: {
        "Content-Type": "application/json",
      },
    },
  );

  if (data.value) {
    return data.value.data;
  }

  return null;
};

export const validateAppointmentCoupon = async (
  couponData: {
    services: number[]; // Array of service IDs
    coupon_code: string; // Coupon code
  },
  token: string | null,
): Promise<{
  success: boolean;
  message: string;
  data?: CouponInfo; // Use Coupon interface for the returned data
}> => {
  const baseUrl = useBaseURL();

  // Prepare request options with Authorization if token exists
  const options = token
    ? {
        headers: {
          Authorization: `${token}`,
        },
      }
    : {};

  try {
    // Use useFetch to make the request
    const { data } = await useFetch<{
      success: boolean;
      message: string;
      data: CouponInfo;
    }>(`${baseUrl}api/appointments/validate_coupon/`, {
      method: "POST",
      body: JSON.stringify(couponData),
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    // Check if the response is successful and return the response data
    if (data.value && data.value.success) {
      return {
        success: true,
        message: data.value.message,
        data: data.value.data, // Returning coupon details
      };
    } else {
      // Handle failure in coupon validation
      throw new Error(data.value?.message || "Coupon validation failed");
    }
  } catch (error) {
    // Log and throw the error
    console.error("Error validating coupon:", error);
    throw error;
  }
};
