import api from "./api";

export const historyService = {
  getHistory: ({ page = 1, pageSize = 10, search = "", filters = {}, sortBy = "date", sortOrder = "desc" } = {}) =>
    api
      .get("/history", {
        params: { page, page_size: pageSize, search, sort_by: sortBy, sort_order: sortOrder, ...filters },
      })
      .then((res) => res.data),

  exportCsv: (filters = {}) =>
    api
      .get("/history/export", { params: filters, responseType: "blob" })
      .then((res) => res.data),

  deleteRecord: (id) => api.delete(`/history/${id}`).then((res) => res.data),
};

export default historyService;
