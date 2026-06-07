import SideBar from "../components/sidebar/SideBar";

import ChatBox
  from "../components/chat/ChatBox";

function ChatPage() {

  return (
    <div className="flex h-screen">
      <SideBar />
      <ChatBox />
    </div>
  );
}

export default ChatPage;