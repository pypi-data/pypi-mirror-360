import { IChatMessage } from '../types';
import { ChatBoxWidget } from '../Components/chatbox';
import { MentionContext } from './ChatMentionDropdown';

export interface IChatThread {
  id: string;
  name: string;
  messages: IChatMessage[];
  lastUpdated: number;
  contexts: Map<string, MentionContext>;
  message_timestamps: Map<string, number>;
}

export interface NotebookChatState {
  chatbox: ChatBoxWidget | null;
  isVisible: boolean;
}

/**
 * Manager for persisting chat histories across notebook sessions
 */
export class ChatHistoryManager {
  // Map of notebook paths to their chat threads
  private notebookChats: Map<string, IChatThread[]> = new Map();
  // Current active notebook path
  private currentNotebookPath: string | null = null;
  // Current active chat thread ID
  private currentThreadId: string | null = null;
  // Storage key prefix
  private readonly STORAGE_KEY_PREFIX = 'sage-ai-chat-history-';
  // Map of notebook paths to their chatbox instances
  private notebookChatboxes: Map<string, NotebookChatState> = new Map();

  constructor() {
    this.loadFromStorage();
  }

  public updateNotebookPath(oldPath: string, newPath: string): void {
    this.currentNotebookPath = newPath;
    const threads = this.notebookChats.get(oldPath) || [];
    this.notebookChats.set(newPath, threads);
    this.notebookChats.delete(oldPath);
    this.saveToStorage();
  }

  /**
   * Set the current notebook path and load its chat history
   * @param notebookPath Path to the notebook
   * @returns The active chat thread for this notebook (creates one if none exists)
   */
  public setCurrentNotebook(notebookPath: string): IChatThread {
    console.log(
      `[ChatHistoryManager] Setting current notebook: ${notebookPath}`
    );

    // If we're switching notebooks, hide the previous one
    if (this.currentNotebookPath && this.currentNotebookPath !== notebookPath) {
      this.hideChatbox(this.currentNotebookPath);
    }

    this.currentNotebookPath = notebookPath;

    // Check if we have chat history for this notebook
    if (!this.notebookChats.has(notebookPath)) {
      // Create a default thread for this notebook
      const defaultThread: IChatThread = {
        id: this.generateThreadId(),
        name: 'Default Chat',
        messages: [],
        lastUpdated: Date.now(),
        contexts: new Map<string, MentionContext>(),
        message_timestamps: new Map<string, number>()
      };

      this.notebookChats.set(notebookPath, [defaultThread]);
      this.saveToStorage();
    }

    // Get all threads for this notebook
    const threads = this.notebookChats.get(notebookPath)!;

    // Sort threads by lastUpdated (most recent first)
    const sortedThreads = [...threads].sort(
      (a, b) => b.lastUpdated - a.lastUpdated
    );

    // Find the most recent "New Chat" thread if it exists
    const mostRecentNewChat = sortedThreads.find(
      thread => thread.name === 'New Chat'
    );

    // If there's a most recent "New Chat", use that as the active thread
    if (mostRecentNewChat) {
      this.currentThreadId = mostRecentNewChat.id;
    } else {
      // Otherwise set the current thread to the first thread
      this.currentThreadId = threads[0].id;
    }

    // Make sure this notebook's chatbox is visible
    this.showChatbox(notebookPath);

    // Return the current thread
    return this.getCurrentThread()!;
  }

  /**
   * Show the chatbox for a notebook
   * @param notebookPath Path to the notebook
   */
  public showChatbox(notebookPath: string): void {
    const state = this.notebookChatboxes.get(notebookPath);
    if (state && state.chatbox) {
      state.isVisible = true;

      // Update the DOM element visibility
      const node = state.chatbox.node;
      if (node) {
        node.style.display = '';
        node.classList.remove('hidden-chatbox');
      }
    }

    // Hide all other chatboxes
    this.notebookChatboxes.forEach((otherState, path) => {
      if (path !== notebookPath && otherState.chatbox) {
        otherState.isVisible = false;
        const node = otherState.chatbox.node;
        if (node) {
          node.style.display = 'none';
          node.classList.add('hidden-chatbox');
        }
      }
    });
  }

