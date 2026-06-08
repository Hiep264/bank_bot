interface Props {
  onClick: () => void;
}

function NewChatButton({
  onClick,
}: Props) {

  return (
    <button
      onClick={onClick}
      className="
        w-full
        p-3
        rounded-lg
        cursor-pointer
        bg-blue-600
        hover:bg-blue-700
        text-white
        font-medium
      "
    >
      + New Chat
    </button>
  );
}

export default NewChatButton;
