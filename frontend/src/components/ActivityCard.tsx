import { Link } from "react-router-dom";
import type { Message } from "../types/Message.types";
import type React from "react";
import { formatDistanceToNow } from "date-fns";
import defaultAvatar from "../assets/avatar.svg";
interface ActivityCardProps {
  roomMessages: Message[];
}

const ActivityCard: React.FC<ActivityCardProps> = ({ roomMessages }) => {
  return (
    <div className="w-full">
      <h5 className="text-[#b2bdbd] mb-4 text-sm uppercase tracking-wide">
        Recent Activities
      </h5>

      {roomMessages.map((message) => (
        <div
          key={message.id}
          className="bg-[#3f4156] border border-[#495057] rounded-md mb-4 text-[#adb5bd]"
        >
          <div className="p-4">
            {/* User Info Row */}
            <div className="flex items-center justify-between mb-2">
              <Link
                to={`/userProfile/${message.owner.id}`}
                className="flex items-center text-inherit no-underline gap-2"
              >
                <img
                  src={
                    message.owner.avatar ? message.owner.avatar : defaultAvatar
                  }
                  alt="User Avatar"
                  className="w-6 h-6 rounded-full object-cover"
                />
                <span className="text-[#78c2ad] text-sm font-medium whitespace-nowrap">
                  @{message.owner.first_name || message.owner.email}
                </span>
              </Link>

              <small className="text-[#b2bdbd] text-xs">
                {formatDistanceToNow(new Date(message.created_at), {
                  addSuffix: true,
                })}
              </small>
            </div>

            {/* Activity Content */}
            <p className="text-sm text-[#adb5bd] mb-1 leading-snug">
              replied to post{" "}
              <Link
                to={`/roomDetails/${message.room.id}`}
                className="text-[#78c2ad] hover:underline"
              >
                {message.room.room_name}
              </Link>
            </p>

            {/* Message Content as Badge */}
            <span className="block bg-[#2d2d39] text-[#e5e5e5] text-xs w-full break-words p-2 rounded-xl mt-2 leading-normal">
              {message.body}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ActivityCard;
