import { Link } from "react-router-dom";
import { formatDistanceToNow } from "date-fns";
import type { Room } from "../types/room.types";
import type React from "react";
import defaultAvatar from "../assets/avatar.svg";
interface RoomDetailsCardProps {
  roomsDetails: Room[];
}

const RoomDetailsCard: React.FC<RoomDetailsCardProps> = ({ roomsDetails }) => {
  return (
    <div className="w-full">
      {roomsDetails.map((room) => (
        <div
          key={room.id}
          className="bg-[#3f4156] border border-[#495057] text-[#adb5bd] rounded-lg mb-4"
        >
          {/* Card Body */}
          <div className="p-4">
            {/* Host Info */}
            <div className="flex items-center justify-between">
              {/* Host Profile Link, Avatar, and Name */}
              <Link
                to={`/userProfile/${room.owner.id}`}
                className="flex items-center gap-2 text-inherit no-underline"
              >
                <img
                  src={room.owner.avatar ? room.owner.avatar : defaultAvatar}
                  alt="User Avatar"
                  className="w-6 h-6 rounded-full object-cover"
                />
                <span className="text-[#78c2ad] text-sm whitespace-nowrap font-medium">
                  @{room.owner.first_name}
                </span>
              </Link>

              {/* Created Time */}
              <small className="text-[#b2bdbd] text-xs whitespace-nowrap">
                {formatDistanceToNow(new Date(room.created_at), {
                  addSuffix: true,
                })}
              </small>
            </div>

            {/* Room Title */}
            <h5 className="mt-3 text-[#b2bdbd] text-lg font-semibold mb-2">
              <Link
                to={`/roomDetails/${room.id}`}
                className="text-[#e5e5e5] hover:underline no-underline"
              >
                {room.room_name}
              </Link>
            </h5>

            {/* Divider */}
            <hr className="border-[#495057] my-3" />

            {/* Room Footer Meta */}
            <div className="flex justify-between items-center text-[#b2bdbd] text-sm mt-2">
              <span className="flex items-center">
                <i className="fas fa-users mr-1" />
                {room.participants_count} Joined
              </span>
              <span className="bg-[#51546e] text-[#b2bdbd] text-xs px-2 py-1 rounded">
                {room.topic_details.topic_name}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default RoomDetailsCard;
