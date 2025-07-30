import { z } from "zod";

export const userSchema = z.object({
  id: z.number(),
  email: z.string(),
  first_name: z.string(),
  avatar: z.string(),
});
