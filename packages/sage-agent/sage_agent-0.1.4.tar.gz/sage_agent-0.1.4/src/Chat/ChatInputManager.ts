import { ChatHistoryManager } from './ChatHistoryManager';
import { ChatMentionDropdown, MentionContext } from './ChatMentionDropdown';
import { Contents } from '@jupyterlab/services';
import { ToolService } from '../Services/ToolService';
import { RichTextChatInput } from './RichTextChatInput';
import { IChatService } from '../Services/IChatService';
import { ConversationService } from './ConversationService';
import { ChatMessages } from './ChatMessages';
import { ChatUIHelper } from './ChatUIHelper';
import { ChatboxContext } from '../Components/ChatboxContext';
import { ChatRequestStatus } from '../types';
import { AppStateService } from '../AppState';

/**
 * Input element type that supports both textarea and rich text input
 */
type ChatInputElement = HTMLTextAreaElement | RichTextChatInput;

/**
 * Manages chat input functionality
 */
export class ChatInputManager {
  private chatInput: ChatInputElement;
  private chatHistoryManager: ChatHistoryManager;
  private userMessageHistory: string[] = [];
  private historyPosition: number = -1;
  private unsavedInput: string = '';
  private mentionDropdown: ChatMentionDropdown;

  // Add map to track all currently active mentions by context.id
  private activeContexts: Map<string, MentionContext> = new Map();

  private onContextSelected: ((context: MentionContext) => void) | null = null;
  private onContextRemoved: ((context_id: string) => void) | null = null;
  private onResetChat: (() => void) | null = null;

  // Dependencies for sendMessage and revertAndSend
  private chatService?: IChatService;
  private conversationService?: ConversationService;
  private messageComponent?: ChatMessages;
  private uiHelper?: ChatUIHelper;
  private contextHandler?: ChatboxContext;
  private sendButton?: HTMLButtonElement;
  private modeSelector?: HTMLElement;
  private modeName: 'agent' | 'ask' | 'fast' = 'agent';
  private isProcessingMessage: boolean = false;
  private updateUndoButtonState?: () => void;
  private cancelMessage?: () => void;
  private onMessageSent?: () => void;

  constructor(
    chatInput: ChatInputElement,
    chatHistoryManager: ChatHistoryManager,
    inputContainer: HTMLElement,
    contentManager: Contents.IManager,
    toolService: ToolService,
    onContextSelected?: (context: MentionContext) => void,
    onContextRemoved?: (context_id: string) => void,
    onResetChat?: () => void
  ) {
    this.chatInput = chatInput;
    this.chatHistoryManager = chatHistoryManager;
    this.onContextSelected = onContextSelected || null;
    this.onContextRemoved = onContextRemoved || null;
    this.onResetChat = onResetChat || null;

    // Initialize the mention dropdown
    const inputElement = this.isRichTextInput(chatInput)
      ? chatInput.getInputElement()
      : chatInput;
    this.mentionDropdown = new ChatMentionDropdown(
      inputElement as HTMLElement, // Changed to HTMLElement
      inputContainer,
      contentManager,
      toolService
    );

    // Set up event handlers for textarea
    this.setupEventHandlers();

    // Load user message history
    this.loadUserMessageHistory();

    // Set up the context selection callback for the mention dropdown
    this.mentionDropdown.setContextSelectedCallback(
      (context: MentionContext) => {
        // Store the context when selected
        this.activeContexts.set(context.id, context);

        // Update rich text input contexts if applicable
        if (this.isRichTextInput(this.chatInput)) {
          this.chatInput.setActiveContexts(this.activeContexts);
        }

        if (this.onContextSelected) {
          this.onContextSelected(context);
        }
      }
    );
  }