  /**
   * Hide the chatbox for a notebook
   * @param notebookPath Path to the notebook
   */
  public hideChatbox(notebookPath: string): void {
    const state = this.notebookChatboxes.get(notebookPath);
    if (state && state.chatbox) {
      state.isVisible = false;
      const node = state.chatbox.node;
      if (node) {
        node.style.display = 'none';
        node.classList.add('hidden-chatbox');
      }
    }
  }

  /**
   * Check if a notebook has a registered chatbox
   * @param notebookPath Path to the notebook
   * @returns True if the notebook has a chatbox
   */
  public hasChatbox(notebookPath: string): boolean {
    return (
      this.notebookChatboxes.has(notebookPath) &&
      !!this.notebookChatboxes.get(notebookPath)?.chatbox
    );
  }

  /**
   * Get the current active chat thread
   * @returns The current chat thread or null if no notebook is set
   */
  public getCurrentThread(): IChatThread | null {
    if (!this.currentNotebookPath || !this.currentThreadId) {
      return null;
    }

    const threads = this.notebookChats.get(this.currentNotebookPath);
    if (!threads) {
      return null;
    }

    return threads.find(thread => thread.id === this.currentThreadId) || null;
  }

  /**
   * Get all chat threads for the current notebook
   * @returns Array of chat threads or empty array if no notebook is set
   */
  public getCurrentNotebookThreads(): IChatThread[] {
    if (!this.currentNotebookPath) {
      return [];
    }

    return this.notebookChats.get(this.currentNotebookPath) || [];
  }

  /**
   * Get all chat threads for a specific notebook
   * @param notebookPath Path to the notebook
   * @returns Array of chat threads or null if notebook not found
   */
  public getThreadsForNotebook(notebookPath: string): IChatThread[] | null {
    if (!notebookPath || !this.notebookChats.has(notebookPath)) {
      return null;
    }

    return this.notebookChats.get(notebookPath) || [];
  }

  /**
   * Update the contexts in the current chat thread
   * @param contexts New contexts for the current thread
   */
  public updateCurrentThreadContexts(
    contexts: Map<string, MentionContext>
  ): void {
    if (!this.currentNotebookPath || !this.currentThreadId) {
      console.warn(
        '[ChatHistoryManager] Cannot update contexts: No active notebook or thread'
      );
      return;
    }

    const threads = this.notebookChats.get(this.currentNotebookPath);
    if (!threads) {
      console.warn(
        `[ChatHistoryManager] No threads found for notebook: ${this.currentNotebookPath}`
      );
      return;
    }

    const threadIndex = threads.findIndex(
      thread => thread.id === this.currentThreadId
    );
    if (threadIndex === -1) {
      console.warn(
        `[ChatHistoryManager] Thread with ID ${this.currentThreadId} not found`
      );
      return;
    }

    // Update the contexts
    threads[threadIndex].contexts = new Map(contexts);
    threads[threadIndex].lastUpdated = Date.now();

    // Save to storage
    this.saveToStorage();
  }

  /**
   * Update the messages in the current chat thread
   * @param messages New messages for the current thread
   * @param contexts Optional contexts for mentions in the messages
   */
  public updateCurrentThreadMessages(
    messages: IChatMessage[],
    contexts?: Map<string, MentionContext>
  ): void {
    if (!this.currentNotebookPath || !this.currentThreadId) {
      console.warn(
        '[ChatHistoryManager] Cannot update messages: No active notebook or thread'
      );
      return;
    }

    const threads = this.notebookChats.get(this.currentNotebookPath);
    if (!threads) {
      console.warn(
        `[ChatHistoryManager] No threads found for notebook: ${this.currentNotebookPath}`
      );
      return;
    }

    const threadIndex = threads.findIndex(
      thread => thread.id === this.currentThreadId
    );
    if (threadIndex === -1) {
      console.warn(
        `[ChatHistoryManager] Thread with ID ${this.currentThreadId} not found`
      );
      return;
    }

    try {
      for (const message of messages) {
        if (
          threads[threadIndex].message_timestamps?.has &&
          threads[threadIndex].message_timestamps?.has(JSON.stringify(message))
        ) {
          continue;
        }

        // Add timestamp for the message
        threads[threadIndex].message_timestamps.set(
          JSON.stringify(message),
          Date.now()
        );
        threads[threadIndex].message_timestamps;
      }
    } catch (error) {
      console.log(
        '[ChatHistoryManager] Error updating message timestamps for eval:',
        error
      );
      return;
    }

    // Update the messages and last updated time
    threads[threadIndex].messages = [
      ...threads[threadIndex].messages,
      ...messages
    ];
    threads[threadIndex].lastUpdated = Date.now();

    // Update contexts if provided
    if (contexts) {
      threads[threadIndex].contexts = new Map(contexts);
    }

    // Save to storage
    this.saveToStorage();
  }

