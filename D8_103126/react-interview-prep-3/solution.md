import React, { useState } from 'react';

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

export const sendMessageApi = (message: Omit<Message, 'status'>): Promise<{ success: boolean; id: string }> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
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

  // 1. Per-Channel Draft Tracking
  const [drafts, setDrafts] = useState<Record<string, string>>({});

  // Active input value for current channel
  const currentDraft = drafts[activeChannelId] || '';

  const handleChannelSelect = (channelId: string) => {
    setActiveChannelId(channelId);
    // 2. Clear unread badge on switch
    setChannels((prev) =>
      prev.map((ch) => (ch.id === channelId ? { ...ch, unreadCount: 0 } : ch))
    );
  };

  const handleDraftChange = (text: string) => {
    setDrafts((prev) => ({
      ...prev,
      [activeChannelId]: text,
    }));
  };

  const handleSendMessage = async (channelId: string, text: string, retryMsgId?: string) => {
    if (!text.trim() && !retryMsgId) return;

    const msgId = retryMsgId || `m_${Date.now()}`;

    if (!retryMsgId) {
      // 3. Optimistic Update: Append 'sending' message immediately
      const newMessage: Message = {
        id: msgId,
        channelId,
        sender: 'Aaron',
        timestamp: Date.now(),
        text,
        status: 'sending',
      };

      setMessages((prev) => ({
        ...prev,
        [channelId]: [...(prev[channelId] || []), newMessage],
      }));

      // Clear draft for active channel
      setDrafts((prev) => ({ ...prev, [channelId]: '' }));
    } else {
      // Mark failed message back to 'sending' on retry
      setMessages((prev) => ({
        ...prev,
        [channelId]: prev[channelId].map((msg) =>
          msg.id === retryMsgId ? { ...msg, status: 'sending' } : msg
        ),
      }));
    }

    try {
      // 4. Async API Call
      await sendMessageApi({
        id: msgId,
        channelId,
        sender: 'Aaron',
        timestamp: Date.now(),
        text,
      });

      // Update status to 'sent'
      setMessages((prev) => ({
        ...prev,
        [channelId]: prev[channelId].map((msg) =>
          msg.id === msgId ? { ...msg, status: 'sent' } : msg
        ),
      }));
    } catch {
      // Rollback status to 'failed'
      setMessages((prev) => ({
        ...prev,
        [channelId]: prev[channelId].map((msg) =>
          msg.id === msgId ? { ...msg, status: 'failed' } : msg
        ),
      }));
    }
  };

  return (
    <div style={{ display: 'flex', width: '700px', height: '450px', border: '1px solid #ccc', fontFamily: 'sans-serif' }}>
      {/* Sidebar */}
      <div style={{ width: '200px', borderRight: '1px solid #ccc', background: '#f5f5f5', padding: '1rem' }}>
        <h3>Channels</h3>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {channels.map((ch) => (
            <li
              key={ch.id}
              onClick={() => handleChannelSelect(ch.id)}
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
          <h4># {channels.find((c) => c.id === activeChannelId)?.name}</h4>
        </div>

        {/* Messages Body */}
        <div style={{ flex: 1, padding: '1rem', overflowY: 'auto' }}>
          {(messages[activeChannelId] || []).map((msg) => (
            <div key={msg.id} style={{ marginBottom: '0.75rem', opacity: msg.status === 'sending' ? 0.6 : 1 }}>
              <div style={{ fontSize: '0.8rem', color: '#666', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <strong>{msg.sender}</strong> • {new Date(msg.timestamp).toLocaleTimeString()}
                {msg.status === 'failed' && (
                  <>
                    <span style={{ color: 'red' }}>(Failed to send)</span>
                    <button
                      onClick={() => handleSendMessage(activeChannelId, msg.text, msg.id)}
                      style={{ padding: '0.1rem 0.4rem', fontSize: '0.7rem', cursor: 'pointer' }}
                    >
                      Retry
                    </button>
                  </>
                )}
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
            value={currentDraft}
            onChange={(e) => handleDraftChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleSendMessage(activeChannelId, currentDraft);
            }}
          />
          <button
            style={{ padding: '0.5rem 1rem', cursor: 'pointer' }}
            onClick={() => handleSendMessage(activeChannelId, currentDraft)}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
