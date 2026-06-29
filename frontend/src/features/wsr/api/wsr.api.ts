export async function getHealth(): Promise<{ status: string }> {
  const response = await fetch("/api/v1/health");
  return response.json() as Promise<{ status: string }>;
}

