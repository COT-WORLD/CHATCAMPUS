import { Link, useParams } from "react-router-dom";
import FormInput from "../components/FormInput";
import React, { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { useAuth } from "../context/AuthContext";
import { updateUserProfileDetailById } from "../api/user";
import { parseApiErrors } from "../utils/apiErrors";
import Toast from "../components/Toast";

interface UserProfileValues {
  email: string;
  first_name: string;
  last_name: string;
  bio: string;
  avatar: File | null;
}

const EditUserProfile = ({
  initialData = {} as Partial<UserProfileValues>,
}) => {
  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
    watch,
  } = useForm<UserProfileValues>({
    defaultValues: {
      email: initialData.email || "",
      first_name: initialData.first_name || "",
      last_name: initialData.last_name || "",
      bio: initialData.bio || "",
      avatar: null,
    },
  });
  const { id } = useParams<{ id?: string }>();
  const fileInput = useRef<HTMLInputElement | null>(null);
  const { user } = useAuth();
  const [toastError, setToastError] = useState<string[] | null>(null);
  const [toastSuccess, setToastSuccess] = useState<string | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string>("");
  watch("avatar");

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file: File | null = e.target.files?.[0] ?? null;
    setValue("avatar", file);
    if (file) setAvatarPreview(URL.createObjectURL(file));
  };

  const fetchUserProfileDetail = async () => {
    if (!user) {
      return <div>Loading user info...</div>;
    }

    reset({
      email: user?.email || "",
      first_name: user?.first_name || "",
      last_name: user?.last_name || "",
      bio: user?.bio || "",
    });
    setAvatarPreview(user?.avatar || "");
    try {
    } catch (error: any) {
      const apiErrorMessages = parseApiErrors(error.response?.data);
      setToastError(apiErrorMessages);
      console.error("Error while fetching user details", error);
    }
  };

  const onFormSubmit = async (data: UserProfileValues) => {
    const formData = new FormData();
    formData.append("first_name", data.first_name);
    formData.append("last_name", data.last_name);
    formData.append("email", data.email);
    formData.append("bio", data.bio);
    if (data.avatar instanceof File) {
      formData.append("avatar", data.avatar);
    }
    try {
      await updateUserProfileDetailById(formData);
      setToastSuccess("Profile updated successfully!");
    } catch (error: any) {
      const apiErrorMessages = parseApiErrors(error.response?.data);
      setToastError(apiErrorMessages);
    }
  };

  useEffect(() => {
    if (user) {
      fetchUserProfileDetail();
    }
  }, [id, user]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#2d2d39] text-[#adb5bd] py-8">
      <div className="bg-[#3f4156] shadow-lg rounded-lg w-full max-w-2xl p-8 flex flex-col gap-6">
        <h2 className="relative text-2xl font-semibold flex items-center justify-center text-[#b2bdbd] mb-4">
          <Link
            to="/"
            className="absolute left-0 top-1/2 -translate-y-1/2 text-[#b2bdbd] transition"
            aria-label="Back to home"
          >
            <i className="fas fa-arrow-left" />
          </Link>
          Edit your profile
        </h2>
        <form
          className="flex flex-col gap-4"
          onSubmit={handleSubmit(onFormSubmit)}
          encType="multipart/form-data"
        >
          {/* Non-field Errors */}
          {toastError && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-3 py-2 rounded">
              {toastError}
            </div>
          )}
          {/* First Name */}
          <FormInput
            label="First Name"
            name="first_name"
            placeholder="First Name"
            register={register}
            required={{ value: true }}
            errors={errors}
            autoComplete="given-name"
          />
          {/* Last Name */}
          <FormInput
            label="Last Name"
            name="last_name"
            placeholder="Last Name"
            register={register}
            required={{ value: true }}
            errors={errors}
            autoComplete="family-name"
          />
          {/* Email */}
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
          {/* Bio */}
          <FormInput
            label="Bio"
            name="bio"
            placeholder="Bio"
            register={register}
            required={{ value: true }}
            errors={errors}
            autoComplete="bio-description"
          />
          {/* Avatar */}
          <div className="flex flex-col gap-1">
            <label
              htmlFor="avatar"
              className="text-sm font-medium text-[#3e4166]"
            >
              Avatar
            </label>
            {avatarPreview && (
              <img
                src={avatarPreview}
                alt="Avatar"
                className="w-28 h-28 rounded-full object-cover mb-2 border border-gray-300"
              />
            )}
            <input
              type="file"
              name="avatar"
              id="avatar"
              accept="image/png,image/jpeg,image/webp"
              className="form-input px-3 py-2 rounded-md border border-gray-300 bg-white text-[#22223b]"
              ref={fileInput}
              onChange={handleAvatarChange}
            />
            {errors.avatar && (
              <span className="text-xs text-red-500">
                {errors.avatar.message}
              </span>
            )}
            {toastError && (
              <Toast
                message={toastError}
                onClose={() => setToastError(null)}
                variant="error"
              />
            )}
            {toastSuccess && (
              <Toast
                message={toastSuccess}
                onClose={() => setToastSuccess(null)}
                variant="success"
              />
            )}
          </div>
          <button
            type="submit"
            className="w-full flex gap-2 justify-center items-center text-white bg-gradient-to-r from-[#4e54c8] to-[#8f94fb] hover:from-[#6b7bfc] hover:to-[#4e54c8] font-semibold py-2 px-4 rounded-md transition"
          >
            <i className="fas fa-pen"></i> Update
          </button>
        </form>
      </div>
    </div>
  );
};

export default EditUserProfile;
