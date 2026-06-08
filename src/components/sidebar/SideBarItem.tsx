interface Props {
  id: number;

  title: string;

  active: boolean;

  onClick: (
    id: number
  ) => void;
}

function SidebarItem({
  id,
  title,
  active,
  onClick,
}: Props) {

  return (
    <div
      onClick={() =>
        onClick(id)
      }
      className={`
        p-3
        rounded-lg
        cursor-pointer
        hover:bg-gray-700
        ${active
          ? "bg-gray-600"
          : "bg-gray-800"
        }
      `}
    >
      {title}
    </div>
  );
}

export default SidebarItem;