import { useState } from "react";

interface Props {
  onSend: (
    message: string
  ) => void;

  loading: boolean;
}

function ChatInput({
  onSend,
  loading,
}: Props) {

  const [input, setInput] =
    useState("");

  const handleSend = () => {

    if (!input.trim()) return;

    onSend(input);

    setInput("");
  };

  return (
    <div
      className="
        border-t
        p-4
        flex
        gap-2
      "
    >
      <input
        type="text"
        value={input}
        disabled={loading}
        onChange={(e) =>
          setInput(e.target.value)
        }
        placeholder="Type message..."
        className="
          flex-1
          border
          rounded-lg
          px-4
          py-2
        "
      />

      <button
        onClick={handleSend}
        disabled={loading}
        className="
          bg-blue-500
          text-white
          px-4
          rounded-lg
        "
      >
        Send
      </button>
    </div>
  );
}

export default ChatInput;