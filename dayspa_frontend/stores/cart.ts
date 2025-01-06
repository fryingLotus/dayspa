export const useCartStore = defineStore("cart", {
  state: () => ({
    services: [] as Service[], // Store for services in the cart
    couponInfo: {
      code: "",
      base_total: 0,
      final_total: 0,
      discount_percentage: 0,
      discount_amount: 0,
    } as CouponInfo,
  }),
  getters: {
    totalPrice: (state): number => {
      console.log(
        "Total Price Getter Triggered:",
        state.couponInfo.final_total,
      );

      // Apply discount to each service if coupon is applied
      const total = state.services.reduce((total, service) => {
        const servicePrice = parseFloat(service.price);
        const discountedPrice = state.couponInfo.discount_percentage
          ? servicePrice -
            (servicePrice * state.couponInfo.discount_percentage) / 100
          : servicePrice;
        return total + discountedPrice;
      }, 0);

      // Return the final total price, using the final total if a discount is applied
      return state.couponInfo.final_total || total;
    },
    totalDuration: (state): number => {
      return state.services.reduce(
        (total, service) => total + service.duration,
        0,
      );
    },
    totalItems: (state): number => {
      return state.services.length;
    },
  },
  actions: {
    addService(service: Service) {
      const existingService = this.services.find((s) => s.id === service.id);
      if (existingService) {
        console.log(`This service (ID: ${service.id}) is already in the cart.`);
        return;
      }
      this.services.push(service);
      console.log(
        `Added service (ID: ${service.id}, Name: ${service.service_name}) to the cart.`,
      );
    },
    removeService(index: number) {
      const removedService = this.services[index];
      this.services.splice(index, 1);
      console.log(
        `Removed service (ID: ${removedService.id}, Name: ${removedService.service_name}) from the cart.`,
      );
    },
    setCouponInfo(couponData: {
      base_total: number;
      final_total: number;
      discount_percentage: number;
      discount_amount: number;
      coupon_code?: string;
    }) {
      console.log("setCouponInfo Called:", couponData);

      // Set coupon info using snake_case
      this.$patch({
        couponInfo: {
          code: couponData.coupon_code || null,
          base_total: couponData.base_total,
          final_total: couponData.final_total,
          discount_percentage: couponData.discount_percentage,
          discount_amount: couponData.discount_amount,
        },
      });

      console.log("Updated Coupon Info in Store:", this.couponInfo);
    },

    clearCoupon() {
      this.couponInfo = {
        code: null,
        base_total: 0,
        final_total: 0,
        discount_percentage: 0,
        discount_amount: 0,
      };
    },
    clearCart() {
      this.services = [];
      this.clearCoupon(); // Clear coupon info when cart is cleared
      console.log("Cleared all items from the cart.");
    },
  },
  persist: true,
});
