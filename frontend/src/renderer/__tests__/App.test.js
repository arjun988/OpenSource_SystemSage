import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../App';
import ChatWindow from '../Chatwin';

// Mock the ChatWindow component
jest.mock('../Chatwin', () => {
  return function MockChatWindow() {
    return <div data-testid="chat-window">Chat Window Component</div>;
  };
});

describe('App Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  test('renders without crashing', () => {
    render(<App />);
    expect(screen.getByTestId('chat-window')).toBeInTheDocument();
  });

  test('renders ChatWindow component', () => {
    render(<App />);
    const chatWindow = screen.getByTestId('chat-window');
    expect(chatWindow).toBeInTheDocument();
    expect(chatWindow).toHaveTextContent('Chat Window Component');
  });

  test('has correct structure', () => {
    const { container } = render(<App />);
    const div = container.firstChild;
    expect(div).toBeInTheDocument();
    expect(div.tagName).toBe('DIV');
  });

  test('ChatWindow is rendered as a child', () => {
    const { container } = render(<App />);
    const chatWindow = screen.getByTestId('chat-window');
    expect(container.firstChild).toContainElement(chatWindow);
  });

  test('matches snapshot', () => {
    const { container } = render(<App />);
    expect(container.firstChild).toMatchSnapshot();
  });
});
