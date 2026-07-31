import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 w-full border-b border-slate-800 bg-slate-950/95 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-8 py-5">

        {/* Logo */}
        <Link href="/" className="text-3xl font-bold">
          <span className="text-blue-500">Market</span>
          <span className="text-white">IQ</span>
        </Link>

        {/* Navigation */}
        <div className="hidden items-center gap-8 text-slate-300 md:flex">

          <Link href="/" className="transition hover:text-white">
            Home
          </Link>

          <Link href="/dashboard" className="transition hover:text-white">
            Dashboard
          </Link>

          <a href="#features" className="transition hover:text-white">
            Features
          </a>

          <a href="#pricing" className="transition hover:text-white">
            Pricing
          </a>

          <a href="#about" className="transition hover:text-white">
            About
          </a>

          <a href="#contact" className="transition hover:text-white">
            Contact
          </a>

        </div>

        {/* Buttons */}
        <div className="flex items-center gap-3">

          <button className="rounded-xl border border-slate-700 px-5 py-2 font-semibold text-white transition hover:bg-slate-800">
            Login
          </button>

          <Link
            href="/dashboard"
            className="rounded-xl bg-blue-600 px-5 py-2 font-semibold text-white transition hover:bg-blue-700"
          >
            Analyze Stock
          </Link>

        </div>

      </div>
    </nav>
  );
}