export {
  Service,
  ServiceResponse,
  ServiceResponseDetail,
  Appointment,
  SingleAppointmentResponse,
  MultipleAppointmentResponse,
  AppointmentResponseBase,
  AppointmentResponse,
  AppointmentCreateRequest,
  Coupon,
  ChangePasswordResponse,
};

declare global {
  interface ChangePasswordResponse {
    old_password?: string; 
    new_password?: string;
  }
  interface Service {
    id: number;
    service_name: string;
    description: string; 
    price: string;
    duration: number;
    service_image_url: string | null; 
    created_at: string; 
    updated_at: string; 
  }
  interface CouponInfo {
    code: string | null;
    base_total: number | null;
    final_total: number | null;
    discount_percentage: number | null;
    discount_amount: number | null;
  }

  interface PriceBreakdown {
    services: Array<{
      service_id: number; 
      service_name: string; 
      price: string; 
    }>;
    base_total: number; 
    total_discount: number; 
    final_total: number; 
    applied_coupon: string | null; 
  }
  interface ServiceResponse {
    count: number;
    next: string | null;
    previous: string | null;
    results: Service[];
  }
  interface Coupon {
    id: number;
    display_name: string; // e.g., "WEEKDAY35 (30.00% off)"
    coupon_code: string; 
    discount: number; // Discount percentage, e.g., 30
  }

  interface Appointment {
    id: number;
    user: number; 
    services: Service[]; 
    appointment_time: string; 
    status: string; // Appointment status, e.g., "confirmed"
    coupon: Coupon | null; 
    total_price: number | null; // Total price after discounts
    price_breakdown: PriceBreakdown; // Price breakdown information
    created_at: string; 
    payment_method: string | null;
  }

  interface AppointmentResponseBase {
    success: boolean; // Indicates if the request was successful
    message: string; // A message from the API, e.g., "Appointments retrieved successfully"
    status_code: number; // HTTP status code
  }

  interface SingleAppointmentResponse extends AppointmentResponseBase {
    data: Appointment; // Single Appointment object
  }

  interface MultipleAppointmentResponse extends AppointmentResponseBase {
    data: Appointment[]; // Array of Appointment objects
  }

  type AppointmentResponse =
    | SingleAppointmentResponse
    | MultipleAppointmentResponse;

  interface AppointmentCreateRequest
    extends Omit<Appointment, "services" | "price_breakdown"> {
    services: number[]; // Now an array of numbers (service IDs), not full service objects
  }

  interface ServiceResponseDetail {
    success: boolean; 
    message: string; 
    data: Service; 
    status_code: number; 
  }
}
