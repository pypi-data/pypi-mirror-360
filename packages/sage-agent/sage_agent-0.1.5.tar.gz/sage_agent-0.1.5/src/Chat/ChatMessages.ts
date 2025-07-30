import { NotebookTools } from '../Notebook/NotebookTools';
import { ToolCall } from '../Services/ToolService';
import { IChatMessage, IToolCall } from '../types';
import { ChatHistoryManager, IChatThread } from './ChatHistoryManager';
// Add import for markdown rendering
import { marked } from 'marked';
import { MentionContext } from './ChatMentionDropdown';
import {
  getToolDisplayMessage,
  getToolIcon,
  COPY_ICON,
  COPIED_ICON,
  STAR_ICON,
  toolCallIcons,
  toolCallMessages
} from '../utils/toolDisplay';

/**
 * Component for handling chat message display
 */
export class ChatMessages {
  private container: HTMLDivElement;
  private messageHistory: Array<IChatMessage> = [];
  private userMessages: Array<IChatMessage> = []; // Store original user inputs only
  private lastAddedMessageType: 'tool' | 'normal' | 'user' | null = null;
  private historyManager: ChatHistoryManager;
  private notebookTools: NotebookTools;
  private mentionContexts: Map<string, MentionContext> = new Map();

  constructor(
    container: HTMLDivElement,
    historyManager: ChatHistoryManager,
    notebookTools: NotebookTools
  ) {
    this.container = container;
    this.historyManager = historyManager;
    this.notebookTools = notebookTools;
    console.log('[ChatMessages] Initialized with empty message history');
  }

  /**
   * Load messages from an existing chat thread
   * @param thread The chat thread to load
   */
  loadFromThread(thread: IChatThread): void {
    // First clear the UI display
    this.container.innerHTML = '';

    // Set the messageHistory from the thread
    this.messageHistory = [...thread.messages];

    // Extract user messages for context reset situations
    this.userMessages = thread.messages.filter(msg => msg.role === 'user');

    // Load mention contexts from the thread
    this.mentionContexts = new Map(thread.contexts || new Map());

    this.lastAddedMessageType = null;

    // Render all messages to the UI
    this.renderAllMessages();

    console.log(
      `[ChatMessages] Loaded ${thread.messages.length} messages from thread`
    );
  }

  /**
   * Render all messages from the history to the UI
   */
  private async renderAllMessages(): Promise<void> {
    // Keep track of consecutive message types to group tools
    let lastToolGroup: { assistant: any; results: any[] } | null = null;

    for (const message of this.messageHistory) {
      if (message.role === 'user') {
        // Check if this is a tool result
        if (
          Array.isArray(message.content) &&
          message.content.length > 0 &&
          typeof message.content[0] === 'object' &&
          message.content[0].type === 'tool_result'
        ) {
          // This is a tool result - add it to the current tool group
          if (lastToolGroup) {
            // Render the tool result to UI
            this.renderToolResult(
              message.content[0].tool_name || 'tool',
              message.content[0].content,
              lastToolGroup
            );
            lastToolGroup.results.push(message.content[0]);
          }
        } else {
          // Regular user message
          lastToolGroup = null;
          this.renderUserMessage(
            typeof message.content === 'string'
              ? message.content
              : JSON.stringify(message.content)
          );
        }
      } else if (message.role === 'assistant') {
        // Check if this is a tool call
        if (
          Array.isArray(message.content) &&
          message.content.length > 0 &&
          typeof message.content[0] === 'object' &&
          message.content[0].type === 'tool_use'
        ) {
          // This is the start of a new tool group
          lastToolGroup = {
            assistant: message,
            results: []
          };

          // Render each tool call to UI
          for (const content of message.content) {
            if (content.type === 'tool_use') {
              this.renderToolCall(content);
            }
          }
        } else {
          // Regular assistant message
          lastToolGroup = null;
          await this.renderAssistantMessage(
            typeof message.content === 'string'
              ? message.content
              : Array.isArray(message.content) &&
                  typeof message.content[0] === 'object' &&
                  message.content[0].text
                ? message.content[0].text
                : JSON.stringify(message.content)
          );
        }
      }
    }

    this.removeLoadingText();
  }

