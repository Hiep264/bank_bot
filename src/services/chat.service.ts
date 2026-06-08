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


export const sendChatMessageStream =
  async (
    payload: ChatRequest,
    onChunk: (text: string) => void
  ): Promise<ChatResponse> => {

    const response =
      await fetch(
        `${API_URL}/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify(
            payload
          ),
        }
      );

    const data =
      await response.json();

    return data;
};