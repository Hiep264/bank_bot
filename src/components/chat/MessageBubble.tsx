import type { Message }
  from "../../types/chat";

interface Props {
  message: Message;
}

function MessageBubble({
  message,
}: Props) {

  const isUser =
    message.role === "user";

  return (
    <div
      className={`flex ${
        isUser
          ? "justify-end"
          : "justify-start"
      }`}
    >
      <div
        className={`
          max-w-[70%]
          p-3
          rounded-xl
          ${
            isUser
              ? "bg-blue-500 text-white"
              : "bg-gray-200 text-black"
          }
        `}
      >
        {message.content}
      </div>
    </div>
  );
}

export default MessageBubble;