  /**
   * Set up event handlers for textarea
   */
  private setupEventHandlers(): void {
    const inputElement = this.isRichTextInput(this.chatInput)
      ? this.chatInput.getInputElement()
      : this.chatInput;

    // Auto-resize the textarea as content grows
    inputElement.addEventListener('input', () => {
      this.resizeTextarea();

      // Detect any contexts that were removed
      // this.detectDeletedContexts();
    });

    // Handle keydown events for submission and special key combinations
    inputElement.addEventListener('keydown', (event: Event) => {
      const keyEvent = event as KeyboardEvent;
      // Message history navigation with arrow keys
      if (keyEvent.key === 'ArrowUp') {
        // Only navigate history if cursor is at the beginning of the text or input is empty
        if (this.getSelectionStart() === 0 || this.getInputValue() === '') {
          keyEvent.preventDefault();
          this.navigateHistory('up');
        }
      } else if (keyEvent.key === 'ArrowDown') {
        // Only navigate history if cursor is at the end of the text or input is empty
        if (
          this.getSelectionStart() === this.getInputLength() ||
          this.getInputValue() === ''
        ) {
          keyEvent.preventDefault();
          this.navigateHistory('down');
        }
      }
    });
  }

  /**
   * Load the user's message history from all chat threads
   */
  public loadUserMessageHistory(): void {
    this.userMessageHistory = [];

    // Iterate through all notebooks
    const notebookPaths = this.chatHistoryManager.getNotebookPaths();
    for (const notebookPath of notebookPaths) {
      // Get all threads for this notebook
      const threads =
        this.chatHistoryManager.getThreadsForNotebook(notebookPath);
      if (!threads) continue;

      // Extract user messages from each thread
      for (const thread of threads) {
        const userMessages = thread.messages
          .filter(msg => msg.role === 'user' && typeof msg.content === 'string')
          .map(msg => (typeof msg.content === 'string' ? msg.content : ''));

        // Add non-empty messages to history
        userMessages.forEach(msg => {
          if (msg && !this.userMessageHistory.includes(msg)) {
            this.userMessageHistory.push(msg);
          }
        });
      }
    }

    // Reset the position to start at the most recent message
    this.historyPosition = -1;
    this.unsavedInput = '';

    // Sort the history so the most recently used messages are at the end
    // This makes arrow-key navigation more intuitive
    this.userMessageHistory.sort((a, b) => {
      // Keep shorter messages (which tend to be more general/reusable) at the end
      if (a.length !== b.length) {
        return a.length - b.length;
      }
      return a.localeCompare(b);
    });

    console.log(
      `[ChatInputManager] Loaded ${this.userMessageHistory.length} user messages for history navigation`
    );
  }

  /**
   * Navigate through user message history
   * @param direction 'up' for older messages, 'down' for newer messages
   */
  public navigateHistory(direction: 'up' | 'down'): void {
    // If no history, nothing to do
    if (this.userMessageHistory.length === 0) {
      return;
    }

    // Save current input if this is the first navigation action
    if (this.historyPosition === -1) {
      this.unsavedInput = this.getInputValue();
    }

    if (direction === 'up') {
      // Navigate to previous message (older)
      if (this.historyPosition < this.userMessageHistory.length - 1) {
        this.historyPosition++;
        const historyMessage =
          this.userMessageHistory[
            this.userMessageHistory.length - 1 - this.historyPosition
          ];
        this.setInputValue(historyMessage);
        // Place cursor at end of text
        const length = historyMessage.length;
        this.setSelectionRange(length, length);
      }
    } else {
      // Navigate to next message (newer)
      if (this.historyPosition > 0) {
        this.historyPosition--;
        const historyMessage =
          this.userMessageHistory[
            this.userMessageHistory.length - 1 - this.historyPosition
          ];
        this.setInputValue(historyMessage);
        // Place cursor at end of text
        const length = historyMessage.length;
        this.setSelectionRange(length, length);
      } else if (this.historyPosition === 0) {
        // Restore the unsaved input when reaching the bottom of history
        this.historyPosition = -1;
        this.setInputValue(this.unsavedInput);
        // Place cursor at end of text
        const length = this.unsavedInput.length;
        this.setSelectionRange(length, length);
      }
    }

    // Resize the textarea to fit the content
    this.resizeTextarea();
  }
  /**
   * Resize the textarea based on its content
   */
  public resizeTextarea(): void {
    if (this.isRichTextInput(this.chatInput)) {
      // Reset height to auto to get the correct scrollHeight
      this.chatInput.setHeight('auto');
      // Set the height to match the content (with a max height)
      const maxHeight = 150; // Maximum height in pixels
      const scrollHeight = this.chatInput.getScrollHeight();
      if (scrollHeight <= maxHeight) {
        this.chatInput.setHeight(scrollHeight + 'px');
        this.chatInput.setOverflowY('hidden');
      } else {
        this.chatInput.setHeight(maxHeight + 'px');
        this.chatInput.setOverflowY('auto');
      }
    } else {
      // Reset height to auto to get the correct scrollHeight
      this.chatInput.style.height = 'auto';
      // Set the height to match the content (with a max height)
      const maxHeight = 150; // Maximum height in pixels
      const scrollHeight = this.chatInput.scrollHeight;
      if (scrollHeight <= maxHeight) {
        this.chatInput.style.height = scrollHeight + 'px';
        this.chatInput.style.overflowY = 'hidden';
      } else {
        this.chatInput.style.height = maxHeight + 'px';
        this.chatInput.style.overflowY = 'auto';
      }
    }
  }

