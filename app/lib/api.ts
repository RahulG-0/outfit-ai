export const CATEGORIES = ["top", "bottom", "outerwear", "shoes", "accessory"] as const;
export type Category = (typeof CATEGORIES)[number];

export interface Item {
  id: string;
  category: Category;
  color: [number, number, number];
  image_url: string;
}

export interface Pairing {
  item_id: string;
  score: number;
  category_compatible: boolean;
  color_harmony: number;
  style_similarity: number;
  item: Item;
}

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const imageSrc = (item: Item) => `${API_URL}${item.image_url}`;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { cache: "no-store", ...init });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed (${response.status})`);
  }
  return response.json();
}

export const getWardrobe = () => request<Item[]>("/wardrobe");

export const getPairings = (id: string) => request<Pairing[]>(`/recommend/${id}`);

export const removeItem = (id: string) =>
  request<{ deleted: string }>(`/wardrobe/${id}`, { method: "DELETE" });

export function addItem(category: Category, file: File) {
  const form = new FormData();
  form.append("category", category);
  form.append("image", file);
  return request<Item>("/wardrobe", { method: "POST", body: form });
}
