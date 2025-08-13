import { Controller, useForm } from "react-hook-form";
import { Link, useNavigate, useParams } from "react-router-dom";
import FormInput from "../components/FormInput";
import Toast from "../components/Toast";
import { useEffect, useState } from "react";
import FormSelect from "../components/FormSelect";
import type { Topic } from "../types/Topic.types";
import { topicsList } from "../api/main";
import { createRoom, getRoomDetailsById, updateRoomById } from "../api/room";
import z from "zod";
import { roomSchema } from "../schemas/room.schema";
import { parseApiErrors } from "../utils/apiErrors";
import { zodResolver } from "@hookform/resolvers/zod";

const RoomManage = () => {
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string[] | null>(null);
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = !!id;
  const [submitLoading, setSubmitLoading] = useState<boolean>(false);
  const [loading, setLoading] = useState(isEdit);
  const [topics, setTopics] = useState<Topic[]>([]);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
    control,
  } = useForm<z.infer<typeof roomSchema>>({
    resolver: zodResolver(roomSchema),
    defaultValues: {
      topic: "",
      room_name: "",
      room_description: "",
    },
  });

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await topicsList("");
        setTopics(response.data?.topics || []);
        if (isEdit) {
          const response = await getRoomDetailsById(id);

          reset({
            topic: response.data?.room.topic_details.topic_name,
            room_name: response.data?.room.room_name || "",
            room_description: response.data?.room.room_description || "",
          });
        }
      } catch (err: any) {
        setError(err.message || "Failed to load data");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [id, reset, isEdit]);

  const onSubmit = async (data: z.infer<typeof roomSchema>) => {
    setSubmitLoading(true);
    setError(null);
    try {
      if (isEdit) {
        await updateRoomById(id, data);
        setSuccess("Room updated successfully");
      } else {
        await createRoom(data);
        setSuccess("Room created successfully");
      }
      setTimeout(() => {
        navigate(isEdit ? `/roomDetails/${id}` : "/");
      }, 1200);
    } catch (err: any) {
      const apiErrorMessages = parseApiErrors(err.response?.data);
      setError(apiErrorMessages);
    } finally {
      setSubmitLoading(false);
    }
  };
  return (
    <div className="flex h-[90vh] justify-center items-center bg-[#2d2d39] text-[#adb5bd] font-sans">
      <div className="bg-[#3f4156] p-8 rounded-lg shadow-lg w-full max-w-xl">
        <h2 className="text-[#b2bdbd] text-center mb-6 text-xl font-bold relative flex items-center justify-center">
          <Link
            to="/"
            className="absolute left-0 top-1/2 -translate-y-1/2 text-[#b2bdbd] hover:text-[#71c6dd]"
          >
            <i className="fas fa-arrow-left" />
          </Link>
          {isEdit ? "Update" : "Create"} Chat Room
        </h2>
        {loading ? (
          <div className="text-center py-10">Loading...</div>
        ) : (
          <form
            className="form w-full"
            onSubmit={handleSubmit(onSubmit)}
            autoComplete="off"
          >
            <Controller
              name="topic"
              control={control}
              rules={{ required: "Topic is required" }}
              render={({ field }) => (
                <FormSelect
                  label="Topic Name"
                  name="topic"
                  options={topics}
                  value={field.value ?? ""}
                  onChange={field.onChange}
                  errors={errors}
                  required={true}
                  placeholder="Select a topic"
                />
              )}
            />
            <FormInput
              label="Room Name"
              name="room_name"
              placeholder="Room Name"
              register={register}
              required={{ value: true }}
              errors={errors}
              autoComplete="off"
            />
            <FormInput
              label="Room Description"
              name="room_description"
              placeholder="Room Description"
              register={register}
              required={{
                value: true,
              }}
              errors={errors}
              autoComplete="off"
            />
            <button
              type="submit"
              className="bg-[#71c6dd] text-[#3f4156] py-3 px-4 rounded-md w-full font-medium text-base flex justify-center items-center gap-2 transition-opacity duration-300 hover:opacity-90"
              disabled={submitLoading}
            >
              <i className="fas fa-paper-plane"></i>
              {submitLoading
                ? isEdit
                  ? "Updating..."
                  : "Creating..."
                : isEdit
                ? "Update"
                : "Create"}
            </button>
            {error && (
              <Toast
                message={error}
                onClose={() => setError(null)}
                variant="error"
              />
            )}
            {success && (
              <Toast
                message={success}
                onClose={() => setSuccess(null)}
                variant="success"
              />
            )}
          </form>
        )}
      </div>
    </div>
  );
};

export default RoomManage;
