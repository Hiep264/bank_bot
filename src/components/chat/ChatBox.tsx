import MessageList
  from "./MessageList";

import ChatInput
  from "./ChatInput";

import { useChat }
  from "../../hooks/useChat";

function ChatBox() {

  const {
    messages,
    sendMessage,
    loading,
  } = useChat();

  return (
    <div
      className="
        flex
        flex-col
        flex-1
        bg-gray-50
      "
    >
      <MessageList
        messages={messages}
      />

      <ChatInput
        onSend={sendMessage}
        loading={loading}
      />
    </div>
  );
}

export default ChatBox;