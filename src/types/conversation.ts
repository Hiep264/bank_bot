export interface Conversation {

  id: number;

  title: string | null;

  summary: string | null;

  created_at: string;

  updated_at: string;
}


export interface MessageResponse {

  id: number;

  conversation_id: number;

  role: "user" | "assistant" | "system";

  content: string;

  message_order: number;

  created_at: string;
}