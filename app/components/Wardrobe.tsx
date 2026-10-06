"use client";

import { useRef, useState } from "react";
import { CATEGORIES, Category, Item, Pairing, addItem, imageSrc, removeItem } from "../lib/api";

const rgb = ([r, g, b]: Item["color"]) => `rgb(${r}, ${g}, ${b})`;

export function UploadForm({ onAdded }: { onAdded: () => void }) {
  const [category, setCategory] = useState<Category>("top");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    const file = fileInput.current?.files?.[0];
    if (!file) {
      setError("Choose a photo first.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await addItem(category, file);
      if (fileInput.current) fileInput.current.value = "";
      onAdded();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form
      onSubmit={submit}
      className="flex flex-wrap items-center gap-3 rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950"
    >
      <select
        aria-label="Category"
        value={category}
        onChange={(e) => setCategory(e.target.value as Category)}
        className="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm capitalize dark:border-zinc-700 dark:bg-zinc-900"
      >
        {CATEGORIES.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>
      <input
        ref={fileInput}
        aria-label="Photo"
        type="file"
        accept="image/png,image/jpeg,image/webp"
        className="text-sm file:mr-3 file:rounded-lg file:border-0 file:bg-zinc-200 file:px-3 file:py-2 file:text-sm dark:file:bg-zinc-800"
      />
      <button
        type="submit"
        disabled={busy}
        className="rounded-lg bg-black px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-white dark:text-black"
      >
        {busy ? "Analyzing…" : "Add to wardrobe"}
      </button>
      {error && <p className="w-full text-sm text-red-600">{error}</p>}
    </form>
  );
}

export function WardrobeGrid({
  items,
  selectedId,
  onSelect,
  onChanged,
}: {
  items: Item[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onChanged: () => void;
}) {
  if (items.length === 0) {
    return <p className="text-sm text-zinc-500">Nothing here yet. Add a few clothing photos above.</p>;
  }
  return (
    <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
      {items.map((item) => (
        <li
          key={item.id}
          className={`overflow-hidden rounded-xl border ${
            selectedId === item.id
              ? "border-black ring-2 ring-black dark:border-white dark:ring-white"
              : "border-zinc-200 dark:border-zinc-800"
          }`}
        >
          <button type="button" onClick={() => onSelect(item.id)} className="block w-full">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={imageSrc(item)} alt={item.category} className="aspect-square w-full object-cover" />
          </button>
          <div className="flex items-center justify-between gap-2 p-2 text-xs">
            <span className="flex items-center gap-2 font-medium capitalize">
              <span
                className="h-3 w-3 rounded-full border border-black/10"
                style={{ backgroundColor: rgb(item.color) }}
              />
              {item.category}
            </span>
            <button
              type="button"
              onClick={async () => {
                await removeItem(item.id);
                onChanged();
              }}
              className="text-zinc-500 hover:text-red-600"
            >
              Remove
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}

export function Pairings({ pairings }: { pairings: Pairing[] | null }) {
  if (pairings === null) return <p className="text-sm text-zinc-500">Scoring pairings…</p>;
  if (pairings.length === 0) {
    return <p className="text-sm text-zinc-500">Add more items to get pairing suggestions.</p>;
  }
  return (
    <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-5">
      {pairings.map((p) => (
        <li key={p.item_id} className="rounded-xl border border-zinc-200 p-2 dark:border-zinc-800">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={imageSrc(p.item)}
            alt={p.item.category}
            className="aspect-square w-full rounded-lg object-cover"
          />
          <p className="mt-2 text-xs font-medium capitalize">{p.item.category}</p>
          <p className="text-xs text-zinc-500">{Math.round(p.score * 100)}% match</p>
          <p className="text-[11px] text-zinc-400">
            color {Math.round(p.color_harmony * 100)} · style {Math.round(p.style_similarity * 100)}
          </p>
        </li>
      ))}
    </ul>
  );
}
