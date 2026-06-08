export interface ChatRequest {

  conversation_id: number | null;

  message: string;
}

export interface ChatResponse {

  reply: string;

  conversation_id: number;
}