  public static getCleanMessageArrayWithTimestamps(thread: IChatThread): any[] {
    // Return messages with timestamps
    return thread.messages.map(message => ({
      ...message,
      timestamp:
        thread.message_timestamps.get(JSON.stringify(message)) || Date.now()
    }));
  }

  /**
   * Clear the messages in the current chat thread
   */
  public clearCurrentThread(): void {
    this.updateCurrentThreadMessages([]);
  }

  /**
   * Get all notebook paths with chat histories
   * @returns Array of notebook paths
   */
  public getNotebookPaths(): string[] {
    return Array.from(this.notebookChats.keys());
  }

  /**
   * Save all chat histories to local storage
   */
  private saveToStorage(): void {
    try {
      // Convert Map to a serializable object
      const storageObj: Record<string, any[]> = {};

      for (const [notebookPath, threads] of this.notebookChats.entries()) {
        // Convert each thread's contexts Map to a serializable object
        const serializedThreads = threads.map(thread => ({
          ...thread,
          contexts: thread.contexts ? Object.fromEntries(thread.contexts) : {},
          message_timestamps: thread.message_timestamps
            ? Object.fromEntries(thread.message_timestamps)
            : {}
        }));
        storageObj[notebookPath] = serializedThreads;
      }

      localStorage.setItem(
        this.STORAGE_KEY_PREFIX + 'notebooks',
        JSON.stringify(storageObj)
      );

      console.log('[ChatHistoryManager] Saved chat histories to storage');
    } catch (error) {
      console.error(
        '[ChatHistoryManager] Error saving chat histories to storage:',
        error
      );
    }
  }

  /**
   * Load chat histories from local storage
   */
  private loadFromStorage(): void {
    try {
      const storedData = localStorage.getItem(
        this.STORAGE_KEY_PREFIX + 'notebooks'
      );

      if (storedData) {
        const parsedData: Record<string, any[]> = JSON.parse(storedData);

        // Convert object back to Map
        this.notebookChats = new Map();
        for (const [notebookPath, threads] of Object.entries(parsedData)) {
          // Migrate old storage format to new format with contexts
          const migratedThreads: IChatThread[] = threads.map(thread => ({
            ...thread,
            // Handle migration for threads that don't have contexts
            contexts: thread.contexts
              ? new Map<string, MentionContext>(Object.entries(thread.contexts))
              : new Map<string, MentionContext>(),
            message_timestamps: thread.message_timestamps
              ? new Map<string, number>(
                  Object.entries(thread.message_timestamps)
                )
              : new Map<string, number>()
          }));

          this.notebookChats.set(notebookPath, migratedThreads);
        }

        console.log('[ChatHistoryManager] Loaded chat histories from storage');
        console.log(
          `[ChatHistoryManager] Loaded ${this.notebookChats.size} notebook chat histories`
        );
      } else {
        console.log('[ChatHistoryManager] No stored chat histories found');
      }
    } catch (error) {
      console.error(
        '[ChatHistoryManager] Error loading chat histories from storage:',
        error
      );
      // Reset to empty state on error
      this.notebookChats = new Map();
    }
  }

  /**
   * Generate a unique ID for a new chat thread
   */
  private generateThreadId(): string {
    return (
      'thread-' + Date.now() + '-' + Math.random().toString(36).substring(2, 9)
    );
  }

