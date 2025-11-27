import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { loginSchema } from "../schemas/login.schema";
import z from "zod";
import { useAuth } from "../context/AuthContext";
import FormInput from "../components/FormInput";
import { Link, useNavigate } from "react-router-dom";
import Toast from "../components/Toast";
import { useState } from "react";
import { parseApiErrors } from "../utils/apiErrors";
import GoogleLogo from "../assets/google.svg";
import { useGoogleLogin } from "@react-oauth/google";
import { ssoLogin } from "../api/auth";
import { setAccessToken, setRefreshToken } from "../utils/tokenStorage";

const Login: React.FC = () => {
  const { login, phase } = useAuth();
  const navigate = useNavigate();
  const isWorking = phase === "logging_in";
  const [toastError, setToastError] = useState<string[] | null>(null);
  const [loadingGoogle, setLoadingGoogle] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<z.infer<typeof loginSchema>>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: z.infer<typeof loginSchema>) => {
    try {
      await login(data.email, data.password);
      navigate("/", { replace: true });
    } catch (error: any) {
      const apiErrorMessages = parseApiErrors(error.response?.data);
      setToastError(apiErrorMessages);
    }
  };

  const googleLogin = useGoogleLogin({
    flow: "implicit",
    onSuccess: async (tokenResponse) => {
      try {
        setLoadingGoogle(true);
        const result = await ssoLogin({
          access_token: tokenResponse.access_token,
        });
        if (result.data?.access && result.data?.refresh) {
          setAccessToken(result.data.access);
          setRefreshToken(result.data.refresh);
          navigate("/", { replace: true });
        } else {
          console.error("Backend did not retrun valid JWT tokens");
        }
      } catch (error) {
        console.error("Google login failed.");
      } finally {
        setLoadingGoogle(false);
      }
    },
    onError: () => setToastError(parseApiErrors("Google login failed.")),
  });
  return (
    <>
      <div className="flex items-center justify-center min-h-screen bg-[#2d2d39] text-[#adb5bd] font-sans overflow-hidden">
        <div className="bg-[#3f4156] p-8 rounded-md shadow-lg w-full max-w-[600px]">
          <h2 className="text-center text-[#b2bdbd] mb-6 text-xl font-bold">
            Login
          </h2>
          <form onSubmit={handleSubmit(onSubmit)}>
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

            <button
              type="submit"
              className="bg-[#71c6dd] text-[#3f4156] p-3 rounded w-full text-base transition-all flex items-center justify-center gap-2 hover:opacity-90"
              disabled={isWorking}
            >
              {isWorking ? (
                <i className="fas fa-spinner fa-spin"></i>
              ) : (
                <i className="fas fa-lock"></i>
              )}
              {isWorking ? "Logging in..." : "Login"}
            </button>

            {toastError && (
              <Toast
                message={toastError}
                onClose={() => setToastError(null)}
                variant="error"
              />
            )}

            <button
              type="button"
              onClick={() => !loadingGoogle && googleLogin()}
              className="mt-4 flex items-center justify-center gap-2 w-full p-3 rounded bg-white text-[#3f4156] font-medium hover:opacity-90 transition-all"
              disabled={loadingGoogle}
            >
              <img src={GoogleLogo} alt="Google" className="h-5 w-5" />
              {loadingGoogle ? "Signing in..." : "Sign in with Google"}
            </button>
          </form>

          <p className="text-center mt-6 text-sm text-[#adb5bd]">
            Haven&apos;t signed up yet?{" "}
            <Link className="text-[#71c6dd] hover:underline" to="/signup">
              Sign Up
            </Link>
          </p>
        </div>
      </div>
    </>
  );
};

export default Login;
