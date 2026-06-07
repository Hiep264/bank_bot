import type { Message }
  from "../../types/chat";

import MessageBubble
  from "./MessageBubble";

interface Props {
  messages: Message[];
}

function MessageList({
  messages,
}: Props) {

  return (
    <div
      className="
        flex-1
        overflow-y-auto
        p-4
        space-y-4
      "
    >
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          message={message}
        />
      ))}
    </div>
  );
}

export default MessageList;