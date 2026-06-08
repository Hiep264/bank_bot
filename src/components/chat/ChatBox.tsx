import MessageList
  from "./MessageList";

import ChatInput
  from "./ChatInput";

import {
  useChatContext,
} from "../../context/ChatContext";

function ChatBox() {

  const {
    messages,
    sendMessage,
    loading,
  } = useChatContext();

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