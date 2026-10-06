"use client";

import { useCallback, useEffect, useState } from "react";
import { Pairings, UploadForm, WardrobeGrid } from "./components/Wardrobe";
import { API_URL, Item, Pairing, getPairings, getWardrobe } from "./lib/api";

export default function Home() {
  const [items, setItems] = useState<Item[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  // Results remember which item they belong to, so a stale list is never shown.
  const [result, setResult] = useState<{ forId: string; pairings: Pairing[] } | null>(null);
  const pairings = result && result.forId === selectedId ? result.pairings : null;
  const [offline, setOffline] = useState(false);

  const refresh = useCallback(() => {
    getWardrobe()
      .then((data) => {
        setItems(data);
        setOffline(false);
      })
      .catch(() => setOffline(true));
  }, []);

  useEffect(refresh, [refresh]);

  useEffect(() => {
    if (!selectedId) return;
    let cancelled = false;
    getPairings(selectedId)
      .then((data) => !cancelled && setResult({ forId: selectedId, pairings: data }))
      .catch(() => !cancelled && setResult({ forId: selectedId, pairings: [] }));
    return () => {
      cancelled = true;
    };
  }, [selectedId, items]);

  return (
    <div className="min-h-screen bg-zinc-50 px-6 py-12 text-zinc-900 dark:bg-black dark:text-zinc-100">
      <main className="mx-auto flex max-w-4xl flex-col gap-8">
        <header>
          <h1 className="text-2xl font-semibold tracking-tight">OutfitPicker</h1>
          <p className="mt-1 text-sm text-zinc-500">
            Add photos of your clothes, then pick one to see what goes with it.
          </p>
        </header>

        <UploadForm onAdded={refresh} />

        {offline && (
          <p className="text-sm text-red-600">
            Can&apos;t reach the backend at {API_URL}. Start it with <code>uvicorn main:app</code> in{" "}
            <code>backend/</code>.
          </p>
        )}

        <section>
          <h2 className="mb-3 text-sm font-semibold">Wardrobe ({items.length})</h2>
          <WardrobeGrid
            items={items}
            selectedId={selectedId}
            onSelect={setSelectedId}
            onChanged={() => {
              setSelectedId(null);
              refresh();
            }}
          />
        </section>

        {selectedId && (
          <section>
            <h2 className="mb-3 text-sm font-semibold">Best pairings</h2>
            <Pairings pairings={pairings} />
          </section>
        )}
      </main>
    </div>
  );
}