  /**
   * Create a new chat thread for the current notebook
   * @param name Name of the new thread
   * @returns The newly created thread or null if no notebook is active
   */
  public createNewThread(name: string = 'New Chat'): IChatThread | null {
    if (!this.currentNotebookPath) {
      console.warn(
        '[ChatHistoryManager] Cannot create thread: No active notebook'
      );
      return null;
    }

    const newThread: IChatThread = {
      id: this.generateThreadId(),
      name,
      messages: [],
      lastUpdated: Date.now(),
      contexts: new Map<string, MentionContext>(),
      message_timestamps: new Map<string, number>()
    };

    const existingThreads =
      this.notebookChats.get(this.currentNotebookPath) || [];
    this.notebookChats.set(this.currentNotebookPath, [
      ...existingThreads,
      newThread
    ]);

    // Set the new thread as the current thread
    this.currentThreadId = newThread.id;

    // Save to storage
    this.saveToStorage();

    return newThread;
  }

  /**
   * Switch to a specific chat thread
   * @param threadId ID of the thread to switch to
   * @returns The thread that was switched to, or null if not found
   */
  public switchToThread(threadId: string): IChatThread | null {
    if (!this.currentNotebookPath) {
      return null;
    }

    const threads = this.notebookChats.get(this.currentNotebookPath);
    if (!threads) {
      return null;
    }

    const thread = threads.find(t => t.id === threadId);
    if (thread) {
      this.currentThreadId = threadId;
      return thread;
    }

    return null;
  }

  /**
   * Rename the current chat thread
   * @param newName New name for the current thread
   * @returns True if successful, false otherwise
   */
  public renameCurrentThread(newName: string): boolean {
    if (!this.currentNotebookPath || !this.currentThreadId) {
      console.warn(
        '[ChatHistoryManager] Cannot rename thread: No active notebook or thread'
      );
      return false;
    }

    const threads = this.notebookChats.get(this.currentNotebookPath);
    if (!threads) {
      console.warn(
        `[ChatHistoryManager] No threads found for notebook: ${this.currentNotebookPath}`
      );
      return false;
    }

    const threadIndex = threads.findIndex(
      thread => thread.id === this.currentThreadId
    );
    if (threadIndex === -1) {
      console.warn(
        `[ChatHistoryManager] Thread with ID ${this.currentThreadId} not found`
      );
      return false;
    }

    // Update the thread name
    threads[threadIndex].name = newName;

    // Save to storage
    this.saveToStorage();

    console.log(
      `[ChatHistoryManager] Renamed thread ${this.currentThreadId} to "${newName}"`
    );
    return true;
  }

  /**
   * Delete a chat thread
   * @param threadId ID of the thread to delete
   * @returns True if successful, false otherwise
   */
  public deleteThread(threadId: string): boolean {
    if (!this.currentNotebookPath) {
      console.warn(
        '[ChatHistoryManager] Cannot delete thread: No active notebook'
      );
      return false;
    }

    const threads = this.notebookChats.get(this.currentNotebookPath);
    if (!threads) {
      return false;
    }

    const threadIndex = threads.findIndex(thread => thread.id === threadId);
    if (threadIndex === -1) {
      return false;
    }

    // Remove the thread
    threads.splice(threadIndex, 1);

    // If we deleted the current thread, switch to first available thread
    if (threadId === this.currentThreadId) {
      if (threads.length > 0) {
        this.currentThreadId = threads[threads.length - 1].id;
      } else {
        // Create a new default thread if we deleted the last one
        const defaultThread: IChatThread = {
          id: this.generateThreadId(),
          name: 'Default Chat',
          messages: [],
          lastUpdated: Date.now(),
          contexts: new Map<string, MentionContext>(),
          message_timestamps: new Map<string, number>()
        };

        threads.push(defaultThread);
        this.currentThreadId = defaultThread.id;
      }
    }

    // Save to storage
    this.saveToStorage();

    console.log(`[ChatHistoryManager] Deleted thread ${threadId}`);
    return true;
  }

  /**
   * Clean up resources for a notebook (when closing)
   * @param notebookPath Path to the notebook
   */
  public cleanupNotebook(notebookPath: string): void {
    // Remove the chatbox reference but keep the chat history
    if (this.notebookChatboxes.has(notebookPath)) {
      this.notebookChatboxes.delete(notebookPath);
    }
  }

  /**
   * Get all registered notebook chatboxes
   * @returns Map of notebook paths to their chatbox states
   */
  public getAllChatboxes(): Map<string, NotebookChatState> {
    return this.notebookChatboxes;
  }
}