  /**
   * Set the value for either input type
   */
  public setInputValue(value: string): void {
    if (this.isRichTextInput(this.chatInput)) {
      this.chatInput.setPlainText(value);
    } else {
      this.chatInput.value = value;
    }

    // Trigger input event to detect removed contexts
    // this.detectDeletedContexts();
  }

  /**
   * Get the plain text value from either input type
   */
  private getInputValue(): string {
    if (this.isRichTextInput(this.chatInput)) {
      return this.chatInput.getPlainText().trim();
    } else {
      return this.chatInput.value.trim();
    }
  }

  /**
   * Check if the input is a RichTextChatInput
   */
  private isRichTextInput(input: ChatInputElement): input is RichTextChatInput {
    return input instanceof RichTextChatInput;
  }

  /**
   * Get selection start position for either input type
   */
  private getSelectionStart(): number {
    if (this.isRichTextInput(this.chatInput)) {
      return this.chatInput.getSelectionStart();
    } else {
      return this.chatInput.selectionStart || 0;
    }
  }

  /**
   * Set selection range for either input type
   */
  private setSelectionRange(start: number, end: number): void {
    if (this.isRichTextInput(this.chatInput)) {
      this.chatInput.setSelectionRange(start, end);
    } else {
      this.chatInput.selectionStart = start;
      this.chatInput.selectionEnd = end;
    }
  }

  /**
   * Get the current input text length
   */
  private getInputLength(): number {
    return this.getInputValue().length;
  }

  /**
   * Clear the input
   */
  public clearInput(): void {
    if (this.isRichTextInput(this.chatInput)) {
      this.chatInput.clear();
    } else {
      this.chatInput.value = '';
      this.chatInput.style.height = 'auto'; // Reset height after clearing
    }
    this.focus();
  }

  /**
   * Add a message to history
   */
  public addToHistory(message: string): void {
    if (!this.userMessageHistory.includes(message)) {
      this.userMessageHistory.push(message);
    }

    // Reset history navigation
    this.historyPosition = -1;
    this.unsavedInput = '';
  }

  /**
   * Focus the input
   */
  public focus(): void {
    if (this.isRichTextInput(this.chatInput)) {
      this.chatInput.focus();
    } else {
      this.chatInput.focus();
    }
  }

  /**
   * Get the current input value (public method)
   */
  public getCurrentInputValue(): string {
    return this.getInputValue();
  }

  /**
   * Set the dependencies needed for sendMessage and revertAndSend functionality
   */
  public setDependencies(dependencies: {
    chatService: IChatService;
    conversationService: ConversationService;
    messageComponent: ChatMessages;
    uiHelper: ChatUIHelper;
    contextHandler: ChatboxContext;
    sendButton: HTMLButtonElement;
    modeSelector: HTMLElement;
    updateUndoButtonState: () => void;
    cancelMessage: () => void;
    onMessageSent?: () => void;
  }): void {
    this.chatService = dependencies.chatService;
    this.conversationService = dependencies.conversationService;
    this.messageComponent = dependencies.messageComponent;
    this.uiHelper = dependencies.uiHelper;
    this.contextHandler = dependencies.contextHandler;
    this.sendButton = dependencies.sendButton;
    this.modeSelector = dependencies.modeSelector;
    this.updateUndoButtonState = dependencies.updateUndoButtonState;
    this.cancelMessage = dependencies.cancelMessage;
    this.onMessageSent = dependencies.onMessageSent;
  }

