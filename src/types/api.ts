import type { Message }
  from "./chat";

export interface ChatRequest {

  messages: {
    role: Message["role"];
    content: string;
  }[];
}

export interface ChatResponse {

  reply: string;
}