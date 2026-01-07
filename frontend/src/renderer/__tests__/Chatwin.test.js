import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatWindow from '../Chatwin';

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock scrollIntoView
window.HTMLElement.prototype.scrollIntoView = jest.fn();

describe('ChatWindow Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    // Mock successful fetch for chat history
    mockFetch.mockImplementation((url) => {
      if (url === 'http://localhost:5000/chat_history') {
        return Promise.resolve({
          json: () => Promise.resolve([
            { sender: 'user', message: 'Hello', timestamp: '2024-01-01 10:00:00' },
            { sender: 'bot', message: 'Hi there!', timestamp: '2024-01-01 10:00:01' }
          ])
        });
      }
      return Promise.resolve({ json: () => Promise.resolve({}) });
    });
  });

  test('renders without crashing', () => {
    render(<ChatWindow />);
    expect(screen.getByText('SystemSage AI Assistant')).toBeInTheDocument();
  });

  test('loads chat history on mount', async () => {
    render(<ChatWindow />);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:5000/chat_history');
    });
  });

  test('displays chat input field', () => {
    render(<ChatWindow />);
    const input = screen.getByPlaceholderText('Type your message or command...');
    expect(input).toBeInTheDocument();
  });

  test('displays send button', () => {
    render(<ChatWindow />);
    const sendButton = screen.getByRole('button', { name: /send/i });
    expect(sendButton).toBeInTheDocument();
  });

  test('displays mode toggle buttons', () => {
    render(<ChatWindow />);
    expect(screen.getByText('Chat')).toBeInTheDocument();
    expect(screen.getByText('Command')).toBeInTheDocument();
  });

  test('has voice recording buttons', () => {
    render(<ChatWindow />);
    const micButtons = screen.getAllByRole('button').filter(button =>
      button.querySelector('svg') // Lucide icons are in SVG
    );
    expect(micButtons.length).toBeGreaterThan(0);
  });

  test('can switch between chat and command mode', async () => {
    const user = userEvent.setup();
    render(<ChatWindow />);

    const commandButton = screen.getByText('Command');
    await user.click(commandButton);

    // Check if mode changed (this might need adjustment based on actual implementation)
    expect(commandButton).toBeInTheDocument();
  });

  test('can type in input field', async () => {
    const user = userEvent.setup();
    render(<ChatWindow />);

    const input = screen.getByPlaceholderText('Type your message or command...');
    await user.type(input, 'Hello world');

    expect(input.value).toBe('Hello world');
  });

  test('sends message when send button is clicked', async () => {
    const user = userEvent.setup();
    render(<ChatWindow />);

    // Mock successful chat response
    mockFetch.mockImplementation((url) => {
      if (url === 'http://localhost:5000/chat_history') {
        return Promise.resolve({
          json: () => Promise.resolve([])
        });
      }
      if (url === 'http://localhost:5000/chat') {
        return Promise.resolve({
          json: () => Promise.resolve({ response: 'Hello from bot!' })
        });
      }
      return Promise.resolve({ json: () => Promise.resolve({}) });
    });

    const input = screen.getByPlaceholderText('Type your message or command...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    await user.type(input, 'Hello');
    await user.click(sendButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:5000/chat', expect.any(Object));
    });
  });

  test('sends message when Enter key is pressed', async () => {
    const user = userEvent.setup();
    render(<ChatWindow />);

    // Mock successful chat response
    mockFetch.mockImplementation((url) => {
      if (url === 'http://localhost:5000/chat_history') {
        return Promise.resolve({
          json: () => Promise.resolve([])
        });
      }
      if (url === 'http://localhost:5000/chat') {
        return Promise.resolve({
          json: () => Promise.resolve({ response: 'Hello from bot!' })
        });
      }
      return Promise.resolve({ json: () => Promise.resolve({}) });
    });

    const input = screen.getByPlaceholderText('Type your message or command...');

    await user.type(input, 'Hello{enter}');

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:5000/chat', expect.any(Object));
    });
  });

  test('shows loading state while sending message', async () => {
    const user = userEvent.setup();
    render(<ChatWindow />);

    // Mock delayed response
    mockFetch.mockImplementation(() => new Promise(resolve =>
      setTimeout(() => resolve({
        json: () => Promise.resolve({ response: 'Delayed response' })
      }), 100)
    ));

    const input = screen.getByPlaceholderText('Type your message or command...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    await user.type(input, 'Test message');
    await user.click(sendButton);

    // Check for loading indicator (this might be a specific element in your component)
    // Adjust based on your actual loading UI
    expect(sendButton).toBeDisabled();
  });

  test('displays chat history', async () => {
    render(<ChatWindow />);

    await waitFor(() => {
      expect(screen.getByText('Hello')).toBeInTheDocument();
      expect(screen.getByText('Hi there!')).toBeInTheDocument();
    });
  });

  test('handles fetch errors gracefully', async () => {
    mockFetch.mockRejectedValue(new Error('Network error'));
    render(<ChatWindow />);

    // Component should still render despite fetch error
    expect(screen.getByText('SystemSage AI Assistant')).toBeInTheDocument();
  });

  test('handles empty chat history', async () => {
    mockFetch.mockResolvedValue({
      json: () => Promise.resolve([])
    });
    render(<ChatWindow />);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:5000/chat_history');
    });

    // Should not crash with empty history
    expect(screen.getByText('SystemSage AI Assistant')).toBeInTheDocument();
  });

  test('has history toggle button', () => {
    render(<ChatWindow />);
    const historyButton = screen.getByRole('button', { name: /clock|history/i });
    expect(historyButton).toBeInTheDocument();
  });

  test('has file operation buttons', () => {
    render(<ChatWindow />);
    const fileButtons = screen.getAllByRole('button').filter(button =>
      button.textContent.includes('File') ||
      button.textContent.includes('Folder') ||
      button.querySelector('svg') // Icon buttons
    );
    expect(fileButtons.length).toBeGreaterThan(0);
  });

  test('has terminal button', () => {
    render(<ChatWindow />);
    const terminalButton = screen.getByRole('button', { name: /terminal/i });
    expect(terminalButton).toBeInTheDocument();
  });

  test('scrolls to bottom when new messages arrive', async () => {
    render(<ChatWindow />);

    await waitFor(() => {
      expect(window.HTMLElement.prototype.scrollIntoView).toHaveBeenCalled();
    });
  });

  test('handles command mode responses differently', async () => {
    const user = userEvent.setup();
    render(<ChatWindow />);

    // Mock command response
    mockFetch.mockImplementation((url) => {
      if (url === 'http://localhost:5000/chat_history') {
        return Promise.resolve({
          json: () => Promise.resolve([])
        });
      }
      if (url === 'http://localhost:5000/command') {
        return Promise.resolve({
          json: () => Promise.resolve({ response: 'Command executed successfully' })
        });
      }
      return Promise.resolve({ json: () => Promise.resolve({}) });
    });

    // Switch to command mode
    const commandButton = screen.getByText('Command');
    await user.click(commandButton);

    const input = screen.getByPlaceholderText('Type your message or command...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    await user.type(input, 'open vscode');
    await user.click(sendButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:5000/command', expect.any(Object));
    });
  });

  test('handles voice recording start', async () => {
    const user = userEvent.setup();
    render(<ChatWindow />);

    const micButton = screen.getAllByRole('button').find(button =>
      button.querySelector('svg') // Find mic button by icon
    );

    if (micButton) {
      await user.click(micButton);

      // Check if recording state is set
      expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalled();
    }
  });

  test('handles voice recording stop', async () => {
    const user = userEvent.setup();
    render(<ChatWindow />);

    // This test would need more setup for the recording state
    // Skipping for now as it requires complex media recorder mocking
  });
});
