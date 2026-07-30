export default function Navbar() {
  return (
    <nav className="w-full border-b border-slate-800 bg-slate-950">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-8 py-5">

        {/* Logo */}
        <h1 className="text-3xl font-bold">
          <span className="text-blue-500">Market</span>
          <span className="text-white">IQ</span>
        </h1>

        {/* Navigation */}
        <div className="hidden gap-8 text-slate-300 md:flex">
          <a href="#" className="hover:text-white transition">
            Features
          </a>

          <a href="#" className="hover:text-white transition">
            Pricing
          </a>

          <a href="#" className="hover:text-white transition">
            About
          </a>

          <a href="#" className="hover:text-white transition">
            Contact
          </a>
        </div>

        {/* Login Button */}
        <button className="rounded-xl bg-blue-600 px-5 py-2 font-semibold hover:bg-blue-700 transition">
          Login
        </button>

      </div>
    </nav>
  );
}