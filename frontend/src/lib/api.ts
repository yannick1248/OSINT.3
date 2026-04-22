const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

export type ModuleDescriptor = {
  name: string;
  description: string;
  input_schema: Record<string, unknown>;
  output_schema: Record<string, unknown>;
  confidence_levels: string[];
};

async function fetchWithTimeout(input: string, init?: RequestInit): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 7000);

  try {
    return await fetch(input, { ...init, signal: controller.signal, cache: 'no-store' });
  } finally {
    clearTimeout(timeout);
  }
}

export async function listModules(): Promise<ModuleDescriptor[]> {
  const res = await fetchWithTimeout(`${BASE_URL}/modules`);
  if (!res.ok) throw new Error(`listModules failed: ${res.status}`);
  return res.json();
}

export async function runModule(
  name: string,
  params: Record<string, unknown>,
  actorId = 'anonymous',
): Promise<unknown> {
  const res = await fetchWithTimeout(`${BASE_URL}/modules/${name}/run`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ actor_id: actorId, params }),
  });

  if (!res.ok) throw new Error(`runModule(${name}) failed: ${res.status}`);
  return res.json();
}
