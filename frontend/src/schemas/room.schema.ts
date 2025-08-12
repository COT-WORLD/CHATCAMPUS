import z from "zod";

export const roomSchema = z.object({
  topic: z.string().nonempty("Topic is required"),
  room_name: z.string().nonempty("Room name is required"),
  room_description: z.string().nonempty("Room Description is required"),
});
