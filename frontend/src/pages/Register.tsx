import { zodResolver } from "@hookform/resolvers/zod";
import React from "react";
import { useForm } from "react-hook-form";
import { registerSchema } from "../schemas/register.schema";
import z from "zod";
import { signup } from "../api/auth";
import FormInput from "../components/FormInput";
import { Link } from "react-router-dom";

const Register: React.FC = () => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<z.infer<typeof registerSchema>>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: z.infer<typeof registerSchema>) => {
    try {
      const response = await signup(data);
      alert(response.data);
      window.location.href = "/login";
    } catch (error: any) {
      alert(error.response?.data?.detail || "Registration Failed");
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-[#2d2d39] text-[#adb5bd] font-sans">
      <div className="bg-[#3f4156] p-8 rounded-md shadow-lg w-full max-w-[600px]">
        <h2 className="text-center text-[#b2bdbd] mb-6 text-xl font-bold">
          Sign Up
        </h2>
        <form onSubmit={handleSubmit(onSubmit)}>
          <FormInput
            label="First Name"
            name="first_name"
            placeholder="First Name"
            register={register}
            required={{ value: true }}
            errors={errors}
            autoComplete="given-name"
          />

          <FormInput
            label="Last Name"
            name="last_name"
            placeholder="Last Name"
            register={register}
            required={{ value: true }}
            errors={errors}
            autoComplete="family-name"
          />

          <FormInput
            label="Email"
            name="email"
            type="email"
            placeholder="Email address"
            register={register}
            required={{ value: true }}
            errors={errors}
            autoComplete="email"
          />

          <FormInput
            label="Password"
            name="password"
            type="password"
            placeholder="Password"
            register={register}
            required={{ value: true }}
            errors={errors}
            autoComplete="password"
          />

          <FormInput
            label="Confirm Password"
            name="password2"
            type="password"
            placeholder="Confirm Password"
            register={register}
            required={{ value: true }}
            errors={errors}
            autoComplete="password2"
          />
          <button
            type="submit"
            className="bg-[#71c6dd] text-[#3f4156] p-3 rounded w-full text-base transition-all flex items-center justify-center gap-2 hover:opacity-90"
          >
            <i className="fas fa-lock"></i>
            Register
          </button>
          {/* {error && (
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
          )} */}
        </form>
        <p className="text-center mt-4 text-[#adb5bd] text-sm">
          Already signed up
          <Link
            className="block text-center text-[#71c6dd] text-sm mt-2 hover:underline"
            to="/login"
          >
            Login
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
