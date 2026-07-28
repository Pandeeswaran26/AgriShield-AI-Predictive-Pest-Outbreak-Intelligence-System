import { Link } from "react-router-dom";
import { Leaf } from "lucide-react";

export default function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-surface-muted px-4 text-center dark:bg-surface-dark">
      <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-600 text-white">
        <Leaf size={26} />
      </span>
      <h1 className="mt-6 font-display text-5xl font-bold">404</h1>
      <p className="mt-2 text-slate-500 dark:text-slate-400">
        This field doesn't exist in AgriShield AI.
      </p>
      <Link to="/" className="btn-primary mt-6">
        Back to home
      </Link>
    </div>
  );
}
