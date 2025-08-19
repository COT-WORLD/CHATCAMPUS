import { useEffect, useState } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import type { UserType } from "../types/User.types";
import type { Room } from "../types/Room.types";
import type { Message } from "../types/Message.types";
import defaultAvatar from "../assets/avatar.svg";
import { formatDistanceToNow } from "date-fns";
import ConfirmModal from "../components/ConfirmModal";
import { deleteRoom, getRoomDetail } from "../api/room";
import { createMessageInRoom, deleteMessageInRoom } from "../api/message";
import { parseApiErrors } from "../utils/apiErrors";
import Toast from "../components/Toast";
import Loader from "../components/Loader";

const RoomDetail = () => {
  const { id } = useParams<{ id?: string }>();
  const { user, isLoading } = useAuth();
  const navigate = useNavigate();
  const [inputValue, setInputValue] = useState<string>("");
  const [isRoomDeleteModalOpen, setRoomDeleteModalOpen] =
    useState<boolean>(false);
  const [isMessageDeleteModalOpen, setMessageDeleteModalOpen] =
    useState<boolean>(false);
  const [participants, setParticipants] = useState<UserType[]>([]);
  const [roomsDetails, setRoomsDetails] = useState<Room>();
  const [roomMessages, setRoomMessages] = useState<Message[]>([]);
  const [error, setError] = useState<string[] | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const isHost = user?.id === roomsDetails?.owner?.id;

  const onSendMessage = async (messageBody: string) => {
    if (!id) return <Navigate to="/" replace />;
    const data = { body: messageBody };
    try {
      await createMessageInRoom(id, data);
      fetchRoomDetails();
    } catch (error) {
      console.error("Error while creating message in room", error);
    }
  };
  const onDeleteMessage = async (messageId: number) => {
    try {
      const response = await deleteMessageInRoom(messageId);
      if (response.status == 204) {
        fetchRoomDetails();
      }
    } catch (error: any) {
      const apiErrorMessages = parseApiErrors(error.response?.data);
      setError(apiErrorMessages);
      console.error("Error while deleting message in room", error);
    }
  };
  const onDeleteRoom = async (roomId: number) => {
    try {
      const response = await deleteRoom(roomId);
      if (response.status == 204) {
        navigate("/");
      }
    } catch (error) {
      console.error("Error while deleting message in room", error);
    }
  };

  const fetchRoomDetails = async () => {
    if (!id) return <Navigate to="/" replace />;
    setLoading(true);
    try {
      const response = await getRoomDetail(id);
      setParticipants(response?.data.participants);
      setRoomsDetails(response?.data.room);
      setRoomMessages(response?.data.messages);
    } catch (error) {
      console.error("Error while fetching room details", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoomDetails();
  }, [id]);

  if (isLoading) return <div>Loading.....</div>;
  if (!user) return <div>Not Authenticated</div>;
  if (loading) {
    return <Loader />;
  }

  return (
    <div className="flex flex-col lg:flex-row gap-4 p-5 min-h-screen bg-[#2d2d39] text-[#adb5bd] font-sans overflow-hidden">
      {/* Chat Room Card */}
      <div className="flex flex-col w-full lg:w-[70%] bg-[#3f4156] rounded-lg overflow-hidden shadow-md max-h-screen min-h-0">
        {/* Header */}
        <div className="flex justify-between items-center px-4 py-3 border-b border-[#e0e0e0] bg-[#696d97]">
          <div className="flex items-center text-white gap-2">
            <Link
              to="/"
              className="text-white hover:underline flex items-center gap-2"
            >
              <i className="fas fa-arrow-left" />
              CHAT ROOM
            </Link>
          </div>

          {isHost && (
            <div className="flex items-center gap-4 text-white">
              <Link to={`/updateRoom/${roomsDetails?.id}`}>
                <i className="fas fa-pen" />
              </Link>

              <button
                type="button"
                onClick={() => setRoomDeleteModalOpen(true)}
              >
                <i className="fas fa-times" />
              </button>
              <ConfirmModal
                open={isRoomDeleteModalOpen}
                title="Confirm Deletion"
                description="Are you sure you want to delete this room? This action cannot be undone."
                onCancel={() => setRoomDeleteModalOpen(false)}
                onConfirm={() => {
                  setRoomDeleteModalOpen(false);
                  if (roomsDetails) {
                    onDeleteRoom(roomsDetails?.id);
                  }
                }}
              />
            </div>
          )}
        </div>

        {/* Room Title Section */}
        <div className="p-4 flex flex-col gap-4">
          <div className="flex justify-between items-center flex-wrap gap-2">
            <h2 className="text-[#71c6dd] font-bold text-xl">
              {roomsDetails?.room_name}
            </h2>
            <p className="text-sm text-[#b2bdbd]">
              {roomsDetails?.created_at &&
                formatDistanceToNow(new Date(roomsDetails?.created_at), {
                  addSuffix: true,
                })}
            </p>
          </div>

          <div className="flex flex-col items-start gap-1">
            <span className="text-sm text-[#b2bdbd] uppercase">Hosted by</span>
            {roomsDetails?.owner && (
              <Link
                to={`/userProfile/${roomsDetails.owner.id}`}
                className="flex items-center gap-2 hover:underline"
              >
                <div className="h-[50px] w-[50px] rounded-full overflow-hidden">
                  <img
                    src={roomsDetails.owner.avatar || defaultAvatar}
                    alt="host avatar"
                    className="h-full w-full object-cover"
                  />
                </div>
                <span className="text-[#71c6dd] font-bold text-sm">
                  @{roomsDetails.owner.first_name}
                </span>
              </Link>
            )}
          </div>

          <p className="text-[#b2bdbd] text-base leading-relaxed">
            {roomsDetails?.room_description}
          </p>

          <div className="flex flex-wrap gap-2 mt-2">
            {roomsDetails?.topic_details && (
              <span className="bg-[#696d97] text-[#e5e5e5] px-2 py-1 rounded text-sm">
                {roomsDetails.topic_details.topic_name}
              </span>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="flex flex-col flex-1 min-h-0 bg-[#2d2d39]">
          {/* Scrollable Messages */}
          <div className="flex-1 overflow-y-auto p-4">
            {Array.isArray(roomMessages) &&
              roomMessages?.map((message) => {
                const isOwner = user?.id === message.owner.id;
                return (
                  <div
                    key={message.id}
                    className="mb-4 bg-[#696d97] rounded-lg p-3 shadow"
                  >
                    <div className="flex justify-between items-start text-sm text-[#e5e5e5] mb-2 gap-4">
                      <Link
                        to={`/userProfile/${message.owner.id}`}
                        className="flex items-center gap-2"
                      >
                        <div className="h-[40px] w-[40px] rounded-full overflow-hidden">
                          <img
                            src={message.owner.avatar || defaultAvatar}
                            alt="user avatar"
                            className="w-full h-full object-cover"
                          />
                        </div>
                        <span className="text-[#71c6dd] font-bold">
                          @{message.owner.first_name}
                        </span>
                      </Link>

                      <div className="flex items-center gap-2">
                        <span className="text-[#b2bdbd]">
                          {message.created_at &&
                            formatDistanceToNow(new Date(message.created_at), {
                              addSuffix: true,
                            })}
                        </span>
                        {isOwner && (
                          <>
                            <button
                              type="button"
                              onClick={() => setMessageDeleteModalOpen(true)}
                            >
                              <i className="fas fa-times" />
                            </button>
                            <ConfirmModal
                              open={isMessageDeleteModalOpen}
                              title="Confirm Deletion"
                              description="Are you sure you want to delete this message? This action cannot be undone."
                              onCancel={() => setMessageDeleteModalOpen(false)}
                              onConfirm={() => {
                                setMessageDeleteModalOpen(false);
                                if (message) {
                                  onDeleteMessage(message?.id);
                                }
                              }}
                            />
                          </>
                        )}
                      </div>
                    </div>

                    <p className="text-[#e5e5e5] leading-normal">
                      {message.body}
                    </p>
                  </div>
                );
              })}
          </div>

          {/* Input fixed at bottom */}
          {user && (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (inputValue.trim()) {
                  onSendMessage(inputValue);
                  setInputValue("");
                }
              }}
              className="bg-[#3f4156] p-2 border-t border-gray-700"
            >
              <input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Write your message here..."
                className="w-full p-3 rounded border border-gray-400 text-white bg-transparent focus:outline-none"
                id="message_body"
              />
              {error && (
                <Toast
                  message={error}
                  onClose={() => setError(null)}
                  variant="error"
                />
              )}
            </form>
          )}
        </div>
      </div>

      {/* Participants Card */}
      <div className="w-full lg:w-[30%] bg-[#3f4156] rounded-lg shadow flex flex-col max-h-screen overflow-hidden">
        <div className="px-4 py-3 bg-[#696d97] border-b border-[#e0e0e0]">
          <h3 className="text-white text-base font-semibold">
            PARTICIPANTS ({participants?.length} Joined)
          </h3>
        </div>

        <div className="px-4 py-2 overflow-y-auto">
          {participants?.map((user) => (
            <div key={user.id} className="flex items-start mb-4">
              <Link to={`/userProfile/${user.id}`} className="mr-3">
                <div className="h-[50px] w-[50px] rounded-full overflow-hidden">
                  <img
                    src={user.avatar || defaultAvatar}
                    alt="Participant avatar"
                    className="w-full h-full object-cover"
                  />
                </div>
              </Link>
              <div className="flex flex-col justify-center">
                <span className="font-bold text-[#b2bdbd] text-sm">
                  {user.first_name}
                </span>
                <span className="text-[#71c6dd] text-xs">
                  @{user.first_name}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RoomDetail;
