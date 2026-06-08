import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  type ReactNode,
} from "react";

import type { Message }
  from "../types/chat";

import type { Conversation }
  from "../types/conversation";

import {
  sendChatMessage,
} from "../services/chat.service";

import {
  createConversation as apiCreateConversation,
  getConversations as apiGetConversations,
  getMessages as apiGetMessages,
} from "../services/conversation.service";


interface ChatContextType {

  conversations: Conversation[];

  currentConversationId:
    number | null;

  messages: Message[];

  loading: boolean;

  sendMessage: (
    text: string
  ) => Promise<void>;

  switchConversation: (
    id: number
  ) => Promise<void>;

  createNewConversation: () => Promise<void>;
}


const ChatContext =
  createContext<ChatContextType | null>(
    null
  );


export function ChatProvider({
  children,
}: {
  children: ReactNode;
}) {

  const [conversations,
    setConversations] =
    useState<Conversation[]>([]);

  const [currentConversationId,
    setCurrentConversationId] =
    useState<number | null>(null);

  const [messages, setMessages] =
    useState<Message[]>([]);

  const [loading, setLoading] =
    useState(false);


  const loadConversations =
    useCallback(async () => {

      try {

        const data =
          await apiGetConversations();

        setConversations(data);

      } catch (error) {

        console.error(error);
      }
    }, []);


  useEffect(() => {

    loadConversations();
  }, [loadConversations]);


  const loadMessages = useCallback(
    async (
      conversationId: number
    ) => {

      try {

        const data =
          await apiGetMessages(
            conversationId
          );

        const mapped: Message[] =
          data.map((msg) => ({
            id: String(msg.id),
            role: msg.role,
            content: msg.content,
            createdAt:
              msg.created_at,
          }));

        setMessages(mapped);

      } catch (error) {

        console.error(error);
      }
    },
    []
  );


  const switchConversation =
    useCallback(
      async (
        id: number
      ) => {

        setCurrentConversationId(
          id
        );

        await loadMessages(id);
      },
      [loadMessages]
    );


  const createNewConversation =
    useCallback(async () => {

      try {

        const result =
          await apiCreateConversation();

        const newId =
          result.conversation_id;

        setCurrentConversationId(
          newId
        );

        setMessages([]);

        await loadConversations();

      } catch (error) {

        console.error(error);
      }
    }, [loadConversations]);


  const sendMessage = useCallback(
    async (text: string) => {

      if (!text.trim()) return;

      let convId =
        currentConversationId;

      if (convId === null) {

        try {

          const result =
            await apiCreateConversation();

          convId =
            result.conversation_id;

          setCurrentConversationId(
            convId
          );

        } catch (error) {

          console.error(error);
          return;
        }
      }

      const userMessage: Message = {
        id: crypto.randomUUID(),
        role: "user",
        content: text,
        createdAt:
          new Date().toISOString(),
      };

      setMessages((prev) => [
        ...prev,
        userMessage,
      ]);

      try {

        setLoading(true);

        const response =
          await sendChatMessage({
            conversation_id:
              convId,
            message: text,
          });

        const assistantMessage:
          Message = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.reply,
          createdAt:
            new Date()
              .toISOString(),
        };

        setMessages((prev) => [
          ...prev,
          assistantMessage,
        ]);

        setCurrentConversationId(
          response.conversation_id
        );

        await loadConversations();

      } catch (error) {

        console.error(error);

      } finally {

        setLoading(false);
      }
    },
    [
      currentConversationId,
      loadConversations,
    ]
  );


  return (
    <ChatContext.Provider
      value={{
        conversations,
        currentConversationId,
        messages,
        loading,
        sendMessage,
        switchConversation,
        createNewConversation,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}


export function useChatContext() {

  const context =
    useContext(ChatContext);

  if (!context) {

    throw new Error(
      "useChatContext must be used within ChatProvider"
    );
  }

  return context;
}
