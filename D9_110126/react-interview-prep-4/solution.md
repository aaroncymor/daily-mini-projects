Your `deduplicatedFetch` function is written cleanly and handles promise deduplication as expected. However, inside `useQuery`, there are **4 critical flaws** that an interviewer evaluating a Full Stack role will flag.

---

### Critical Bugs & Flaws

#### 1. Violating Stale-While-Revalidate (SWR) Behavior

* **Issue:** When data is stale, you trigger revalidation, but you **don't set `data` to the cached stale value first**.
* **Impact:** The UI flips back to `data = null` and displays a blank state while fetching, completely destroying the benefit of Stale-While-Revalidate (which should display old data immediately while updating in the background).

#### 2. Stale Timestamps (`Date.now()` outside `useEffect`)

* **Issue:** `const now = Date.now()` runs at the top level of the hook function during render, while `newEntry = { data: null, timestamp: now }` is defined outside `useEffect`.
* **Impact:** When `freshFetcher.then(...)` resolves ~1000ms later, `newEntry` saves the **stale `now` timestamp** from 1 second earlier, skewing your TTL calculation. `Date.now()` must be recorded *when the fetch resolves*.

#### 3. Unnecessary State Flashing in Cleanup

* **Issue:** In the `useEffect` cleanup return function, you run:
```javascript
return () => {
  setData(null);
  setIsLoading(true);
  setIsFetching(false);
  setError(null);
}

```


* **Impact:** Calling state setters during cleanup triggers unneeded state resets and flickering right before unmounting or re-running effects. Cleanup functions in fetching hooks should be used for **cancellation flags / abort controllers**, not for setting state.

#### 4. Susceptibility to Race Conditions

* **Issue:** If a user clicks `p1` $\rightarrow$ `p2` quickly, both promises fire. If `p1` resolves after `p2`, `p1`'s `.then()` callback will execute and overwrite the screen with `p1` data.
* **Fix:** Use a boolean flag (`let isMounted = true`) inside `useEffect` and check `if (!isMounted) return` before updating state.

---

### Complete Clean Implementation

Here is how your solution looks when restructured to pass senior-level interview standards:

```typescript
import React, { useState, useEffect } from 'react';

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

type CacheEntry<T> = {
  data: T;
  timestamp: number;
};

const QUERY_CACHE = new Map<string, CacheEntry<any>>();
const IN_FLIGHT_PROMISES = new Map<string, Promise<any>>();

function deduplicatedFetch<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  if (IN_FLIGHT_PROMISES.has(key)) {
    console.log(`[DEDUPLICATED] Reusing existing network request for ${key}`);
    return IN_FLIGHT_PROMISES.get(key) as Promise<T>;
  }

  const promise = fetcher().finally(() => {
    IN_FLIGHT_PROMISES.delete(key);
  });

  IN_FLIGHT_PROMISES.set(key, promise);
  return promise;
}

export function useQuery<T>(
  key: string,
  fetcher: () => Promise<T>,
  options: { ttlMs?: number } = { ttlMs: 5000 }
) {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isFetching, setIsFetching] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const cachedEntry = QUERY_CACHE.get(key);
    const now = Date.now();
    const isStale = !cachedEntry || now - cachedEntry.timestamp > (options.ttlMs ?? 5000);

    // 1. Immediately hydrate from cache if available (SWR pattern)
    if (cachedEntry) {
      setData(cachedEntry.data);
      setIsLoading(false);

      // If cached data is fresh, no network call required
      if (!isStale) {
        setIsFetching(false);
        setError(null);
        return;
      }
    } else {
      // Hard loading state only when no cache exists
      setIsLoading(true);
      setData(null);
    }

    setIsFetching(true);
    setError(null);

    // 2. Fetch or Revalidate
    deduplicatedFetch(key, fetcher)
      .then((result) => {
        if (!isMounted) return;

        // Cache result with a fresh timestamp recorded at resolution time
        QUERY_CACHE.set(key, { data: result, timestamp: Date.now() });

        setData(result);
        setError(null);
      })
      .catch((err) => {
        if (!isMounted) return;
        setError(err.message || String(err));
      })
      .finally(() => {
        if (!isMounted) return;
        setIsLoading(false);
        setIsFetching(false);
      });

    // 3. Cleanup: Cancel state updates if key changes or component unmounts
    return () => {
      isMounted = false;
    };
  }, [key]);

  return { data, isLoading, isFetching, error };
}

export default function ProductInspector() {
  const [selectedId, setSelectedId] = useState<string>('p1');
  const { data, isLoading, isFetching, error } = useQuery(
    `product-${selectedId}`,
    () => fetchProductApi(selectedId),
    { ttlMs: 5000 }
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
