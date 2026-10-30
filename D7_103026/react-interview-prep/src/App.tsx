import React, { useState, useEffect, useMemo } from 'react';

interface User {
  id: number;
  name: string;
  role: string;
  status: 'active' | 'inactive';
}

const MOCK_USERS: User[] = [
  { id: 1, name: 'Alice Smith', role: 'Engineering', status: 'active' },
  { id: 2, name: 'Bob Jones', role: 'Product', status: 'active' },
  { id: 3, name: 'Charlie Brown', role: 'Engineering', status: 'inactive' },
  { id: 4, name: 'Diana Prince', role: 'Design', status: 'active' },
  { id: 5, name: 'Evan Wright', role: 'Operations', status: 'inactive' },
];

const fetchUsersApi = (query: string, signal?: AbortSignal): Promise<User[]> => {
  return new Promise((resolve, reject) => {
    const timeoutId = setTimeout(() => {
      if (signal?.aborted) {
        return reject(new DOMException('Aborted', 'AbortError'));
      }
      if (Math.random() < 0.1) {
        return reject(new Error('Internal Server Error (500)'));
      }

      let filtered = MOCK_USERS;
      if (query.trim().length > 0) {
        filtered = MOCK_USERS.filter((u) =>
          u.name.toLowerCase().includes(query.toLowerCase())
        );
      }

      resolve(filtered);
    }, 600 + Math.random() * 400);

    if (signal) {
      signal.addEventListener('abort', () => clearTimeout(timeoutId));
    }
  });
};

function useDebounce<T>(value: T, delay = 400): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

export default function UserSearchDashboard() {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState<User[]>([]);
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const debouncedSearchTerm = useDebounce(searchTerm, 400);

  // 1. Fetching logic with cancellation support
  useEffect(() => {
    const controller = new AbortController();

    async function loadData() {
      setIsLoading(true);
      setError('');

      try {
        const data = await fetchUsersApi(debouncedSearchTerm, controller.signal);
        setResults(data);
      } catch (err: any) {
        // Ignore deliberate aborts from debounced keystrokes
        if (err.name !== 'AbortError') {
          setError(err.message || 'An error occurred while fetching users.');
          setResults([]);
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    }

    loadData();

    return () => {
      controller.abort();
    };
  }, [debouncedSearchTerm]);

  // 2. Derived State for Status Filter (No re-fetching required)
  const visibleUsers = useMemo(() => {
    if (statusFilter === 'all') return results;
    return results.filter((user) => user.status === statusFilter);
  }, [results, statusFilter]);

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif', maxWidth: '600px' }}>
      <h2>User Directory Search</h2>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        <input
          type="text"
          placeholder="Search users..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{ flex: 1, padding: '0.5rem' }}
        />

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as any)}
          style={{ padding: '0.5rem' }}
        >
          <option value="all">All Statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>

      {isLoading && <p>Loading users...</p>}

      {!isLoading && error && (
        <p style={{ color: 'red', fontWeight: 'bold' }}>{error}</p>
      )}

      {!isLoading && !error && visibleUsers.length === 0 && (
        <p>No users found matching criteria.</p>
      )}

      {!isLoading && !error && visibleUsers.length > 0 && (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {visibleUsers.map((user) => (
            <li
              key={user.id}
              style={{
                padding: '0.75rem',
                borderBottom: '1px solid #ccc',
                display: 'flex',
                justifyContent: 'space-between',
              }}
            >
              <span>
                <strong>{user.name}</strong> ({user.role})
              </span>
              <span
                style={{
                  color: user.status === 'active' ? 'green' : 'gray',
                  fontWeight: 'bold',
                }}
              >
                {user.status}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
