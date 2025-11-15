import ProblemSolveShellV2 from "@/components/solve/ProblemSolveShellV2";
import { notFound } from "next/navigation";

export default async function SolveProblemPage({ params }) {
  const { id } = await params;
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const endpoint = `${apiUrl}/api/problems/${encodeURIComponent(id)}`;

  try {
    const res = await fetch(endpoint, { cache: "no-store" });

    if (!res.ok) {
      if (res.status === 404) {
        notFound();
      }
      throw new Error(
        `Failed to fetch problem: ${res.status} ${res.statusText}`
      );
    }

    const problem = await res.json();
    return <ProblemSolveShellV2 problem={problem} />;
  } catch (err) {
    console.error("Error loading problem:", err);
    notFound();
  }
}
