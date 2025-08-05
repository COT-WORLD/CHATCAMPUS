import React from "react";

type Variant = "success" | "error" | "info" | "warning";

const variantStyles: Record<Variant, string> = {
  success: "bg-green-500 text-white",
  error: "bg-red-500 text-white",
  info: "bg-blue-500 text-white",
  warning: "bg-yellow-500 text-black",
};

interface ToastProps {
  message?: string | string[] | null;
  onClose: () => void;
  variant?: Variant;
}

const Toast: React.FC<ToastProps> = ({
  message,
  onClose,
  variant = "info",
}) => {
  if (!message || (Array.isArray(message) && message.length === 0)) return null;

  const messages = Array.isArray(message) ? message : [message];

  return (
    <div className="absolute bottom-10 end-10">
      <div
        className={`max-w-xs ${variantStyles[variant]} text-sm rounded-xl shadow-lg`}
        role="alert"
        tabIndex={-1}
        aria-labelledby="toast-label"
      >
        <div id="toast-label" className="flex p-4 items-center">
          {messages.map((msg, i) => (
            <span key={i}>{msg}</span>
          ))}
          <button
            onClick={onClose}
            type="button"
            className="ms-auto inline-flex shrink-0 justify-center items-center size-5 rounded-lg text-white hover:text-white opacity-50 hover:opacity-100 focus:outline-none focus:opacity-100"
            aria-label="Close"
          >
            <span className="sr-only">Close</span>
            <svg
              className="shrink-0 size-4"
              xmlns="http://www.w3.org/2000/svg"
              width={24}
              height={24}
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M18 6 6 18"></path>
              <path d="m6 6 12 12"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Toast;
