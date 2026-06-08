import axios from "axios";

import type {
  Conversation,
} from "../types/conversation";

import type {
  MessageResponse,
} from "../types/conversation";

const API_URL =
  "http://localhost:8000";


export const createConversation =
  async (): Promise<{
    conversation_id: number;
  }> => {

    const response =
      await axios.post<{
        conversation_id: number;
      }>(
        `${API_URL}/conversations`
      );

    return response.data;
};


export const getConversations =
  async (): Promise<
    Conversation[]
  > => {

    const response =
      await axios.get<
        Conversation[]
      >(
        `${API_URL}/conversations`
      );

    return response.data;
};


export const getMessages =
  async (
    conversationId: number
  ): Promise<MessageResponse[]> => {

    const response =
      await axios.get<
        MessageResponse[]
      >(
        `${API_URL}/conversations/${conversationId}/messages`
      );

    return response.data;
};