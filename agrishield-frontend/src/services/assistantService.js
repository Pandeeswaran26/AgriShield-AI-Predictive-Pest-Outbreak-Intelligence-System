import api from "./api";

export const assistantService = {
  sendMessage: (message, history = []) =>
    api.post("/assistant/chat", { message, history }).then((res) => res.data),
};

export default assistantService;
