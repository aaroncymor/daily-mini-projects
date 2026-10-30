For a Full Stack Engineer interview, technical evaluators typically look beyond basic UI rendering: they want to see **clean state architecture, proper lifecycle/effect management, async API integration with resilience (race conditions/cancellation), and performant re-render optimizations**.

Here is a focused, real-world React coding challenge designed specifically for a full-stack engineering interview evaluation.

---

### **Difficulty:** Advanced / Intermediate Full-Stack Focus

### **Scenario: Resilient Dashboard Search & Filter Component**

You are building a live user/entity lookup component for an internal operational dashboard. The backend exposes an asynchronous REST endpoint. You need to implement search autocompletion with debouncing, error handling, loading states, and state-synchronization edge cases.

---

### **Setup Instructions**

1. Create a fresh React project using Vite:
```bash
npm create vite@latest react-interview-prep -- --template react-ts
cd react-interview-prep
npm install
npm run dev

```


2. Replace `src/App.tsx` (or `src/App.jsx`) with the starter setup below.

---

### **Initial Starter Code**

```tsx
import React, { useState, useEffect } from 'react';

// Simulated API endpoint with artificial delay and random failures
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
      // Simulating a minor network failure chance
      if (Math.random() < 0.1) {
        return reject(new Error('Internal Server Error (500)'));
      }
      const filtered = MOCK_USERS.filter((u) =>
        u.name.toLowerCase().includes(query.toLowerCase())
      );
      resolve(filtered);
    }, 600 + Math.random() * 400); // Random delay between 600ms-1000ms

    if (signal) {
      signal.addEventListener('abort', () => clearTimeout(timeoutId));
    }
  });
};

export default function UserSearchDashboard() {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState<User[]>([]);
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');

  // TODO: Implement search pipeline & state handling

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

      {/* Render Loading, Error, or Results state here */}
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {results.map((user) => (
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
            <span>{user.status}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

```

---

### **Task Requirements**

1. **Debouncing & Race Condition Prevention:**
* Debounce the search input by **300ms–400ms** so API calls aren't fired on every keystroke.
* Use `AbortController` (or proper cleanup in `useEffect`) to cancel outstanding requests if `searchTerm` changes before the previous response returns (preventing race conditions).


2. **Async State Architecture:**
* Add explicit states for `isLoading` and `error`.
* Handle network failures gracefully (display a readable error message and clear stale data or offer a retry).


3. **Optimized Filtering (Client vs Server):**
* Apply the `statusFilter` (`all`, `active`, `inactive`) efficiently without triggering unnecessary API calls if only the dropdown filter changes (derive filtered state or memoize with `useMemo`).


4. **Edge Cases:**
* Empty input should clear or reset results without throwing errors.
* Rapid typing followed by quick clearing should not display out-of-order results.



---

### **Submission Prompt**

Implement the solution in your IDE, paste your updated code or custom hook solution back here when done, and I will perform a detailed code review assessing performance, edge-case coverage, and clean React idioms!
