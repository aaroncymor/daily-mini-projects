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
  const [pollingInterval, setPollingInterval] = useState(3000)

  async function fetchFeedEvents() {
    try {
      console.log("fetchFeedEvents() start...");
      const events = await fetchFeedEventsApi();
      setEvents(events);
      console.log("Resetting polling interval back to 3s");
      // reset polling interval
      setPollingInterval(3000);
    } catch(error) {
      console.log("Error occured while fetching feed events...");
      setPollErrorCount((prevCount) => {
        const nextCount = prevCount + 1;
        console.log(`Total error counter updated to : ${nextCount}`)
        return nextCount;
      });
      console.log(`Total error counter: ${pollErrorCount}`);
      // increase polling interval (* 2)
      setPollingInterval((prevInterval) => {
        const nextInterval = Math.min(prevInterval * 2, 30000);
        console.log(`Total backoff time updated to: ${nextInterval}`);
        return nextInterval;
      });
    } finally {
      setIsPolling(false);
    }
  }

  async function updateEventStatus(eventId) {
    // Optimistic update
    setEvents((prevEvents) =>
      prevEvents.map((evt) => evt.id == eventId ? {...evt, status: 'processed'} : evt)
    );
    try {
      await updateEventStatusApi(eventId, 'processed');
    } catch {
      console.log(`Failed to update event status: ${eventId}. Rollingback...`);
      setEvents((prevEvents) =>
        prevEvents.map((evt) => evt.id == eventId ? {...evt, status: 'pending'} : evt)
      );
    }
  }

  // TODO: Implement custom polling logic, optimistic updates, and backoff
  useEffect(() => {

    let interval = null;
    if (isPolling === true) {
      interval = setInterval(() => {
          fetchFeedEvents();
      }, pollingInterval);
    }
    return () => {
      if (isPolling === false && interval) {
        clearInterval(interval);
      }
    }

  }, [isPolling]);

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
              <strong>{evt.title}</strong>
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
                <button onClick={() => { updateEventStatus(evt.id) }}>
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
