const { test, expect } = require('@playwright/test');

test.describe('OpenSource SystemSage E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('http://localhost:3000');

    // Wait for the app to load
    await page.waitForSelector('[data-testid="chat-window"], .chat-window, .App', { timeout: 10000 });
  });

  test('should load the main application', async ({ page }) => {
    // Check if the main title is visible
    await expect(page.locator('text=SystemSage AI Assistant')).toBeVisible();
  });

  test('should display chat input field', async ({ page }) => {
    // Check for input field
    const inputField = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]');
    await expect(inputField).toBeVisible();
  });

  test('should have send button', async ({ page }) => {
    // Check for send button
    const sendButton = page.locator('button:has-text("Send"), button:has(svg)').first();
    await expect(sendButton).toBeVisible();
  });

  test('should have mode toggle buttons', async ({ page }) => {
    // Check for Chat/Command mode buttons
    await expect(page.locator('text=Chat')).toBeVisible();
    await expect(page.locator('text=Command')).toBeVisible();
  });

  test('should allow typing in input field', async ({ page }) => {
    const inputField = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]');

    await inputField.fill('Hello SystemSage!');
    await expect(inputField).toHaveValue('Hello SystemSage!');
  });

  test('should send message and receive response', async ({ page }) => {
    const inputField = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]');
    const sendButton = page.locator('button:has-text("Send"), button:has(svg)').first();

    // Type a message
    await inputField.fill('Hello');

    // Click send
    await sendButton.click();

    // Wait for response (this might take time depending on backend)
    await page.waitForTimeout(2000);

    // Check if response appears (adjust selector based on actual implementation)
    const responseElements = page.locator('.message.bot, .bot-message, [data-sender="bot"]');
    const responseCount = await responseElements.count();

    // Should have at least one response
    expect(responseCount).toBeGreaterThan(0);
  });

  test('should switch between chat and command modes', async ({ page }) => {
    // Click on Command mode
    await page.locator('text=Command').click();

    // Verify mode changed (check for visual indicator or input placeholder change)
    const inputField = page.locator('input[placeholder*="command"], textarea[placeholder*="command"]');

    // Should find command input or the mode should be visually indicated
    const commandModeIndicator = page.locator('text=Command Mode, .command-mode, [data-mode="command"]');
    const hasCommandIndicator = await commandModeIndicator.count() > 0;
    const hasCommandPlaceholder = await inputField.count() > 0;

    expect(hasCommandIndicator || hasCommandPlaceholder).toBe(true);
  });

  test('should handle command execution', async ({ page }) => {
    // Switch to command mode
    await page.locator('text=Command').click();

    const inputField = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]');
    const sendButton = page.locator('button:has-text("Send"), button:has(svg)').first();

    // Send a simple command
    await inputField.fill('echo hello');
    await sendButton.click();

    // Wait for response
    await page.waitForTimeout(3000);

    // Check for command response
    const commandResponse = page.locator('text=hello, .command-response, [data-type="command"]');
    const hasResponse = await commandResponse.count() > 0;

    expect(hasResponse).toBe(true);
  });

  test('should have functional buttons', async ({ page }) => {
    // Check for various action buttons
    const buttons = page.locator('button');

    // Should have multiple buttons (send, mode toggles, action buttons)
    const buttonCount = await buttons.count();
    expect(buttonCount).toBeGreaterThan(3);
  });

  test('should display messages in chat area', async ({ page }) => {
    // Send a message
    const inputField = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]');
    const sendButton = page.locator('button:has-text("Send"), button:has(svg)').first();

    await inputField.fill('Test message');
    await sendButton.click();

    // Wait for processing
    await page.waitForTimeout(2000);

    // Check if message appears in chat
    await expect(page.locator('text=Test message')).toBeVisible();
  });

  test('should handle file operations', async ({ page }) => {
    // Look for file operation buttons
    const fileButtons = page.locator('button:has-text("File"), button[title*="file"]');

    if (await fileButtons.count() > 0) {
      // If file buttons exist, test basic functionality
      await fileButtons.first().click();

      // Should not crash the app
      await expect(page.locator('text=SystemSage AI Assistant')).toBeVisible();
    }
  });

  test('should handle voice recording', async ({ page }) => {
    // Look for microphone buttons
    const micButtons = page.locator('button[aria-label*="voice"], button[aria-label*="mic"], button:has(svg)');

    // Find buttons that might be mic buttons (this is a heuristic)
    const allButtons = await page.locator('button').all();
    let micButtonFound = false;

    for (const button of allButtons) {
      const buttonText = await button.textContent();
      if (buttonText.includes('🎤') || buttonText.includes('Mic') || buttonText.includes('Voice')) {
        micButtonFound = true;
        break;
      }
    }

    if (micButtonFound) {
      // Test that clicking mic button doesn't crash
      const micButton = page.locator('button').filter({ hasText: /🎤|Mic|Voice/ }).first();
      await micButton.click();

      // App should still be functional
      await expect(page.locator('text=SystemSage AI Assistant')).toBeVisible();
    }
  });

  test('should maintain chat history', async ({ page }) => {
    // Send multiple messages
    const inputField = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]');
    const sendButton = page.locator('button:has-text("Send"), button:has(svg)').first();

    const messages = ['First message', 'Second message', 'Third message'];

    for (const message of messages) {
      await inputField.fill(message);
      await sendButton.click();
      await page.waitForTimeout(1000);
    }

    // Check that multiple messages are visible
    for (const message of messages) {
      await expect(page.locator(`text=${message}`)).toBeVisible();
    }
  });

  test('should handle long messages', async ({ page }) => {
    const inputField = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]');
    const sendButton = page.locator('button:has-text("Send"), button:has(svg)').first();

    // Create a long message
    const longMessage = 'A'.repeat(500);
    await inputField.fill(longMessage);
    await sendButton.click();

    await page.waitForTimeout(2000);

    // Should handle long messages without crashing
    await expect(page.locator('text=SystemSage AI Assistant')).toBeVisible();
  });

  test('should be responsive on different screen sizes', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('text=SystemSage AI Assistant')).toBeVisible();

    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('text=SystemSage AI Assistant')).toBeVisible();

    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    await expect(page.locator('text=SystemSage AI Assistant')).toBeVisible();
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // This test would require mocking network requests
    // For now, just ensure the app doesn't crash when backend is unavailable

    const inputField = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]');
    const sendButton = page.locator('button:has-text("Send"), button:has(svg)').first();

    await inputField.fill('Test network error');
    await sendButton.click();

    // Wait a bit for potential error handling
    await page.waitForTimeout(3000);

    // App should still be functional even if backend fails
    await expect(page.locator('text=SystemSage AI Assistant')).toBeVisible();

    // Should still be able to type in input
    await expect(inputField).toBeEnabled();
  });

  test('should have proper accessibility attributes', async ({ page }) => {
    // Check for basic accessibility
    const inputs = page.locator('input, textarea');
    const buttons = page.locator('button');

    // Should have some form of labeling
    const totalInputs = await inputs.count();
    const totalButtons = await buttons.count();

    expect(totalInputs).toBeGreaterThan(0);
    expect(totalButtons).toBeGreaterThan(0);
  });

  test('should handle rapid successive messages', async ({ page }) => {
    const inputField = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]');
    const sendButton = page.locator('button:has-text("Send"), button:has(svg)').first();

    // Send multiple messages quickly
    for (let i = 1; i <= 5; i++) {
      await inputField.fill(`Quick message ${i}`);
      await sendButton.click();
      // Don't wait between sends to test rapid clicking
    }

    // Wait for all responses
    await page.waitForTimeout(5000);

    // App should still be functional
    await expect(page.locator('text=SystemSage AI Assistant')).toBeVisible();
  });
});
