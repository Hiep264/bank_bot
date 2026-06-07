interface Props {
  title: string;
}

function SidebarItem({
  title,
}: Props) {

  return (
    <div
      className="
        p-3
        rounded-lg
        cursor-pointer
        hover:bg-gray-700
        bg-gray-800
      "
    >
      {title}
    </div>
  );
}

export default SidebarItem;