  /**
   * Set the mode name
   */
  public setModeName(modeName: 'agent' | 'ask' | 'fast'): void {
    this.modeName = modeName;
  }

  /**
   * Get the current processing state
   */
  public getIsProcessingMessage(): boolean {
    return this.isProcessingMessage;
  }

  /**
   * Set the processing state
   */
  public setIsProcessingMessage(value: boolean): void {
    this.isProcessingMessage = value;
  }

  /**
   * Send a message to the AI service
   */
  public async sendMessage(cell_context?: string): Promise<void> {
    // Check if dependencies are set
    if (
      !this.chatService ||
      !this.conversationService ||
      !this.messageComponent ||
      !this.uiHelper ||
      !this.contextHandler ||
      !this.sendButton ||
      !this.modeSelector
    ) {
      console.error(
        'ChatInputManager dependencies not set. Call setDependencies() first.'
      );
      return;
    }

    const userInput = this.getCurrentInputValue();
    if (!userInput || this.isProcessingMessage) {
      return;
    }

    // Hide the waiting reply box when user sends a message
    AppStateService.getWaitingUserReplyBoxManager().hide();

    // Special command to reset the chat
    if (userInput.toLowerCase() === 'reset') {
      // We'll need to add a callback for this
      if (this.onResetChat) {
        this.onResetChat();
      }
      this.clearInput();
      return;
    }

    // Add message to history navigation
    this.addToHistory(userInput);

    // Notify that a message is being sent (triggers switch to history widget)
    if (this.onMessageSent) {
      this.onMessageSent();
    }

    // Set processing state
    this.isProcessingMessage = true;
    this.uiHelper.updateSendButton(this.sendButton, true);
    AppStateService.getPlanStateDisplay().setLoading(true);
    this.uiHelper.updateAgentModeElement(this.modeSelector, true);

    // Reset LLM state display to generating state, clearing any diff state
    this.uiHelper.resetToGeneratingState('Generating...');

    // Clear the input
    this.clearInput();

    // Check if the chat client has been properly initialized
    if (!this.chatService.isInitialized()) {
      this.messageComponent.addSystemMessage(
        '❌ API key is not set. Please configure it in the settings.'
      );
      this.isProcessingMessage = false;
      this.uiHelper.updateSendButton(this.sendButton, false);
      AppStateService.getPlanStateDisplay().setLoading(false);
      this.uiHelper.updateAgentModeElement(this.modeSelector, false);
      return;
    }

    // Display the user message in the UI
    this.messageComponent.addUserMessage(userInput);

    // Initialize messages with the user query
    const newUserMessage = { role: 'user', content: userInput };

    try {
      // Make sure the conversation service knows which notebook we're targeting
      const currentNotebookPath =
        AppStateService.getState().currentNotebookPath;
      if (currentNotebookPath) {
        this.conversationService.setNotebookPath(currentNotebookPath);
      }

      const system_messages: string[] = [];

      const messages = [newUserMessage];
      if (cell_context) {
        system_messages.push(cell_context);
      }
      const mentionContexts = this.messageComponent.getMentionContexts();
      if (mentionContexts.size > 0) {
        system_messages.push(this.contextHandler.getCurrentContextMessage());
      }

      // Proceed with sending the message
      await this.conversationService.processConversation(
        messages,
        system_messages,
        this.modeName
      );
    } catch (error) {
      console.error('Error in conversation processing:', error);

      // Only show error if we're not cancelled
      if (this.chatService.getRequestStatus() !== ChatRequestStatus.CANCELLED) {
        this.messageComponent.addErrorMessage(
          `❌ ${error instanceof Error ? error.message : 'An error occurred while communicating with the AI service.'}`
        );
      }
    } finally {
      // Reset state
      this.isProcessingMessage = false;
      this.uiHelper.updateSendButton(this.sendButton, false);
      AppStateService.getPlanStateDisplay().setLoading(false);
      this.uiHelper.updateAgentModeElement(this.modeSelector, false);
    }
  }
}
