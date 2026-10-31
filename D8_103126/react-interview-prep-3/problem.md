### **Difficulty:** Senior / Full-Stack Focus

### **Scenario: Multi-Channel Real-Time Chat & State Sync Engine**

You are building an enterprise chat sidebar for an internal communications tool. The application connects to a real-time event stream (simulated) where users can switch between channels, draft unsaved messages per channel, handle unread message counters, and perform optimistic message delivery with retry capabilities on network drop.

---

### **Setup Instructions**

1. Create or open your React TypeScript environment:
```bash
npm create vite@latest react-interview-prep-3 -- --template react-ts
cd react-interview-prep-3
npm install
npm run dev

```


2. Replace `src/App.tsx` with the starter setup below.

---

### **Initial Starter Code**

```tsx
import React, { useState, useEffect, useRef, useReducer } from 'react';

export interface Message {
  id: string;
  channelId: string;
  sender: string;
  text: string;
  timestamp: number;
  status: 'sending' | 'sent' | 'failed';
}

export interface Channel {
  id: string;
  name: string;
  unreadCount: number;
}

const INITIAL_CHANNELS: Channel[] = [
  { id: 'general', name: 'General', unreadCount: 0 },
  { id: 'engineering', name: 'Engineering', unreadCount: 2 },
  { id: 'random', name: 'Random', unreadCount: 0 },
];

const INITIAL_MESSAGES: Record<string, Message[]> = {
  general: [
    { id: 'm1', channelId: 'general', sender: 'Alice', text: 'Hey team!', timestamp: Date.now() - 60000, status: 'sent' }
  ],
  engineering: [
    { id: 'm2', channelId: 'engineering', sender: 'Bob', text: 'Deployment ready.', timestamp: Date.now() - 120000, status: 'sent' },
    { id: 'm3', channelId: 'engineering', sender: 'Charlie', text: 'Reviewing PR now.', timestamp: Date.now() - 30000, status: 'sent' }
  ],
  random: []
};

// Simulated Async API to send message
export const sendMessageApi = (message: Omit<Message, 'status'>): Promise<{ success: boolean; id: string }> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // 30% chance of simulated network write failure
      if (Math.random() < 0.3) {
        return reject(new Error('Network error: Message delivery failed'));
      }
      resolve({ success: true, id: message.id });
    }, 800);
  });
};

export default function ChatDashboard() {
  const [activeChannelId, setActiveChannelId] = useState<string>('general');
  const [channels, setChannels] = useState<Channel[]>(INITIAL_CHANNELS);
  const [messages, setMessages] = useState<Record<string, Message[]>>(INITIAL_MESSAGES);

  // TODO: Add draft state tracking per channel
  // TODO: Add active message input state

  return (
    <div style={{ display: 'flex', width: '700px', height: '450px', border: '1px solid #ccc', fontFamily: 'sans-serif' }}>
      {/* Channels Sidebar */}
      <div style={{ width: '200px', borderRight: '1px solid #ccc', background: '#f5f5f5', padding: '1rem' }}>
        <h3>Channels</h3>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {channels.map((ch) => (
            <li
              key={ch.id}
              onClick={() => setActiveChannelId(ch.id)}
              style={{
                padding: '0.5rem',
                cursor: 'pointer',
                borderRadius: '4px',
                marginBottom: '0.25rem',
                background: activeChannelId === ch.id ? '#e0e0e0' : 'transparent',
                display: 'flex',
                justifyContent: 'space-between',
                fontWeight: activeChannelId === ch.id ? 'bold' : 'normal',
              }}
            >
              <span># {ch.name}</span>
              {ch.unreadCount > 0 && (
                <span style={{ background: 'red', color: 'white', borderRadius: '10px', padding: '0.1rem 0.5rem', fontSize: '0.75rem' }}>
                  {ch.unreadCount}
                </span>
              )}
            </li>
          ))}
        </ul>
      </div>

      {/* Main Chat View */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '1rem', borderBottom: '1px solid #ccc', background: '#fafafa' }}>
          <h4># {channels.find(c => c.id === activeChannelId)?.name}</h4>
        </div>

        {/* Messages Body */}
        <div style={{ flex: 1, padding: '1rem', overflowY: 'auto' }}>
          {(messages[activeChannelId] || []).map((msg) => (
            <div key={msg.id} style={{ marginBottom: '0.75rem', opacity: msg.status === 'sending' ? 0.6 : 1 }}>
              <div style={{ fontSize: '0.8rem', color: '#666' }}>
                <strong>{msg.sender}</strong> • {new Date(msg.timestamp).toLocaleTimeString()}
                {msg.status === 'failed' && <span style={{ color: 'red', marginLeft: '0.5rem' }}>(Failed to send)</span>}
              </div>
              <div>{msg.text}</div>
            </div>
          ))}
        </div>

        {/* Input Box */}
        <div style={{ padding: '1rem', borderTop: '1px solid #ccc', display: 'flex', gap: '0.5rem' }}>
          <input
            type="text"
            placeholder="Type a message..."
            style={{ flex: 1, padding: '0.5rem' }}
          />
          <button style={{ padding: '0.5rem 1rem' }}>Send</button>
        </div>
      </div>
    </div>
  );
}

```

---

### **Task Requirements**

1. **Per-Channel Unsaved Drafts:**
* Typing into the input box should[118;1:3u modify the draft text **specifically for the active channel**.
* Switching between channels (e.g., `#general` $\rightarrow$ `#engineering` $\rightarrow$ `#general`) must preserve the typed draft of each channel without losing input state.


2. **Unread Badge Management:**
* Switching to a channel with `unreadCount > 0` must automatically reset its `unreadCount` to `0`.


3. **Optimistic Delivery & Individual Retry:**
* Hitting **Send** immediately adds a message to the active channel's message list with `status: 'sending'`, clears that channel's draft input, and triggers `sendMessageApi`.
* On API resolve: update the message's status to `'sent'`.
* On API reject: set status to `'failed'`. Failed messages should display a **"Retry"** button inline that allows re-attempting delivery for that specific message.


4. **Performance & Data Structure Architecture:**
* Keep state structured cleanly to avoid deep object mutation bugs.



---

### **Submission Prompt**

Implement the draft preservation, unread clearing, and optimistic sending/retry flows in your editor. Paste your solution back here when ready for a review!
