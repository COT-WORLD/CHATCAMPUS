interface ConfirmModal {
  title: string;
  open: boolean;
  description: string;
  onCancel: () => void;
  onConfirm: () => void;
}

const ConfirmModal = ({
  open,
  title,
  description,
  onCancel,
  onConfirm,
}: ConfirmModal) => {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-[#282a36] rounded-lg shadow-xl w-full max-w-md">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700">
          <h5 className="text-lg font-semibold text-[#ff5a5f]">{title}</h5>
          <button
            onClick={onCancel}
            className="text-[#adb5bd] hover:text-[#ff5a5f] text-xl"
          >
            <i className="fas fa-times" />
          </button>
        </div>
        <div className="px-6 py-5">
          <p className="text-[#eee]">{description}</p>
        </div>
        <div className="flex justify-end gap-3 px-6 py-4 border-t border-gray-700">
          <button
            onClick={onCancel}
            className="bg-[#adb5bd] text-[#282a36] px-4 py-2 rounded hover:bg-[#71c6dd] hover:text-[#133449] transition"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="bg-[#ff5a5f] text-white px-4 py-2 rounded hover:bg-[#e04141] transition"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmModal;
