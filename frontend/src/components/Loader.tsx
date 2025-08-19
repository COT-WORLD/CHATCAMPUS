const Loader = () => {
  return (
    <div className="flex items-center min-h-screen overflow-hidden bg-[#2d2d39]">
      <div
        className="w-6 h-6 bg-blue-500 rounded-full bounce-across"
        style={{ animationDelay: "0s" }}
      ></div>
      <div
        className="w-6 h-6 bg-green-500 rounded-full bounce-across"
        style={{ animationDelay: "0.2s" }}
      ></div>
      <div
        className="w-6 h-6 bg-red-500 rounded-full bounce-across"
        style={{ animationDelay: "0.4s" }}
      ></div>
      <div
        className="w-6 h-6 bg-yellow-500 rounded-full bounce-across"
        style={{ animationDelay: "0.6s" }}
      ></div>
    </div>
  );
};

export default Loader;
