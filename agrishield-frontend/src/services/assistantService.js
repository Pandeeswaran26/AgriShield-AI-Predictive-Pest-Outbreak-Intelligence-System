import api from "./api";

export const sendMessage = (message, history = []) =>
  api.post("/assistant/chat", { message, history }).then((r) => r.data);
