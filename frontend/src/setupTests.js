import '@testing-library/jest-dom';

// Mock Electron remote
jest.mock('@electron/remote', () => ({
  dialog: {
    showOpenDialog: jest.fn(),
    showSaveDialog: jest.fn(),
    showMessageBox: jest.fn()
  },
  app: {
    getPath: jest.fn(() => '/mock/path')
  }
}));

// Mock fetch globally
global.fetch = jest.fn();

// Mock MediaRecorder
global.MediaRecorder = jest.fn().mockImplementation(() => ({
  start: jest.fn(),
  stop: jest.fn(),
  ondataavailable: jest.fn(),
  onstop: jest.fn(),
  state: 'inactive'
}));

// Mock navigator.mediaDevices
Object.defineProperty(navigator, 'mediaDevices', {
  value: {
    getUserMedia: jest.fn().mockResolvedValue({
      getTracks: jest.fn(() => [{
        stop: jest.fn()
      }])
    })
  },
  writable: true
});

// Mock Blob
global.Blob = jest.fn().mockImplementation((chunks, options) => ({
  size: chunks ? chunks.length : 0,
  type: options ? options.type : ''
}));

// Mock FormData
global.FormData = jest.fn().mockImplementation(() => ({
  append: jest.fn()
}));

// Mock URL.createObjectURL
global.URL.createObjectURL = jest.fn(() => 'mock-object-url');

// Mock URL.revokeObjectURL
global.URL.revokeObjectURL = jest.fn();

// Mock console methods to avoid noise in tests
const originalConsoleError = console.error;
const originalConsoleWarn = console.warn;

beforeAll(() => {
  console.error = jest.fn();
  console.warn = jest.fn();
});

afterAll(() => {
  console.error = originalConsoleError;
  console.warn = originalConsoleWarn;
});

// Cleanup after each test
afterEach(() => {
  jest.clearAllMocks();
});
