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

function deduplicatedFetch<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  // 1. If a request for this key is ALREADY in flight, return the existing promise
  if (IN_FLIGHT_PROMISES.has(key)) {
    console.log(`[DEDUPLICATED] Resuing existing network request for ${key}`);
    return IN_FLIGHT_PROMISES.get(key) as Promise<T>;
  }

  // 2. Create the new request promise
  const promise = fetcher().finally(() => {
    // Clean up the map once the promise settles (whether success or error)
    IN_FLIGHT_PROMISES.delete(key);
  });

  // Store it so concurrent calls can grab it
  IN_FLIGHT_PROMISES.set(key, promise);
  return promise;
}

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

  const now = Date.now();

  // optimistic
  let newEntry = {
    data: null,
    timestamp:now
  }

  useEffect(() => {

    setIsFetching(true);
    if (!QUERY_CACHE.has(key)) {
      // new entry
      // fire zero argument fetcher function
      let freshFetcher = deduplicatedFetch(key, fetcher);

      freshFetcher
        .then((result) => {
          setData(result);
          newEntry = {...newEntry, data: result}
          QUERY_CACHE.set(key, newEntry);
          setIsLoading(false);
          setIsFetching(false);
        })
        .catch((err) => {
          setError(`An error occured while fetching data. Error: ${err}`);
          setIsLoading(false);
          setIsFetching(false);
        });
    } else {
      // old entry
      let oldEntry = QUERY_CACHE.get(key);
      const ts = oldEntry.timestamp;

      if (now - ts <= options.ttlMs) { // return cache data immediately
        setData(oldEntry.data);
        setIsLoading(false);
        setIsFetching(false);
      } else { // data is stale
        // call the fetcher again
        let freshFetcher = deduplicatedFetch(key, fetcher);
        freshFetcher
          .then((result) => {
            setData(result);
            newEntry = {...newEntry, data: result}
            QUERY_CACHE.set(key, newEntry);
            setIsLoading(false);
            setIsFetching(false);
          })
          .catch((err) => {
            setError(`An error occured while fetching data. Error: ${err}`);
            setIsLoading(false);
            setIsFetching(false);
          });
      }
    }

    // cleanup
    return () => {
      setData(null);
      setIsLoading(true);
      setIsFetching(false);
      setError(null);
    }

  }, [key]);

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
