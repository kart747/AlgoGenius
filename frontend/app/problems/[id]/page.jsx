import { redirect } from "next/navigation";

export default async function ProblemRedirectPage({ params }) {
  const { id } = await params;
  redirect(`/problems/${id}/solve`);
}
