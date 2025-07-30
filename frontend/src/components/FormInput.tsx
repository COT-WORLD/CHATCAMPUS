import React from "react";
import type {
  FieldErrors,
  UseFormRegister,
  RegisterOptions,
} from "react-hook-form";

interface FormInputProps {
  label: string;
  name: string;
  type?: React.HTMLInputTypeAttribute;
  placeholder?: string;
  register: UseFormRegister<any>;
  required?: boolean | RegisterOptions;
  errors?: FieldErrors;
  autoComplete?: string;
}

const FormInput: React.FC<FormInputProps> = ({
  label,
  name,
  type = "text",
  placeholder,
  register,
  required,
  errors,
  autoComplete,
}) => {
  const validation = required
    ? typeof required === "boolean"
      ? { required }
      : { required: required.value }
    : undefined;
  return (
    <div className="mb-4">
      <label htmlFor={name} className="block text-sm mb-1">
        {label}
      </label>
      <input
        id={name}
        type={type}
        placeholder={placeholder}
        autoComplete={autoComplete}
        className="w-full p-3 bg-[#495057] border border-[#6c757d] text-[#b2bdbd] rounded placeholder-[#adb5bd]"
        {...register(name, validation)}
        aria-invalid={errors?.[name] ? "true" : "false"}
      />
      {errors?.[name]?.message && typeof errors[name]?.message === "string" && (
        <span role="alert" className="text-red-500 text-sm mt-1 block">
          {errors[name]?.message}
        </span>
      )}
    </div>
  );
};

export default FormInput;