  /**
   * Remove the tool loading text
   */
  public removeLoadingText(): void {
    this.container
      .querySelectorAll('.sage-ai-loading-text')
      .forEach(content => {
        content.classList.remove('sage-ai-loading-text');
      });
  }

  /**
   * Safely render markdown content with sanitization
   */
  private async renderMarkdown(text: string): Promise<string> {
    try {
      // Set options to ensure safe rendering with sanitization
      marked.setOptions({
        gfm: true, // GitHub flavored markdown
        breaks: false // Convert line breaks to <br>
      });

      // Sanitize the HTML output from marked
      return await marked.parse(text);
    } catch (error) {
      console.error('Error rendering markdown:', error);
      // Fall back to plain text if rendering fails
      return this.escapeHtml(text);
    }
  }

  /**
   * Escape HTML special characters to prevent XSS when fallback is needed
   */
  private escapeHtml(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  /**
   * Render a user message to the UI (without adding to history)
   */
  private renderUserMessage(message: string): void {
    this.closeToolGroupIfOpen();

    const messageElement = document.createElement('div');
    messageElement.className = 'sage-ai-message sage-ai-user-message';

    // Create a container for the message content
    const contentElement = document.createElement('div');
    contentElement.className = 'sage-ai-message-content';
    // Only escape HTML for user messages - generally don't need markdown
    contentElement.innerHTML = this.escapeHtml(message);

    messageElement.append(contentElement);

    this.container.appendChild(messageElement);

    this.lastAddedMessageType = 'user';
  }

  /**
   * Render an assistant message to the UI (without adding to history)
   */
  private async renderAssistantMessage(
    message: string,
    _container?: HTMLElement
  ): Promise<void> {
    this.closeToolGroupIfOpen();

    const messageElement = document.createElement('div');
    messageElement.className = 'sage-ai-message sage-ai-ai-message';

    // Create a container for the message header
    const headerElement = document.createElement('div');
    headerElement.className = 'sage-ai-message-header';

    // Create header image element
    const headerImageElement = document.createElement('div');
    headerImageElement.className = 'sage-ai-message-header-image';

    headerElement.append(headerImageElement);

    // Create header title element
    const headerSageTitleElement = document.createElement('span');
    headerSageTitleElement.className = 'sage-ai-message-header-title';
    headerSageTitleElement.innerText = 'Sage';

    headerElement.append(headerSageTitleElement);

    if (this.lastAddedMessageType !== 'user') {
      headerElement.style.display = 'none';
    }

    // Create a container for the message content
    const contentElement = document.createElement('div');
    contentElement.className =
      'sage-ai-message-content sage-ai-markdown-content';
    // Render markdown for AI responses
    contentElement.innerHTML = await this.renderMarkdown(message);

    // Assemble the message
    messageElement.appendChild(headerElement);
    messageElement.appendChild(contentElement);

    const container: HTMLElement = _container ?? this.container;
    container.appendChild(messageElement);
    this.lastAddedMessageType = 'normal';

    // Activate any code blocks in the message
    this.activateCodeBlocks(contentElement);
  }

  /**
   * Activate code blocks with syntax highlighting and copy buttons
   */
  private activateCodeBlocks(container: HTMLElement): void {
    // Find all code blocks
    const codeBlocks = container.querySelectorAll('pre code');

    codeBlocks.forEach(codeBlock => {
      // Create a container for the code block with a copy button
      const codeContainer = document.createElement('div');
      codeContainer.className = 'sage-ai-code-block-container';

      // Create copy button
      const copyButton = document.createElement('button');
      copyButton.className = 'sage-ai-copy-code-button';
      copyButton.innerHTML = COPY_ICON;
      copyButton.title = 'Copy code to clipboard';

      // Add click handler to copy button
      copyButton.addEventListener('click', () => {
        const code = codeBlock.textContent || '';
        navigator.clipboard
          .writeText(code)
          .then(() => {
            copyButton.innerHTML = COPIED_ICON;
            setTimeout(() => {
              copyButton.innerHTML = COPY_ICON;
            }, 2000);
          })
          .catch(err => {
            console.error('Failed to copy code: ', err);
            copyButton.innerHTML = 'Error';
            setTimeout(() => {
              copyButton.innerHTML = COPY_ICON;
            }, 2000);
          });
      });

      // Wrap the original code block
      const preElement = codeBlock.parentElement;
      if (preElement && preElement.tagName === 'PRE') {
        // Insert the code block and copy button into the container
        preElement.parentNode?.insertBefore(codeContainer, preElement);
        codeContainer.appendChild(preElement);
        codeContainer.appendChild(copyButton);
      }
    });
  }

  /**
   * Get the current mention contexts
   * @returns Map of mention contexts
   */
  public getMentionContexts(): Map<string, MentionContext> {
    return new Map(this.mentionContexts);
  }

  /**
   * Set mention contexts
   * @param contexts Map of mention contexts to set
   */
  public setMentionContexts(contexts: Map<string, MentionContext>): void {
    this.mentionContexts = new Map(contexts);
  }

  /**
   * Add a mention context
   * @param context The mention context to add
   */
  public addMentionContext(context: MentionContext): void {
    this.mentionContexts.set(context.id, context);
    // Update the persistent storage
    this.historyManager.updateCurrentThreadContexts(this.mentionContexts);
  }

  /**
   * Remove a mention context
   * @param contextId The ID of the context to remove
   */
  public removeMentionContext(contextId: string): void {
    this.mentionContexts.delete(contextId);
    // Update the persistent storage
    this.historyManager.updateCurrentThreadContexts(this.mentionContexts);
  }

  /**
   * Add a user message to the chat history
   */
  addUserMessage(message: string): void {
    this.closeToolGroupIfOpen();

    console.log('[ChatMessages] Adding user message:', message);
    const messageElement = document.createElement('div');
    messageElement.className = 'sage-ai-message sage-ai-user-message';

    // Create a container for the message content
    const contentElement = document.createElement('div');
    contentElement.className = 'sage-ai-message-content';
    // Only escape HTML for user messages - generally don't need markdown
    contentElement.innerHTML = this.escapeHtml(message);

    messageElement.append(contentElement);

    this.container.appendChild(messageElement);
    this.scrollToBottom();

    // Add to message history for context
    const userMessage = { role: 'user', content: message };
    this.messageHistory.push(userMessage);
    // Also store in userMessages for context reset situations
    this.userMessages.push({ role: 'user', content: message });

    // Update the persistent storage with contexts
    this.historyManager.updateCurrentThreadMessages(
      this.messageHistory,
      this.mentionContexts
    );

    this.lastAddedMessageType = 'user';

    console.log('[ChatMessages] User message added to history');
    console.log(
      '[ChatMessages] Current message history:',
      JSON.stringify(this.messageHistory)
    );
    console.log(
      '[ChatMessages] Current user messages:',
      JSON.stringify(this.userMessages)
    );
  }

  /**
   * Add a system message to the chat history
   */
  addSystemMessage(message: string): void {
    this.closeToolGroupIfOpen();

    console.log('[ChatMessages] Adding system message:', message);
    const messageElement = document.createElement('div');
    messageElement.className = 'sage-ai-message sage-ai-system-message';

    const textElement = document.createElement('p');
    textElement.className = 'sage-ai-system-message-text';
    textElement.innerHTML = message;
    messageElement.appendChild(textElement);
    this.container.appendChild(messageElement);
    this.scrollToBottom();

    this.lastAddedMessageType = 'normal';

    console.log('[ChatMessages] System message added (not saved to history)');
    // System messages are not saved to history
  }

  /**
   * Add an error message to the chat history
   */
  addErrorMessage(message: string): void {
    this.closeToolGroupIfOpen();

    console.log('[ChatMessages] Adding error message:', message);
    const messageElement = document.createElement('div');
    messageElement.className = 'sage-ai-message sage-ai-error-message';
    messageElement.textContent = message;
    this.container.appendChild(messageElement);
    this.scrollToBottom();

    this.lastAddedMessageType = 'normal';

    console.log('[ChatMessages] Error message added (not saved to history)');
    // Error messages are not saved to history
  }

  /**
   * Close the current tool group if one is open
   */
  private closeToolGroupIfOpen(): void {
    if (this.lastAddedMessageType === 'tool') {
      this.lastAddedMessageType = null;
    }
  }

  /**
   * Render a single tool call
   */
  private renderToolCall(toolCall: IToolCall): void {
    if (toolCall.name === 'notebook-wait_user_reply') {
      return;
    }

    console.log('[ChatMessages] Rendering tool call:', toolCall.name);
    console.log(
      '[ChatMessages] Tool call input:',
      JSON.stringify(toolCall.input)
    );

    const container = document.createElement('div');
    container.classList.add('sage-ai-tool-call-v1');
    container.setAttribute('sage-ai-tool-call-name', toolCall.name);

    // Add the SVG icon
    const iconElement = document.createElement('div');
    iconElement.innerHTML = getToolIcon(toolCall.name);
    container.appendChild(iconElement.firstChild!);

    // Add the text
    const textElement = document.createElement('span');
    textElement.innerHTML = getToolDisplayMessage(
      toolCall.name,
      toolCall.input
    );
    textElement.className = 'sage-ai-loading-text';
    container.appendChild(textElement);

    this.upsertCellIdLabelInDOM(container, toolCall.name, toolCall.input);

    // Append to the container and scroll
    this.container.appendChild(container);
    this.scrollToBottom();

    this.lastAddedMessageType = 'tool'; // Mark as tool interaction
  }

  /**
   * Add tool calls to the chat history
   */
  addToolCalls(toolCalls: IToolCall[]): void {
    if (!toolCalls || toolCalls.length === 0) {
      console.log('[ChatMessages] No tool calls to add');
      return;
    }

    console.log('[ChatMessages] Adding tool calls:', toolCalls.length);

    // Add each tool call to history and render
    toolCalls.forEach((toolCall, index) => {
      console.log(
        `[ChatMessages] Processing tool call #${index + 1}:`,
        toolCall.name
      );
      this.renderToolCall(toolCall);

      // Add to message history
      const toolCallMessage = {
        role: 'assistant',
        content: [
          {
            type: 'tool_use',
            id: toolCall.id,
            name: toolCall.name,
            input: toolCall.input
          }
        ]
      };

      this.messageHistory.push(toolCallMessage);

      // Update the persistent storage with contexts
      this.historyManager.updateCurrentThreadMessages(
        this.messageHistory,
        this.mentionContexts
      );

      console.log(`[ChatMessages] Tool call #${index + 1} added to history`);
    });

    console.log(
      '[ChatMessages] All tool calls added, current history length:',
      this.messageHistory.length
    );
    console.log(
      '[ChatMessages] Last message in history:',
      JSON.stringify(this.messageHistory[this.messageHistory.length - 1])
    );
  }

  /**
   * Add a streaming tool call container to the chat history
   * @returns The container element to be updated with streaming tool call content
   */
  addStreamingToolCall(): HTMLDivElement {
    this.closeToolGroupIfOpen();

    console.log('[ChatMessages] Adding streaming tool call container');

    // Remove any existing streaming cursor from text streaming
    const existingCursor = this.container.querySelector(
      '.sage-ai-streaming-cursor'
    );
    if (existingCursor) {
      existingCursor.remove();
    }

    // Create a container for the streaming tool call
    const toolCallContainer = document.createElement('div');
    toolCallContainer.className =
      'sage-ai-tool-call-v1 sage-ai-streaming-tool-call';
    toolCallContainer.setAttribute('data-tool-call', '{}'); // Store single tool call

    // Add a placeholder for the tool call content
    const toolCallPlaceholder = document.createElement('div');
    toolCallPlaceholder.className = 'sage-ai-streaming-tool-call-placeholder';
    toolCallPlaceholder.innerHTML = 'Sage is thinking about tools to use...';

    // Add a streaming cursor to the tool call
    const cursor = document.createElement('span');
    cursor.classList.add('sage-ai-streaming-cursor');
    toolCallPlaceholder.appendChild(cursor);

    toolCallContainer.appendChild(toolCallPlaceholder);

    this.container.appendChild(toolCallContainer);
    this.scrollToBottom();

    console.log(
      '[ChatMessages] Streaming tool call container added (not yet in history)'
    );

    return toolCallContainer;
  }

  /**
   * Update a streaming tool call with new tool call information
   * @param toolCallContainer The tool call container to update
   * @param toolUse The tool use information to add or update
   */
  updateStreamingToolCall(
    toolCallContainer: HTMLDivElement,
    toolUse: any
  ): void {
    console.log(
      '[ChatMessages] Updating streaming tool call with:',
      toolUse.name
    );

    if (toolCallContainer) {
      // Remove placeholder if it exists
      const placeholder = toolCallContainer.querySelector(
        '.sage-ai-streaming-tool-call-placeholder'
      );
      if (placeholder) {
        placeholder.remove();
      }

      // Update the tool call data
      toolCallContainer.setAttribute('data-tool-call', JSON.stringify(toolUse));
      toolCallContainer.setAttribute('sage-ai-tool-call-name', toolUse.name);

      // Only add icon if it doesn't exist yet
      let iconElement = toolCallContainer.querySelector(
        '.sage-ai-tool-call-icon'
      );
      if (!iconElement) {
        iconElement = document.createElement('div');
        iconElement.className = 'sage-ai-tool-call-icon';
        iconElement.innerHTML = getToolIcon(toolUse.name);
        toolCallContainer.appendChild(iconElement);
      }

      // Update text element if it exists, or create it if it doesn't
      let textElement = toolCallContainer.querySelector(
        '.sage-ai-loading-text'
      );
      const newText = getToolDisplayMessage(toolUse.name, toolUse.input);

      if (textElement) {
        // Only update if text has changed
        if (textElement.innerHTML !== newText) {
          textElement.innerHTML = newText;
        }
      } else {
        // Create text element if it doesn't exist
        textElement = document.createElement('span');
        textElement.innerHTML = newText;
        textElement.className = 'sage-ai-loading-text';
        toolCallContainer.appendChild(textElement);
      }

      this.upsertCellIdLabelInDOM(
        toolCallContainer,
        toolUse.name,
        toolUse.input
      );

      this.container.scrollTop = this.container.scrollHeight;

      console.log('[ChatMessages] Streaming tool call updated');
    } else {
      console.warn(
        '[ChatMessages] Warning: Tool call container not found in streaming message element'
      );
    }
  }

  /**
   * Finalize a streaming tool call, saving it to history
   * @param toolCallContainer The tool call container to finalize
   */
  finalizeStreamingToolCall(toolCallContainer: HTMLDivElement): void {
    console.log('[ChatMessages] Finalizing streaming tool call');

    // Remove the streaming cursor first
    const cursor = toolCallContainer.querySelector('.sage-ai-streaming-cursor');
    if (cursor) {
      cursor.remove();
    }

    const textLoadingElement = toolCallContainer.querySelector(
      '.sage-ai-loading-text'
    );
    if (textLoadingElement) {
      textLoadingElement.classList.remove('sage-ai-loading-text');
    }

    // Get the tool call data
    const toolCallStr =
      toolCallContainer.getAttribute('data-tool-call') || '{}';
    const toolCall = JSON.parse(toolCallStr);

    console.log('[ChatMessages] Finalized tool call:', toolCall.name);

    if (toolCall.name) {
      // Now that streaming is complete, render the definitive tool call properly
      this.renderToolCall(toolCall);

      // Remove the streaming tool call element
      toolCallContainer.remove();

      this.scrollToBottom();

      // Add to message history
      const toolCallMessage = {
        role: 'assistant',
        content: [
          {
            type: 'tool_use',
            id: toolCall.id,
            name: toolCall.name,
            input: toolCall.input
          }
        ]
      };

      this.messageHistory.push(toolCallMessage);

      // Update the persistent storage with contexts
      this.historyManager.updateCurrentThreadMessages(
        this.messageHistory,
        this.mentionContexts
      );

      console.log('[ChatMessages] Finalized tool call added to history');
      console.log(
        '[ChatMessages] Current history length:',
        this.messageHistory.length
      );
    } else {
      console.warn(
        '[ChatMessages] Warning: No tool call data found when finalizing streaming tool call'
      );
    }

    console.log('[ChatMessages] Streaming tool call finalized');
  }

  /**
   * Render a tool result
   */
  private renderToolResult(
    toolName: string,
    result: any,
    toolCallData: any
  ): void {
    console.log('[ChatMessages] Rendering tool result for:', toolName);
    console.log(
      '[ChatMessages] Tool result data:',
      JSON.stringify(result).substring(0, 200) +
        (JSON.stringify(result).length > 200 ? '...' : '')
    );
    console.log(`[ChatMessages] Tool result for call`, toolCallData);

    const toolCallLoading = this.container.querySelector(
      '.sage-ai-loading-text'
    );
    if (toolCallLoading) {
      toolCallLoading.classList.remove('sage-ai-loading-text');
      const container = toolCallLoading.parentElement!;
      const toolCall = container.getAttribute(
        'sage-ai-tool-call-name'
      ) as ToolCall;

      const error = getResultError(result);
      if (typeof error === 'string') {
        container.classList.add('error-state');
        container.title = error;
      }

      this.upsertCellIdLabelInDOM(container, toolCall, toolCallData, result);

      if (toolCall === 'notebook-edit_plan') {
        container.classList.add('clickable');

        container.addEventListener('click', () => {
          void this.notebookTools.scrollToPlanCell();
        });
      }

      this.scrollToBottom();
      this.lastAddedMessageType = 'tool';

      return;
    }
  }

  private upsertCellIdLabelInDOM(
    container: HTMLElement,
    toolCallName: string,
    toolCallData: any,
    result?: any
  ) {
    const oldLabel = container.querySelector('.sage-ai-tool-call-cell');
    if (oldLabel) {
      oldLabel.remove();
    }

    const shouldScrollToCellById = [
      'notebook-add_cell',
      'notebook-edit_cell',
      'notebook-run_cell'
    ].includes(toolCallName);
    if (shouldScrollToCellById) {
      let cellId: string = '';

      if (typeof result === 'string' && /^cell_(\d+)$/.test(result)) {
        cellId = result;
      }

      let toolCallCellId = toolCallData?.assistant?.content[0]?.input?.cell_id;
      if (
        typeof toolCallCellId === 'string' &&
        /^cell_(\d+)$/.test(toolCallCellId)
      ) {
        cellId = toolCallCellId;
      }

      if (
        // ...existing code...
        typeof toolCallData.cell_id === 'string' &&
        /^cell_(\d+)$/.test(toolCallData.cell_id)
      ) {
        cellId = toolCallData.cell_id;
      }

      if (cellId && /^cell_(\d+)$/.test(cellId)) {
        container.classList.add('clickable');

        const cellIdLabel = document.createElement('div');
        cellIdLabel.classList.add('sage-ai-tool-call-cell');
        cellIdLabel.innerHTML = cellId;

        container.appendChild(cellIdLabel);

        container.addEventListener('click', () => {
          void this.notebookTools.scrollToCellById(cellId);
        });
      }
    }
  }

  /**
   * Add a tool execution result to the chat history
   */
  addToolResult(
    toolName: string,
    toolUseId: string,
    result: any,
    toolCallData: any
  ): void {
    console.log('[ChatMessages] Adding tool result for:', toolName);
    this.renderToolResult(toolName, result, toolCallData);

    // Add to message history as user message (tool results are considered user messages)
    const toolResultMessage = {
      role: 'user',
      content: [
        {
          type: 'tool_result',
          tool_use_id: toolUseId,
          content: result
        }
      ]
    };

    this.messageHistory.push(toolResultMessage);

    // Update the persistent storage with contexts
    this.historyManager.updateCurrentThreadMessages(
      this.messageHistory,
      this.mentionContexts
    );

    console.log('[ChatMessages] Tool result added to history');
    console.log(
      '[ChatMessages] Current history length:',
      this.messageHistory.length
    );
    console.log(
      '[ChatMessages.addToolResult] Last message in history:',
      JSON.stringify(this.messageHistory[this.messageHistory.length - 1])
    );
  }

  /**
   * Add a loading indicator to the chat history
   */
  addLoadingIndicator(text: string = 'Generating...'): HTMLDivElement {
    this.closeToolGroupIfOpen();
    console.log('[ChatMessages] Adding loading indicator:', text);

    const loadingElement = document.createElement('div');
    loadingElement.className = 'sage-ai-message sage-ai-loading';

    // Create animated dots
    const dotsContainer = document.createElement('div');
    dotsContainer.className = 'sage-ai-blob-loader';

    loadingElement.appendChild(dotsContainer);

    // Create text element
    const textSpan = document.createElement('span');
    textSpan.textContent = text;

    loadingElement.appendChild(textSpan);

    this.container.appendChild(loadingElement);
    this.scrollToBottom();

    return loadingElement;
  }

  /**
   * Remove an element from the chat history
   */
  removeElement(element: HTMLElement): void {
    console.log('[ChatMessages] Removing element from UI');
    if (this.container.contains(element)) {
      this.container.removeChild(element);
    }
  }

  /**
   * Get the message history
   */
  getMessageHistory(): Array<IChatMessage> {
    console.log(
      '[ChatMessages] Getting message history, length:',
      this.messageHistory.length
    );
    return [...this.messageHistory];
  }

  /**
   * Update a streaming message with new text
   * @param messageElement The message element to update
   * @param text The text to append
   */
  async updateStreamingMessage(
    messageElement: HTMLDivElement,
    text: string
  ): Promise<void> {
    console.log(
      '[ChatMessages] Updating streaming message with text:',
      text.substring(0, 30) + (text.length > 30 ? '...' : '')
    );
    const content = messageElement.querySelector(
      '.sage-ai-message-content'
    ) as HTMLElement; // Add explicit type cast to HTMLElement

    if (content) {
      // Accumulate the raw text in data attribute to avoid race conditions
      const currentRawText = content.getAttribute('data-raw-text') || '';
      const newRawText = currentRawText + text;
      content.setAttribute('data-raw-text', newRawText);

      // For streaming display, we use simplified rendering
      // This avoids race conditions in markdown parsing
      content.innerHTML = await this.renderMarkdown(newRawText);

      const cursor = document.createElement('span');
      cursor.classList.add('sage-ai-streaming-cursor');

      // Append cursor to the last child of content, or to content if no children exist
      const lastChild = content.lastElementChild;
      const lastChildLastElementChild = lastChild?.lastElementChild;
      if (lastChildLastElementChild) {
        lastChildLastElementChild.appendChild(cursor);
      } else if (lastChild) {
        lastChild.appendChild(cursor);
      } else {
        content.appendChild(cursor);
      }

      this.container.scrollTop = this.container.scrollHeight;

      // Log current accumulated streaming text length
      console.log(
        '[ChatMessages] Current accumulated streaming text length:',
        newRawText.length
      );
    } else {
      console.warn(
        '[ChatMessages] Warning: Content span not found in streaming message element'
      );
    }
  }

  /**
   * Finalize a streaming message, saving it to history
   * @param messageElement The message element to finalize
   */
  async finalizeStreamingMessage(
    messageElement: HTMLDivElement
  ): Promise<void> {
    console.log('[ChatMessages] Finalizing streaming message');
    const content = messageElement.querySelector(
      '.sage-ai-message-content'
    ) as HTMLElement; // Add explicit type cast to HTMLElement

    if (content) {
      // Get the complete accumulated text
      const messageText = content.getAttribute('data-raw-text') || '';
      console.log(
        '[ChatMessages] Finalized message text length:',
        messageText.length
      );
      console.log(
        '[ChatMessages] First 100 chars of finalized message:',
        messageText.substring(0, 100) + (messageText.length > 100 ? '...' : '')
      );

      // Now that streaming is complete, render the definitive message properly
      await this.renderAssistantMessage(
        messageText,
        messageElement.parentElement || undefined
      );
      // Finishes the streaming message lifecycle removing it
      messageElement.remove();

      this.scrollToBottom();

      // Add to message history
      const aiMessage = {
        role: 'assistant',
        content: messageText
      };
      this.messageHistory.push(aiMessage);

      // Update the persistent storage with contexts
      this.historyManager.updateCurrentThreadMessages(
        this.messageHistory,
        this.mentionContexts
      );

      console.log('[ChatMessages] Finalized AI message added to history');
      console.log(
        '[ChatMessages] Current history length:',
        this.messageHistory.length
      );
    } else {
      console.warn(
        '[ChatMessages] Warning: Content span not found when finalizing streaming message'
      );
    }

    // Remove the streaming class now that it's complete
    messageElement.classList.remove('sage-ai-streaming-message');
    const cursor = messageElement.querySelector('sage-ai-streaming-cursor');
    if (cursor) {
      cursor.remove();
    }
    console.log('[ChatMessages] Streaming message finalized and class removed');
  }

  /**
   * Scroll the chat container to the bottom
   */
  public scrollToBottom(): void {
    if (this.container) {
      this.container.scrollTop = this.container.scrollHeight;
    }
  }

  /**
   * Add a streaming AI message container to the chat history
   * @returns The container element to be updated with streaming content
   */
  addStreamingAIMessage(): HTMLDivElement {
    this.closeToolGroupIfOpen();

    console.log('[ChatMessages] Adding streaming AI message container');
    const messageElement = document.createElement('div');
    messageElement.className =
      'sage-ai-message sage-ai-ai-message sage-ai-streaming-message';

    // Create header element
    const headerElement = document.createElement('div');
    headerElement.className = 'sage-ai-message-header';

    // Create header image element
    const headerImageElement = document.createElement('div');
    headerImageElement.className = 'sage-ai-message-header-image';

    headerElement.append(headerImageElement);

    // Create header title element
    const headerSageTitleElement = document.createElement('span');
    headerSageTitleElement.className = 'sage-ai-message-header-title';
    headerSageTitleElement.innerText = 'Sage';

    headerElement.append(headerSageTitleElement);

    if (this.lastAddedMessageType !== 'user') {
      headerElement.style.display = 'none';
    }

    // Create a container to hold the streaming content
    const contentElement = document.createElement('div');
    contentElement.className =
      'sage-ai-message-content sage-ai-streaming-content sage-ai-markdown-content';
    contentElement.setAttribute('data-raw-text', ''); // Store accumulated raw text

    // Assemble the message
    messageElement.appendChild(headerElement);
    messageElement.appendChild(contentElement);

    this.container.appendChild(messageElement);
    this.scrollToBottom();

    console.log(
      '[ChatMessages] Streaming message container added (not yet in history)'
    );
    return messageElement;
  }
}

/**
 * Check if the tool result is a stringified array with at least 1 { error: true } object
 * If so, returns a normalized string joining the errorText
 * This is the result of a run_cell tool call
 *
 * Returns false otherwise
 */
function getResultError(result: unknown): false | string {
  try {
    if (typeof result !== 'string') return false;

    const obj = JSON.parse(result as string);

    if (Array.isArray(obj)) {
      const errors = obj.filter(item => item && item?.error === true);
      if (!errors.length) return false;

      return errors.map(item => item.errorText).join('\n');
    }
  } catch (e) {
    console.log("Couldn't check result error", e);
  }

  return false;
}
