import { useBaseURL } from "~/service/baseURL";
export const updateUser = async (
  data: { first_name: string; last_name: string },
  token?: string | null,
) => {
  try {
    const baseUrl = useBaseURL();
    const url = `${baseUrl}api/auth/update_user_info/`;
    const { data: response } = await useFetch(url, {
      method: "PUT",
      body: JSON.stringify(data),
      headers: {
        Authorization: `${token}`,
        "Content-Type": "application/json",
      },
    });

    if (response.value) {
      return response.value;
    }

    return null;
  } catch (error) {
    console.error("Error updating user:", error);
    throw new Error("Unable to update user data");
  }
};
export const changePassword = async (
  data: { email: string; new_password: string; old_password: string },
  token?: string | null,
) => {
  try {
    const baseUrl = useBaseURL();
    const url = `${baseUrl}api/auth/change_password/`;

    const response = await $fetch(url, {
      method: "PUT",
      body: JSON.stringify(data),
      headers: {
        Authorization: `${token}`,
        "Content-Type": "application/json",
      },
    });

    // Check for the old_password error in the response and throw an error if it exists
    if (response.old_password) {
      throw new Error(response.old_password); // Specific error message
    }

    // If there's no error, return the response
    return response;
  } catch (error) {
    // Log the full error response for better debugging
    console.error("Error changing user password:", error);

    // Return a detailed error message if possible
    const errorMessage = error.response ? error.response.data : error.message;
    throw new Error(errorMessage || "Unable to change user password");
  }
};
export const requestPasswordReset = async (email: string) => {
  try {
    const baseUrl = useBaseURL();
    const url = `${baseUrl}api/auth/password_reset/`;
    const { data: response } = await useFetch(url, {
      method: "POST",
      body: JSON.stringify({ email }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (response.value) {
      return response.value;
    }

    return null;
  } catch (error) {
    console.error("Error requesting password reset:", error);
    throw new Error("Unable to send password reset email");
  }
};

// Reset the password using the token from the email
export const resetPassword = async (token: string, password: string) => {
  try {
    const baseUrl = useBaseURL();
    const url = `${baseUrl}api/auth/password_reset_confirm/`;

    // Pass the token and password in the request body
    const { data: response } = await useFetch(url, {
      method: "POST",
      body: JSON.stringify({ password, token }), // Include both password and token
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (response?.value) {
      return response.value; // Success response
    }

    return null; // No response value, or failure
  } catch (error) {
    console.error("Error resetting password:", error);
    throw new Error("Unable to reset password");
  }
};
