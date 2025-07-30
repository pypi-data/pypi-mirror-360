import { ChatMessages } from '../Chat/ChatMessages';

/**
 * A component for displaying a code execution confirmation dialog
 */
export class CodeConfirmationDialog {
  private chatHistory: HTMLDivElement;
  private messageComponent: ChatMessages;
  private confirmationContainer: HTMLDivElement | null = null;
  private isShowing: boolean = false;

  constructor(chatHistory: HTMLDivElement, messageComponent: ChatMessages) {
    this.chatHistory = chatHistory;
    this.messageComponent = messageComponent;
  }

  /**
   * Show a confirmation dialog for code execution
   * @param code The code to be executed
   * @param isProcessingStopped Whether the processing has been stopped
   * @returns A promise that resolves to true if execution is approved, false otherwise
   */
  public async showConfirmation(
    code: string,
    isProcessingStopped: boolean = false
  ): Promise<boolean> {
    // If processing has been stopped, don't show the dialog and return false
    if (isProcessingStopped) {
      return false;
    }

    this.isShowing = true;

    return new Promise<boolean>(resolve => {
      // Create an inline confirmation message in the chat
      this.confirmationContainer = document.createElement('div');
      this.confirmationContainer.className = 'sage-ai-code-confirmation';

      // Add heading
      const heading = document.createElement('h3');
      heading.textContent = 'Run Cell? (Ctrl+Enter/Cmd+Enter to confirm)';
      heading.className = 'sage-ai-code-confirmation-heading';
      this.confirmationContainer.appendChild(heading);

      const buttonContainer = document.createElement('div');
      buttonContainer.className = 'sage-ai-confirmation-button-container';

      const cancelButton = document.createElement('button');
      cancelButton.textContent = 'Reject';
      cancelButton.className = 'sage-ai-reject-button';

      const confirmButton = document.createElement('button');
      confirmButton.textContent = 'Run';
      confirmButton.className = 'sage-ai-confirm-button';

      buttonContainer.appendChild(cancelButton);
      buttonContainer.appendChild(confirmButton);

      this.confirmationContainer.appendChild(buttonContainer);

      // Add the confirmation container to the chat history
      this.chatHistory.appendChild(this.confirmationContainer);

      // Scroll to the bottom of the chat history
      this.chatHistory.scrollTop = this.chatHistory.scrollHeight;

      // Function to handle approval
      const approveExecution = () => {
        if (this.confirmationContainer) {
          this.chatHistory.removeChild(this.confirmationContainer);
          this.confirmationContainer = null;
        }
        this.messageComponent.addSystemMessage(
          'Cell execution approved by user.'
        );
        this.isShowing = false;
        resolve(true);
      };

      // Function to handle rejection
      const rejectExecution = () => {
        if (this.confirmationContainer) {
          this.chatHistory.removeChild(this.confirmationContainer);
          this.confirmationContainer = null;
        }
        this.messageComponent.addSystemMessage(
          '❌ Cell execution rejected by user.'
        );
        this.isShowing = false;
        resolve(false);
      };

      // Keyboard event handler for the entire document
      const keyboardHandler = (event: KeyboardEvent) => {
        // Check for Cmd+Enter (macOS) or Ctrl+Enter (Windows/Linux)
        if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) {
          event.preventDefault();
          approveExecution();
          // Clean up event listener
          document.removeEventListener('keydown', keyboardHandler);
        }
      };

      // Add keyboard event listener
      document.addEventListener('keydown', keyboardHandler);

      // Set up button event handlers
      confirmButton.addEventListener('click', () => {
        approveExecution();
        document.removeEventListener('keydown', keyboardHandler);
      });

      cancelButton.addEventListener('click', () => {
        rejectExecution();
        document.removeEventListener('keydown', keyboardHandler);
      });
    });
  }

  /**
   * Check if the confirmation dialog is currently showing
   */
  public isDialogShowing(): boolean {
    return this.isShowing;
  }
}
