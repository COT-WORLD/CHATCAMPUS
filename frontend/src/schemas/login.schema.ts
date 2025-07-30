import { z } from "zod";

export const loginSchema = z.object({
  email: z
    .string({ error: "Email is required" })
    .email("Please enter a valid email address"),
  password: z.string().nonempty("Password is required"),
});

//for use with react hook form
export type LoginSchemaType = z.infer<typeof loginSchema>;
