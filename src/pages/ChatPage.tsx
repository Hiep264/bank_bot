import SideBar
  from "../components/sidebar/SideBar";

import ChatBox
  from "../components/chat/ChatBox";

import {
  ChatProvider,
} from "../context/ChatContext";

function ChatPage() {

  return (
    <ChatProvider>
      <div
        className="flex h-screen"
      >
        <SideBar />
        <ChatBox />
      </div>
    </ChatProvider>
  );
}

export default ChatPage;