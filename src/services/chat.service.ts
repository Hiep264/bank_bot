import axios from "axios";

import type {
  ChatRequest,
  ChatResponse,
} from "../types/api";

const API_URL =
  "http://localhost:8000";


export const sendChatMessage =
  async (
    payload: ChatRequest
  ): Promise<ChatResponse> => {

    const response =
      await axios.post<ChatResponse>(
        `${API_URL}/chat`,
        payload
      );

    return response.data;
};