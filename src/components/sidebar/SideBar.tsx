import SidebarItem
  from "./SideBarItem";

import NewChatButton
  from "./NewChatButton";

import {
  useChatContext,
} from "../../context/ChatContext";

function SideBar() {

  const {
    conversations,
    currentConversationId,
    switchConversation,
    createNewConversation,
  } = useChatContext();

  return (
    <div
      className="
        w-64
        bg-gray-900
        text-white
        p-4
        flex
        flex-col
      "
    >
      <h1
        className="
          text-2xl
          font-bold
          mb-4
        "
      >
        Chats
      </h1>

      <NewChatButton
        onClick={
          createNewConversation
        }
      />

      <div
        className="
          flex-1
          overflow-y-auto
          space-y-2
          mt-4
        "
      >
        {conversations.map((
          chat
        ) => (
          <SidebarItem
            key={chat.id}
            id={chat.id}
            title={
              chat.title ?? "New Chat"
            }
            active={
              chat.id ===
              currentConversationId
            }
            onClick={
              switchConversation
            }
          />
        ))}
      </div>
    </div>
  );
}

export default SideBar;