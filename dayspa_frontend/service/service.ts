import { useBaseURL } from "~/service/baseURL";
export const fetchServices = async (page: number, pageSize: number) => {
  try {
    const baseUrl = useBaseURL();
    const { data } = await useFetch<ServiceResponse>(`${baseUrl}api/service/`, {
      params: { page, page_size: pageSize },
    });

    if (data.value) {
      return {
        services: data.value.results,
        count: data.value.count,
      };
    }

    // Fallback if data is unexpected
    return { services: [], count: 0 };
  } catch (error) {
    console.error("Error fetching services:", error);
    throw new Error("Unable to fetch services");
  }
};

export const fetchServiceById = async (id: string) => {
  const baseURL = useBaseURL();
  const { data } = await useFetch<ServiceResponseDetail>(
    `${baseURL}api/service/${id}/`,
  );
  if (data.value) {
    return data.value.data;
  }
  return null;
};

