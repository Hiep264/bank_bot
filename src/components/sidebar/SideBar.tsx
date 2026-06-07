import SidebarItem
  from "./SideBarItem";

function SideBar() {

  const chats = [
    "Chat 1",
    "Chat 2",
    "Chat 3",
  ];

  return (
    <div
      className="
        w-64
        bg-gray-900
        text-white
        p-4
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

      <div className="space-y-2">
        {chats.map((chat) => (
          <SidebarItem
            key={chat}
            title={chat}
          />
        ))}
      </div>
    </div>
  );
}

export default SideBar;