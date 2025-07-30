import { z } from "zod";

export const registerSchema = z
  .object({
    email: z.string().email("Please enter a valid email address"),
    first_name: z.string().nonempty("First Name is required"),
    last_name: z.string().nonempty("Last Name is required"),
    password: z.string().min(8, "Password must be at least 8 characters"),
    password2: z.string().min(1, "Please confirm your password"),
  })
  .refine((data) => data.password === data.password2, {
    message: "Password do not match",
    path: ["password2"],
  });
