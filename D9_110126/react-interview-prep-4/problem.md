---

### **Difficulty:** Advanced / Full-Stack Engineer Interview Target

### **Scenario: Resilient Client-Side Cache & Stale-While-Revalidate Query Hook**

In full-stack interviews, engineers are frequently asked to build lightweight versions of tools like TanStack Query / SWR. You are tasked with creating a custom React hook—`useQuery`—that implements an in-memory cache, background revalidation, deduplication of concurrent requests, and automated garbage collection / expiration.

---

### **Setup Instructions**

1. Create or open your React TypeScript environment:
```bash
npm create vite@latest react-interview-prep-4 -- --template react-ts
cd react-interview-prep-4
npm install
npm run dev

```


2. Replace `src/App.tsx` with the starter setup below.

---

### **Initial Starter Code**

```tsx
import React, { useState, useEffect, useRef } from 'react';

// Simulated API endpoint with artificial delay
export interface Product {
  id: string;
  name: string;
  price: number;
}

const DATABASE: Record<string, Product> = {
  p1: { id: 'p1', name: 'MacBook Pro M1', price: 1299 },
  p2: { id: 'p2', name: 'Logitech MX Master 3S', price: 99 },
  p3: { id: 'p3', name: 'Keychron K2 Keyboard', price: 89 },
};

export const fetchProductApi = (productId: string): Promise<Product> => {
  console.log(`[NETWORK FETCH] Requesting product: ${productId}`);
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (DATABASE[productId]) {
        resolve({ ...DATABASE[productId] });
      } else {
        reject(new Error(`Product ${productId} not found.`));
      }
    }, 1000);
  });
};

// Global in-memory cache structure (outside component tree)
type CacheEntry<T> = {
  data: T;
  timestamp: number;
};
const QUERY_CACHE = new Map<string, CacheEntry<any>>();
const IN_FLIGHT_PROMISES = new Map<string, Promise<any>>();

// TODO: Implement the useQuery hook with Stale-While-Revalidate logic
export function useQuery<T>(
  key: string,
  fetcher: () => Promise<T>,
  options: { ttlMs?: number } = { ttlMs: 5000 }
) {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isFetching, setIsFetching] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // TODO: Implement cache lookup, stale checking, background revalidation, and promise deduplication

  return { data, isLoading, isFetching, error };
}

export default function ProductInspector() {
  const [selectedId, setSelectedId] = useState<string>('p1');
  const { data, isLoading, isFetching, error } = useQuery(
    `product-${selectedId}`,
    () => fetchProductApi(selectedId),
    { ttlMs: 5000 } // 5-second TTL before data is considered stale
  );

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif', maxWidth: '600px' }}>
      <h2>Product Inspector (SWR Cache Practice)</h2>

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
        {['p1', 'p2', 'p3', 'p4_invalid'].map((id) => (
          <button
            key={id}
            onClick={() => setSelectedId(id)}
            style={{
              padding: '0.5rem 1rem',
              fontWeight: selectedId === id ? 'bold' : 'normal',
              background: selectedId === id ? '#2563eb' : '#e5e7eb',
              color: selectedId === id ? '#ffffff' : '#000000',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Inspect {id}
          </button>
        ))}
      </div>

      <div style={{ border: '1px solid #ccc', padding: '1.5rem', borderRadius: '8px' }}>
        <div style={{ marginBottom: '0.5rem', fontSize: '0.85rem', color: '#666' }}>
          <span>Status: </span>
          {isLoading ? (
            <strong style={{ color: 'orange' }}>Loading Initial...</strong>
          ) : isFetching ? (
            <strong style={{ color: 'blue' }}>Revalidating in background...</strong>
          ) : (
            <strong style={{ color: 'green' }}>Fresh (From Cache)</strong>
          )}
        </div>

        {error && <p style={{ color: 'red' }}>Error: {error}</p>}

        {data && (
          <div>
            <h3>{data.name}</h3>
            <p>Price: ${data.price}</p>
          </div>
        )}
      </div>
    </div>
  );
}

```

---

### **Task Requirements**

1. **Stale-While-Revalidate (SWR) Execution Flow:**
* On hook invocation, check `QUERY_CACHE` for `key`.
* **If cached data exists and is FRESH** ($< \text{ttlMs}$ old): return cached data immediately (`isLoading = false`, `isFetching = false`), and **do not** trigger a network fetch.
* **If cached data exists but is STALE** ($> \text{ttlMs}$ old): render stale data immediately (`isLoading = false`), but set `isFetching = true` and trigger background revalidation. Once the new fetch resolves, update state and overwrite `QUERY_CACHE`.
* **If NO cache entry exists**: set `isLoading = true` and fetch data from network.


2. **Request Deduplication (`IN_FLIGHT_PROMISES`):**
* If two components or rapidly toggled renders invoke `useQuery` with the same `key` while a request is already pending, reuse the existing promise from `IN_FLIGHT_PROMISES` rather than triggering duplicate API calls.


3. **Cleanup & Race Condition Prevention:**
* If `key` changes before a fetch completes, ignore the resolving data of the old key (prevent out-of-order state overwrites).



---

### **Submission Prompt**

Implement `useQuery` in your editor and paste your solution back here when done. Focus on clean state boundaries and promise management—essential skills for senior full-stack evaluation!
