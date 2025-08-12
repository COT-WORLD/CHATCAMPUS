import React from "react";
import type { Topic } from "../types/topic.types";
import type { FieldErrors } from "react-hook-form";

interface FormSelectProps {
  label: string;
  name: string;
  options: Topic[];
  value: string;
  onChange: () => void;
  placeholder: string;
  className?: string;
  type?: React.HTMLInputTypeAttribute;
  required?: boolean;
  errors?: FieldErrors;
}

const FormSelect: React.FC<FormSelectProps> = ({
  label,
  name,
  value,
  onChange,
  options = [],
  required = false,
  errors,
  placeholder = "Select an option",
  className = "",
  ...rest
}) => {
  return (
    <div className="mb-4">
      {label && (
        <label
          htmlFor={name}
          className="block text-[#adb5bd] text-sm mb-1 font-normal"
        >
          {label}
        </label>
      )}
      <input
        type="text"
        name={name}
        id={name}
        onChange={onChange}
        value={value ?? ""}
        list="topic_list"
        autoComplete="off"
        placeholder={placeholder}
        required={required}
        className={`block w-full px-3 py-3 bg-[#495057] border border-[#6c757d] text-[#b2bdbd] rounded-md placeholder-[#adb5bd] focus:outline-none focus:ring-[#71c6dd] focus:border-[#71c6dd] ${className}`}
        aria-invalid={!!errors?.[name]}
        {...rest}
      />
      <datalist id="topic_list">
        <select name={name}>
          {options.map((topic) => (
            <option value={topic.topic_name} key={topic.id || topic.topic_name}>
              {topic.topic_name}
            </option>
          ))}
        </select>
      </datalist>
      {errors?.[name] && (
        <div className="text-[#b2bdbd] text-xs mt-1">
          {typeof errors[name]?.message === "string"
            ? errors[name]!.message
            : `${label} is required`}
        </div>
      )}
    </div>
  );
};

export default FormSelect;
