---

### **Difficulty:** Advanced / Senior Full-Stack Focus

### **Scenario: Real-Time Event Feed with Optimistic UI & Reconnection Backoff**

You are building a live dashboard feed for real-time order/event updates (e.g., an order management system or activity stream). The feed polls an asynchronous endpoint for new events, allows users to mark items as "Processed", and performs optimistic UI updates with automatic rollback on network failure.

---

### **Setup Instructions**

1. Use your existing Vite + React TypeScript project or initialize a new one:
```bash
npm create vite@latest react-interview-prep-2 -- --template react-ts
cd react-interview-prep-2
npm install
npm run dev

```


2. Replace `src/App.tsx` with the starter code below.

---

### **Initial Starter Code**

```tsx
import React, { useState, useEffect, useCallback, useRef } from 'react';

export interface FeedEvent {
  id: string;
  title: string;
  timestamp: string;
  status: 'pending' | 'processed';
}

// Simulated backend database
let SERVER_EVENTS: FeedEvent[] = [
  { id: 'evt_1', title: 'Order #1001 placed', timestamp: new Date(Date.now() - 30000).toISOString(), status: 'pending' },
  { id: 'evt_2', title: 'Payment received for Order #1000', timestamp: new Date(Date.now() - 60000).toISOString(), status: 'processed' },
  { id: 'evt_3', title: 'Refund requested for Order #998', timestamp: new Date(Date.now() - 90000).toISOString(), status: 'pending' },
];

// API: Fetch latest feed events
export const fetchFeedEventsApi = (): Promise<FeedEvent[]> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // 15% chance of simulated network drop
      if (Math.random() < 0.15) {
        return reject(new Error('Network connection interrupted (503)'));
      }
      resolve([...SERVER_EVENTS]);
    }, 400);
  });
};

// API: Mutation to update event status
export const updateEventStatusApi = (id: string, status: 'pending' | 'processed'): Promise<{ success: boolean }> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // 25% chance of server rejection/failure on mutation
      if (Math.random() < 0.25) {
        return reject(new Error('Failed to update event status on server.'));
      }
      SERVER_EVENTS = SERVER_EVENTS.map((evt) =>
        evt.id === id ? { ...evt, status } : evt
      );
      resolve({ success: true });
    }, 500);
  });
};

export default function EventFeedDashboard() {
  const [events, setEvents] = useState<FeedEvent[]>([]);
  const [isPolling, setIsPolling] = useState(true);
  const [pollErrorCount, setPollErrorCount] = useState(0);

  // TODO: Implement custom polling logic, optimistic updates, and backoff

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif', maxWidth: '650px' }}>
      <h2>Live System Event Feed</h2>
      <div style={{ marginBottom: '1rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <button onClick={() => setIsPolling(!isPolling)}>
          {isPolling ? 'Pause Live Stream' : 'Resume Live Stream'}
        </button>
        <span>Status: {isPolling ? '🟢 Active Polling' : '🟡 Paused'}</span>
        {pollErrorCount > 0 && (
          <span style={{ color: 'orange' }}>Consecutive Errors: {pollErrorCount}</span>
        )}
      </div>

      <ul style={{ listStyle: 'none', padding: 0 }}>
        {events.map((evt) => (
          <li
            key={evt.id}
            style={{
              padding: '1rem',
              marginBottom: '0.5rem',
              border: '1px solid #ddd',
              borderRadius: '6px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              backgroundColor: evt.status === 'processed' ? '#f0fdf4' : '#ffffff',
            }}
          >
            <div>
              <[118;1:3ustrong>{evt.title}</strong>
              <div style={{ fontSize: '0.8rem', color: '#666' }}>
                {new Date(evt.timestamp).toLocaleTimeString()}
              </div>
            </div>

            <div>
              <span
                style={{
                  marginRight: '1rem',
                  fontSize: '0.85rem',
                  fontWeight: 'bold',
                  color: evt.status === 'processed' ? 'green' : 'goldenrod',
                }}
              >
                {evt.status.toUpperCase()}
              </span>
              {evt.status === 'pending' && (
                <button onClick={() => {/* TODO: Implement Optimistic Update */}}>
                  Mark Processed
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

```

---

### **Task Requirements**

1. **Auto-Polling Mechanism (`useInterval` / `useEffect`):**
* Poll `fetchFeedEventsApi` every **3000ms** when `isPolling` is enabled.
* Ensure interval timers are correctly cleaned up on unmount or when polling is paused to prevent memory leaks.


2. **Exponential Backoff on Polling Errors:**
* When polling fails, increment `pollErrorCount` and back off the polling interval exponentially (e.g., $3s \rightarrow 6s \rightarrow 12s \rightarrow \text{max } 30s$).
* Reset backoff delay back to 3000ms upon the first successful fetch.


3. **Optimistic UI Updates with Rollback:**
* Clicking **"Mark Processed"** should immediately set the event's status to `'processed'` in local state before the API promise resolves.
* Call `updateEventStatusApi(id, 'processed')`.
* If the API mutation fails, roll back local state to `'pending'` and display a notification or inline error message indicating the mutation failed.


4. **Stale Closure Avoidance:**
* Ensure the polling callback or interval references the latest state without triggering unnecessary re-subscriptions on every render.



---

### **Submission Prompt**

Implement the polling pipeline and optimistic mutation logic in your editor, then share your code or custom hook solution here for a review on concurrency, hook design, and error recovery patterns!
