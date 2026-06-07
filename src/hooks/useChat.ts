import { useState } from "react";

import type { Message }
  from "../types/chat";

import { sendChatMessage }
  from "../services/chat.service";


export const useChat = () => {

  const [messages, setMessages] =
    useState<Message[]>([
      {
        id: crypto.randomUUID(),

        role: "assistant",

        content: "Hello 👋",

        createdAt:
          new Date().toISOString(),
      },
    ]);

  const [loading, setLoading] =
    useState(false);


  const sendMessage =
    async (text: string) => {

      if (!text.trim()) return;

      const userMessage: Message = {

        id: crypto.randomUUID(),

        role: "user",

        content: text,

        createdAt:
          new Date().toISOString(),
      };

      // update UI trước
      const updatedMessages = [
        ...messages,
        userMessage,
      ];

      setMessages(updatedMessages);

      try {

        setLoading(true);

        // gửi full history cho backend
        const response =
          await sendChatMessage({
            messages:
              updatedMessages.map(
                (message) => ({
                  role: message.role,
                  content: message.content,
                })
              ),
          });

        const assistantMessage: Message =
          {

            id: crypto.randomUUID(),

            role: "assistant",

            content:
              response.reply,

            createdAt:
              new Date().toISOString(),
          };

        setMessages((prev) => [
          ...prev,
          assistantMessage,
        ]);

      } catch (error) {

        console.error(error);

      } finally {

        setLoading(false);

      }
    };

  return {
    messages,
    sendMessage,
    loading,
  };
};