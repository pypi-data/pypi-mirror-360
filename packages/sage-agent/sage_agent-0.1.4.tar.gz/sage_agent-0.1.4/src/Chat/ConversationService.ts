import { ChatMessages } from './ChatMessages';
import { ToolService } from '../Services/ToolService';
import { IChatService } from '../Services/IChatService';
import { ChatRequestStatus, DiffApprovalStatus } from '../types';
import { NotebookStateService } from '../Notebook/NotebookStateService';
import { CodeConfirmationDialog } from '../Components/CodeConfirmationDialog';
import { RejectionFeedbackDialog } from '../Components/RejectionFeedbackDialog';
import {
  ActionHistory,
  ActionType,
  IActionHistoryEntry
} from './ActionHistory';
import { NotebookDiffManager } from '../Notebook/NotebookDiffManager';
import { Contents } from '@jupyterlab/services';
import { SettingsWidget } from '../Components/Settings/SettingsWidget';
import { AppStateService } from '../AppState';

export interface LoadingIndicatorManager {
  updateLoadingIndicator(text?: string): void;
  removeLoadingIndicator(): void;
}

/**
 * Service responsible for processing conversations with AI
 */
export class ConversationService {
  public chatService: IChatService;
  private toolService: ToolService;
  private messageComponent: ChatMessages;
  private notebookStateService: NotebookStateService;
  private codeConfirmationDialog: CodeConfirmationDialog;
  private loadingManager: LoadingIndicatorManager;
  private chatHistory: HTMLDivElement;
  private actionHistory: ActionHistory;
  private diffManager: NotebookDiffManager | null = null;
  private isActiveToolExecution: boolean = false; // Track if we're in a tool execution phase
  private autoRun: boolean = false; // New flag to control automatic code execution
  private notebookPath: string | null = null;
  private streamingElement: HTMLDivElement | null = null; // Element for streaming text
  private contentManager: Contents.IManager;

  // Update the property to handle multiple templates
  private templates: Array<{ name: string; content: string }> = [];

  constructor(
    chatService: IChatService,
    toolService: ToolService,
    contentManager: Contents.IManager,
    messageComponent: ChatMessages,
    chatHistory: HTMLDivElement,
    loadingManager: LoadingIndicatorManager,
    diffManager?: NotebookDiffManager
  ) {
    this.chatService = chatService;
    this.toolService = toolService;
    this.messageComponent = messageComponent;
    this.chatHistory = chatHistory;
    this.loadingManager = loadingManager;
    this.actionHistory = new ActionHistory();
    this.diffManager = diffManager || null;
    this.contentManager = contentManager;

    // Initialize dependent services
    this.notebookStateService = new NotebookStateService(toolService);
    this.codeConfirmationDialog = new CodeConfirmationDialog(
      chatHistory,
      messageComponent
    );

    // Ensure chat service has the full conversation history
    this.syncChatServiceHistory();
  }

  public updateNotebookPath(newPath: string): void {
    this.notebookPath = newPath;
    this.notebookStateService.updateNotebookPath(newPath);
  }

  /**
   * Sync the chat service's history with the message component's history
   * This ensures the LLM has full context of the conversation
   */
  private syncChatServiceHistory(): void {
    // Reset chat service history
    this.chatService.resetConversationHistory();

    // Get current message history from the message component
    const messageHistory = this.messageComponent.getMessageHistory();

    // Add each message to the chat service history
    for (const message of messageHistory) {
      if (message.role === 'assistant') {
        this.chatService.addToolResult(
          { role: 'assistant', content: message.content },
          null
        );
      } else if (message.role === 'user') {
        this.chatService.addToolResult(null, message.content);
      }
    }

    console.log(
      `Synchronized ${messageHistory.length} messages to chat service history`
    );
  }

  /**
   * Set the autorun flag
   * @param enabled Whether to automatically run code without confirmation
   */
  public setAutoRun(enabled: boolean): void {
    this.autoRun = enabled;
    console.log(`Auto-run mode ${enabled ? 'enabled' : 'disabled'}`);
  }

  /**
   * Set the diff manager instance
   */
  public setDiffManager(diffManager: NotebookDiffManager): void {
    this.diffManager = diffManager;
    console.log('NotebookDiffManager set in ConversationService');
  }

  /**
   * Set the current notebook path
   * @param notebookPath Path to the notebook to interact with
   */
  public setNotebookPath(notebookPath: string): void {
    this.notebookPath = notebookPath;
    console.log(`[ConversationService] Set notebook path: ${notebookPath}`);
  }

  /**
   * Handles the case when a cell execution is rejected
   */
  public async handleCellRejection(
    mode: 'agent' | 'ask' | 'fast' = 'agent'
  ): Promise<void> {
    this.messageComponent.addSystemMessage(
      'Cell execution rejected. Asking for corrections based on user feedback...'
    );

    const rejectionDialog = new RejectionFeedbackDialog();
    const rejectionReason = await rejectionDialog.showDialog();

    // Add the special user feedback message
    const rejectionMessage = {
      role: 'user',
      content: `I rejected the previous cell execution because: ${rejectionReason}`
    };

    // Add the feedback to the visible message history
    this.messageComponent.addUserMessage(
      `I rejected the previous cell execution because: ${rejectionReason}`
    );

    // Process conversation with just the new rejection message
    await this.processConversation([rejectionMessage], [], mode);
  }

  /**
   * Process a tool call ensuring the notebook path is passed through
   */
  private async processToolCall(toolCall: any): Promise<any> {
    // Create a copy of the tool call that includes notebook path
    const toolCallWithContext = {
      ...toolCall,
      input: {
        ...toolCall.input,
        notebook_path: this.notebookPath
      }
    };

    return await this.toolService.executeTool(
      toolCallWithContext,
      3, // maxRetries
      true // includeContextInfo
    );
  }

  /**
   * Execute all approved cells from the diff manager
   * @param contentId The content ID for tracking tool results
   * @returns Promise resolving to true if cells were executed, false if none to execute
   */
  public async executeAllApprovedCells(contentId: string): Promise<boolean> {
    if (!this.diffManager || !this.diffManager.shouldExecuteApprovedCells()) {
      return false;
    }

    // Get all approved cell IDs
    const approvedCellIds = this.diffManager.getApprovedCellIds(
      this.notebookPath
    );

    if (approvedCellIds.length === 0) {
      return false;
    }

    this.messageComponent.addSystemMessage(
      `Running all ${approvedCellIds.length} approved cells.`
    );

    // Show loading indicator while executing
    this.loadingManager.updateLoadingIndicator('Running cells...');

    // Execute each approved cell
    for (const cellId of approvedCellIds) {
      try {
        const result = await this.toolService.executeTool({
          id: `run_approved_cell_${cellId}`,
          name: 'notebook-run_cell',
          input: {
            cell_id: cellId,
            notebook_path: this.notebookPath
          }
        });

        // Show each cell's output
        if (result && result.content) {
          this.messageComponent.addToolResult(
            'notebook-run_cell',
            contentId,
            result.content,
            undefined // No input to display for approved cells
          );
        }
      } catch (error) {
        console.error(`Error running cell ${cellId}:`, error);
        this.messageComponent.addErrorMessage(
          `Error running cell: ${error instanceof Error ? error.message : String(error)}`
        );
      }
    }

    // Remove loading indicator
    this.loadingManager.removeLoadingIndicator();
    return true;
  }

  public async createErrorMessage(message: any) {
    console.log('Creating error message dump...');
    console.log(message);
    try {
      let fileExists = false;
      try {
        await this.contentManager.get('./error_dump.txt');
        fileExists = true;
      } catch (e) {
        fileExists = false;
      }
      if (!fileExists) {
        await this.contentManager.save('./error_dump.txt', {
          type: 'file',
          format: 'text',
          content: ''
        });
      }

      const current = await this.contentManager.get('./error_dump.txt');
      let content = current.content || '';

      content += `\n\n---\n\n${new Date().toISOString()}\n\n${message}`;
      await this.contentManager.save('./error_dump.txt', {
        type: 'file',
        format: 'text',
        content: content
      });
    } catch (err) {
      console.error(err);
    }
  }

  /**
   * Process the conversation with the AI service
   */
  public async processConversation(
    newMessages: any[],
    systemPromptMessages: string[] = [],
    mode: 'agent' | 'ask' | 'fast' = 'agent'
  ): Promise<void> {
    // Ensure notebook path is being used in processing
    console.log(
      `[ConversationService] Processing conversation for notebook: ${this.notebookPath || 'unknown'}`
    );

    // Don't check for diffs at the beginning - we'll do that just before code execution
    // or if we reach the end without tool calls

    // Process conversation with tool calls
    let response;
    // Create a streaming message element that will be updated as we receive content
    let currentStreamingMessage: HTMLDivElement | null = null;
    // Create a streaming tool call element that will be updated as we receive tool calls
    let currentStreamingToolCall: HTMLDivElement | null = null;

    let streamingToolCall:
      | {
          id: string;
          name: string;
          accumulatedInput: string;
          cellId?: string;
          originalContent?: string;
          originalSummary?: string;
          summary?: string;
          toolResult?: {
            type: 'tool_result';
            tool_use_id: string;
            content: string;
          };
        }
      | undefined;

    try {
      // Add the loading indicator at the start
      this.loadingManager.updateLoadingIndicator();

      this.toolService.notebookTools?.refresh_ids();

      // If we have template contexts, prepend a system message for each template
      if (this.templates && this.templates.length > 0) {
        const templateMessages = this.templates.map(template => ({
          role: 'user',
          content: `I'm providing the template "${template.name}" as additional context for our conversation:\n\n${template.content}`
        }));

        // Prepend template messages to the messages being sent
        newMessages = [...templateMessages, ...newMessages];

        // Clear the template contexts after use - they're one-time contexts
        this.templates = [];
      }

      const tools =
        mode === 'ask'
          ? this.toolService.getAskModeTools()
          : this.toolService.getTools();

      // Call AI service with retry handling and notebook state fetching
      response = await this.chatService.sendMessage(
        newMessages,
        tools,
        mode,
        systemPromptMessages,
        async (error, attempt) => {
          // Don't set up retry if we've been cancelled
          if (
            this.chatService.getRequestStatus() === ChatRequestStatus.CANCELLED
          ) {
            return;
          }

          this.messageComponent.addErrorMessage(
            `API request failed: ${error.message}. Retrying in 45 seconds... (Attempt ${attempt})`
          );

          // Update loading indicator with retry information
          this.loadingManager.updateLoadingIndicator('Waiting to retry...');
        },
        // Pass the notebook state fetching function
        () => this.notebookStateService.fetchNotebookState(),
        (text: string) => {
          // Check if we're cancelled before handling streaming text
          if (
            this.chatService.getRequestStatus() === ChatRequestStatus.CANCELLED
          ) {
            return;
          }

          // Remove loading indicator once streaming starts
          this.loadingManager.removeLoadingIndicator();

          if (!currentStreamingMessage) {
            // Create a new streaming message container on first chunk
            currentStreamingMessage =
              this.messageComponent.addStreamingAIMessage();
          }

          // Append the new text chunk to the message
          this.messageComponent.updateStreamingMessage(
            currentStreamingMessage,
            text
          );
        },
        (toolUse: any) => {
          console.log('[ConversationService] Tool use detected:', toolUse);

          if (
            this.chatService.getRequestStatus() === ChatRequestStatus.CANCELLED
          ) {
            return;
          }

          this.loadingManager.removeLoadingIndicator();

          if (!currentStreamingToolCall) {
            currentStreamingToolCall =
              this.messageComponent.addStreamingToolCall();
          }

          // Handle the different types of tool_use events
          if (toolUse.type === 'tool_use_delta') {
            // This is a streaming update for a tool call's input.
            if (streamingToolCall) {
              streamingToolCall.accumulatedInput += toolUse.input_delta;

              // Use regex to extract the code from the partial JSON.
              const codeRegex =
                /"(?:source|new_source|updated_plan_string)"\s*:\s*"((?:[^"\\]|\\.)*)/;
              const match = streamingToolCall.accumulatedInput.match(codeRegex);

              const partialToolUse = {
                type: 'tool_use',
                id: toolUse.id,
                name: streamingToolCall.name,
                input: {
                  is_streaming: true,
                  updated_plan_string: undefined,
                  new_source: undefined,
                  source: undefined,
                  cell_id: undefined
                }
              };

              if (match && match[1]) {
                try {
                  // Unescape the JSON string content to get the real code.
                  const code = JSON.parse(`"${match[1]}"`);

                  // --- Real-time notebook updates ---
                  const isAddCell =
                    streamingToolCall.name === 'notebook-add_cell';
                  const isEditCell =
                    streamingToolCall.name === 'notebook-edit_cell';
                  const isEditPlan =
                    streamingToolCall.name === 'notebook-edit_plan';

                  if (isEditPlan) {
                    this.toolService.notebookTools?.stream_edit_plan({
                      partial_plan: code,
                      notebook_path: this.notebookPath
                    });
                    partialToolUse.input.updated_plan_string = code;
                  }
                  if (isAddCell) {
                    // Extract cell_type from accumulated input
                    const cellTypeRegex = /"cell_type"\s*:\s*"([^"]*)"/;
                    const cellTypeMatch =
                      streamingToolCall.accumulatedInput.match(cellTypeRegex);
                    const cellType = cellTypeMatch ? cellTypeMatch[1] : null;

                    const cellSummaryRegex = /"summary"\s*:\s*"([^"]*)"/;
                    const cellSummaryMatch =
                      streamingToolCall.accumulatedInput.match(
                        cellSummaryRegex
                      );
                    const cellSummary = cellSummaryMatch
                      ? cellSummaryMatch[1]
                      : 'Cell being created by AI...';

                    // Only create cell if we have a valid cell_type
                    const validCellTypes = ['code', 'markdown', 'raw'];
                    if (cellType && validCellTypes.includes(cellType)) {
                      if (!streamingToolCall.cellId) {
                        // First delta: create the cell
                        const newCellId =
                          this.toolService.notebookTools?.add_cell({
                            cell_type: cellType,
                            summary: cellSummary,
                            source: code,
                            notebook_path: this.notebookPath
                          });
                        partialToolUse.input.source = code;
                        partialToolUse.input.cell_id =
                          streamingToolCall.cellId as any;

                        streamingToolCall.cellId = newCellId;
                        streamingToolCall.toolResult = {
                          type: 'tool_result',
                          tool_use_id: toolUse.id,
                          content: newCellId || ''
                        };
                      } else {
                        // Subsequent deltas: edit the cell
                        this.toolService.notebookTools?.edit_cell({
                          cell_id: streamingToolCall.cellId,
                          summary: cellSummary,
                          new_source: code,
                          is_tracking_id: true, // add_cell returns a tracking ID
                          notebook_path: this.notebookPath
                        });
                      }
                    }
                  } else if (isEditCell) {
                    // For edit_cell, we also need the cell_id from the stream
                    if (!streamingToolCall.cellId) {
                      const cellIdRegex = /"cell_id"\s*:\s*"([^"]*)"/;
                      const cellIdMatch =
                        streamingToolCall.accumulatedInput.match(cellIdRegex);
                      if (cellIdMatch && cellIdMatch[1]) {
                        streamingToolCall.cellId = cellIdMatch[1];

                        // Get the original content for diff tracking
                        if (
                          this.diffManager &&
                          !streamingToolCall.originalContent
                        ) {
                          try {
                            const cellInfo =
                              this.toolService.notebookTools?.findCellByAnyId(
                                streamingToolCall.cellId,
                                this.notebookPath
                              );
                            if (cellInfo) {
                              streamingToolCall.originalContent =
                                cellInfo.cell.model.sharedModel.getSource() ||
                                '';
                              streamingToolCall.originalSummary =
                                (
                                  cellInfo.cell.model.sharedModel.metadata
                                    .custom as any
                                ).summary || '';
                            }
                          } catch (error) {
                            console.warn(
                              'Could not get original content for diff:',
                              error
                            );
                          }
                        }
                      }
                    }

                    if (streamingToolCall.cellId) {
                      // For edit_cell, we need to properly handle the diff calculation
                      // The streaming code might be partial, so we need to preserve the rest of the original content
                      let finalContent = code;

                      if (
                        streamingToolCall.originalContent &&
                        code.length < streamingToolCall.originalContent.length
                      ) {
                        // If the streaming code is shorter than original, preserve the remaining content
                        finalContent =
                          code +
                          streamingToolCall.originalContent.substring(
                            code.length
                          );
                      } else if (
                        streamingToolCall.originalContent &&
                        code.length > streamingToolCall.originalContent.length
                      ) {
                        // If streaming code is longer than original, use the new code as-is
                        finalContent = code;
                      }
                      // If lengths are equal, use the new code as-is

                      const result = this.toolService.notebookTools?.edit_cell({
                        cell_id: streamingToolCall.cellId,
                        new_source: finalContent,
                        summary:
                          streamingToolCall.summary ||
                          'Cell being updated by AI...',
                        is_tracking_id:
                          streamingToolCall.cellId.startsWith('cell_'),
                        notebook_path: this.notebookPath
                      });
                      streamingToolCall.toolResult = {
                        type: 'tool_result',
                        tool_use_id: toolUse.id,
                        content: result ? `true` : 'false'
                      };
                    }

                    partialToolUse.input.new_source = code;
                    partialToolUse.input.cell_id =
                      streamingToolCall.cellId as any;
                  }
                  // --- End real-time notebook updates ---

                  this.messageComponent.updateStreamingToolCall(
                    currentStreamingToolCall,
                    partialToolUse
                  );
                } catch (e) {
                  // JSON is likely not well-formed enough to parse the string yet.
                  // We can ignore this and wait for the next delta.
                }
              }
            }
          }

          if (toolUse.type === 'tool_use') {
            streamingToolCall = {
              id: toolUse.id,
              name: toolUse.name,
              accumulatedInput: ''
            };

            // Show tool state in LLMStateDisplay for streaming tool calls (unless we have pending diffs)
            const llmStateDisplay =
              AppStateService.getChatContainerSafe()?.chatWidget
                .llmStateDisplay;
            if (llmStateDisplay && !llmStateDisplay.isDiffState()) {
              llmStateDisplay.showTool(toolUse.name);
            }

            // Update the streaming tool call with the new tool use
            this.messageComponent.updateStreamingToolCall(
              currentStreamingToolCall,
              toolUse
            );
          }

          if (toolUse.type === 'tool_use_stop') {
            this.messageComponent.updateStreamingToolCall(
              currentStreamingToolCall,
              toolUse
            );

            if (toolUse.name === 'notebook-edit_cell') {
              this.toolService.notebookTools?.edit_cell({
                cell_id: toolUse.input.cell_id,
                new_source: toolUse.input.new_source || '',
                summary: toolUse.input.summary || '',
                is_tracking_id: true,
                notebook_path: this.notebookPath
              });

              this.diffManager?.trackEditCell(
                toolUse.input.cell_id,
                streamingToolCall!.originalContent || '',
                toolUse.input.new_source,
                toolUse.input.summary,
                this.notebookPath
              );
            }

            if (toolUse.name === 'notebook-add_cell') {
              this.toolService.notebookTools?.edit_cell({
                cell_id: streamingToolCall!.cellId!,
                new_source: toolUse.input.source || '',
                summary: toolUse.input.summary || '',
                is_tracking_id: true,
                notebook_path: this.notebookPath
              });

              this.diffManager?.trackAddCell(
                streamingToolCall!.cellId!,
                toolUse.input.source,
                toolUse.input.summary
              );
            }

            if (toolUse.name === 'notebook-edit_plan') {
              this.toolService.notebookTools?.edit_plan({
                updated_plan_string: toolUse.input.updated_plan_string,
                current_step_string: toolUse.input.current_step_string,
                next_step_string: toolUse.input.next_step_string,
                notebook_path: this.notebookPath
              });
            }
          }
        },
        // Pass the notebook context manager and notebook path
        this.toolService.getContextManager(),
        this.notebookPath as string,
        this.createErrorMessage.bind(this)
      );

      // Check if the response indicates cancellation
      if (response?.cancelled || this.chatService.isRequestCancelled()) {
        console.log('Response processing skipped due to cancellation');
        // Clean up any streaming message if it exists
        if (currentStreamingMessage) {
          this.messageComponent.removeElement(currentStreamingMessage);
        }
        // Clean up any streaming tool call if it exists
        if (currentStreamingToolCall) {
          this.messageComponent.removeElement(currentStreamingToolCall);
        }

        this.loadingManager.removeLoadingIndicator();
        return;
      }
    } catch (error) {
      // If cancelled, just return without showing an error
      if (this.chatService.isRequestCancelled()) {
        console.log('Request was cancelled, skipping error handling');
        // Clean up any streaming message if it exists
        if (currentStreamingMessage) {
          this.messageComponent.removeElement(currentStreamingMessage);
        }
        // Clean up any streaming tool call if it exists
        if (currentStreamingToolCall) {
          this.messageComponent.removeElement(currentStreamingToolCall);
        }

        this.loadingManager.removeLoadingIndicator();
        return;
      }

      this.loadingManager.removeLoadingIndicator();
      throw error;
    }

    // Check if we received a cell rejection signal
    if (response.needsFreshContext === true) {
      this.loadingManager.removeLoadingIndicator();
      await this.handleCellRejection(mode);
      return;
    }

    // Finalize the streaming message if it exists
    if (currentStreamingMessage) {
      await this.messageComponent.finalizeStreamingMessage(
        currentStreamingMessage
      );
    }

    // Finalize the streaming tool call if it exists
    if (currentStreamingToolCall) {
      this.messageComponent.finalizeStreamingToolCall(currentStreamingToolCall);

      // Revert to generating state after streaming tool call finishes (unless we have pending diffs)
      const llmStateDisplay =
        AppStateService.getChatContainerSafe()?.chatWidget.llmStateDisplay;
      if (llmStateDisplay && !llmStateDisplay.isDiffState()) {
        llmStateDisplay.show('Generating...');
        llmStateDisplay.hide();
      }
    }

    // Check again for cancellation before processing tool calls
    if (this.chatService.getRequestStatus() === ChatRequestStatus.CANCELLED) {
      console.log('Request was cancelled, skipping tool call processing');
      this.loadingManager.removeLoadingIndicator();
      return;
    }
    if (SettingsWidget.SAGE_TOKEN_MODE) {
      console.log('Sage Token Mode is enabled, adding usage message');
      console.log('Response usage:', response);
      let numUserMessages = 0;
      let numAIResponses = 0;
      let numToolCalls = 0;
      let numToolResults = 0;
      for (const message of this.messageComponent.getMessageHistory()) {
        console.log(message);

        if (typeof message.content === 'string') {
          if (message.role === 'assistant') numAIResponses += 1;
          else numUserMessages += 1;
        } else {
          if (message.role === 'assistant') numToolCalls += 1;
          else numToolResults += 1;
        }
      }

      this.messageComponent.addSystemMessage(
        `cache_input_tokens: ${response.usage.cache_creation_input_tokens}, cache_read_tokens: ${response.usage.cache_read_input_tokens} \n
         input_tokens: ${response.usage.input_tokens}, output_tokens: ${response.usage.output_tokens} \n
         user_messages: ${numUserMessages}, assistant_responses: ${numAIResponses} \n
         tool_calls: ${numToolCalls}, tool_results: ${numToolResults} \n`
      );
    }

    // Process tool calls if any exist
    let hasToolCalls = false;
    if (response.content && response.content.length > 0) {
      for (const content of response.content) {
        // Check for cancellation before each tool processing
        if (this.chatService.isRequestCancelled()) {
          console.log('Request was cancelled, stopping tool processing');
          this.loadingManager.removeLoadingIndicator();
          return;
        }

        // Only process tool calls
        if (content.type === 'tool_use') {
          hasToolCalls = true;
          this.isActiveToolExecution = true; // Mark that we're executing tools
          const toolName = content.name;
          const toolArgs = content.input;
          console.log(`AI wants to use tool: ${toolName}`);

          // Track actions for undo functionality based on tool type
          let actionBeforeExecution: any = null;

          // For edit_cell and remove_cells, capture the existing state first
          if (toolName === 'notebook-edit_cell') {
            try {
              // Get the cell before it's modified
              const cellInfo = await this.toolService.executeTool({
                id: 'get_cell_before_edit',
                name: 'notebook-get_cell_info',
                input: { cell_id: toolArgs.cell_id }
              });

              if (cellInfo && cellInfo.content) {
                const cellData = JSON.parse(cellInfo.content);
                actionBeforeExecution = {
                  originalCell: cellData,
                  originalContent: streamingToolCall?.originalContent || '',
                  originalSummary: streamingToolCall?.originalSummary || '',
                  newSource: toolArgs.new_source,
                  cellId: toolArgs.cell_id,
                  cell_id: toolArgs.cell_id,
                  summary: toolArgs.summary
                };
              }
            } catch (err) {
              console.error('Failed to get cell info before edit:', err);
            }
          } else if (toolName === 'notebook-remove_cells') {
            try {
              // Get information about cells before removal
              const cellsToRemove = toolArgs.cell_ids || [];
              const cellInfoPromises = cellsToRemove.map((cellId: string) =>
                this.toolService.executeTool({
                  id: `get_cell_before_remove_${cellId}`,
                  name: 'notebook-get_cell_info',
                  input: { cell_id: cellId }
                })
              );

              const cellInfoResults = await Promise.all(cellInfoPromises);
              const removedCells = cellInfoResults
                .map(result => {
                  if (result && result.content) {
                    return JSON.parse(result.content);
                  }
                  return null;
                })
                .filter(cell => cell !== null);

              if (removedCells.length > 0) {
                actionBeforeExecution = {
                  removedCells
                };
              }
            } catch (err) {
              console.error('Failed to get cell info before removal:', err);
            }
          }

          // Handle special case for run_cell and execute_cell - check for diff approval first
          if (
            toolName === 'notebook-run_cell' ||
            toolName === 'notebook-execute_cell'
          ) {
            this.loadingManager.removeLoadingIndicator();

            // Check for pending diffs before running cells
            const diffsApproved =
              await this.checkPendingDiffsBeforeCodeExecution();
            if (!diffsApproved) {
              // All diffs were rejected, so stop processing and do not show code execution confirmation
              this.messageComponent.addSystemMessage(
                '❌ All changes were rejected. Code execution has been cancelled.'
              );
              return;
            }

            // Check if we should execute all approved cells
            const executedApprovedCells = await this.executeAllApprovedCells(
              content.id
            );
            if (executedApprovedCells) {
              // Skip the original run_cell call since we've executed all cells
              continue;
            }

            // If we're dealing with a cell ID that might have changed due to diff application,
            // ensure we're using the latest cell ID
            if (this.diffManager && toolArgs.cell_id) {
              const updatedCellId = this.diffManager.getCurrentCellId(
                toolArgs.cell_id
              );
              if (updatedCellId !== toolArgs.cell_id) {
                console.log(
                  `Updating cell ID for execution: ${toolArgs.cell_id} → ${updatedCellId}`
                );
                toolArgs.cell_id = updatedCellId;
              }
            }

            // Check if we should skip confirmation (either via autoRun or "Approve All and Run" flag)
            let shouldRun = false;

            if (this.autoRun) {
              // Auto-run enabled - skip confirmation
              shouldRun = true;
              this.messageComponent.addSystemMessage(
                'Automatically running code (auto-run is enabled).'
              );
            } else if (
              this.diffManager &&
              this.diffManager.shouldRunImmediately()
            ) {
              // Skip confirmation if approved with "Approve All and Run"
              shouldRun = true;
              this.messageComponent.addSystemMessage(
                'Running code immediately after approving changes.'
              );
            } else {
              // Otherwise show the normal confirmation
              shouldRun = await this.codeConfirmationDialog.showConfirmation(
                toolArgs.code || toolArgs.source || ''
              );
              if (!shouldRun) {
                this.messageComponent.removeLoadingText();
              }
            }

            // If user rejects code execution
            if (!shouldRun) {
              // Handle rejection
              await this.handleCellRejection(mode);
              return;
            }

            // Show loading indicator again after confirmation
            this.loadingManager.updateLoadingIndicator();
          }

          // Show tool state in LLMStateDisplay (unless we have pending diffs which take precedence)
          const llmStateDisplay =
            AppStateService.getChatContainerSafe()?.chatWidget.llmStateDisplay;
          if (llmStateDisplay && !llmStateDisplay.isDiffState()) {
            llmStateDisplay.showTool(toolName);
          }

          // The streaming tool calls are edit, plan and add cell
          const isStreamToolCall =
            streamingToolCall && streamingToolCall.toolResult;

          const toolResult = isStreamToolCall
            ? streamingToolCall!.toolResult
            : await this.processToolCall({
                id: content.id,
                name: toolName,
                input: toolArgs
              });

          // Mark tool execution as complete
          this.isActiveToolExecution = false;

          // Revert to generating state after tool completion (unless we have pending diffs)
          if (llmStateDisplay && !llmStateDisplay.isDiffState()) {
            llmStateDisplay.show('Generating...');
          }

          // Track the action in history for undo
          if (
            toolName === 'notebook-add_cell' &&
            toolResult &&
            toolResult.content
          ) {
            try {
              // For add_cell, we need the cell ID that was created
              const cellId = toolResult.content.replace(/"/g, '').trim();
              this.actionHistory.addAction(
                ActionType.ADD_CELL,
                { cellId, ...toolArgs },
                `Added ${toolArgs.cell_type} cell`
              );
            } catch (err) {
              console.error('Failed to track add_cell action:', err);
            }
          } else if (
            toolName === 'notebook-edit_cell' &&
            actionBeforeExecution
          ) {
            this.actionHistory.addAction(
              ActionType.EDIT_CELL,
              actionBeforeExecution,
              `Edited cell ${toolArgs.cell_id.substring(0, 8)}...`
            );
          } else if (
            toolName === 'notebook-remove_cells' &&
            actionBeforeExecution
          ) {
            this.actionHistory.addAction(
              ActionType.REMOVE_CELLS,
              actionBeforeExecution,
              `Removed ${toolArgs.cell_ids.length} cell(s)`
            );

            // If we have a diff manager, also track remove diffs
            if (this.diffManager && actionBeforeExecution.removedCells) {
              for (const cell of actionBeforeExecution.removedCells) {
                if (cell && (cell.id || cell.trackingId)) {
                  this.diffManager.trackRemoveCell(
                    cell.trackingId || cell.id,
                    cell.content || '',
                    cell.custom?.summary || 'Removed by AI'
                  );
                }
              }
            }
          }

          // Check for cancellation before showing tool results
          if (
            this.chatService.getRequestStatus() === ChatRequestStatus.CANCELLED
          ) {
            console.log('Request was cancelled, skipping tool result display');
            return;
          }

          // Show the tool result in the UI
          this.messageComponent.addToolResult(
            toolName,
            content.id,
            toolResult.content,
            content?.input
          );

          // Check if we've been cancelled
          if (
            this.chatService.getRequestStatus() === ChatRequestStatus.CANCELLED
          ) {
            return;
          }

          // Create assistant message with tool call for history tracking
          const assistantMessage = {
            role: 'assistant',
            content: [content]
          };

          // Add tool call and result to the conversation history
          this.chatService.addToolResult(assistantMessage, toolResult);

          // Final check for cancellation before recursively processing
          if (
            this.chatService.getRequestStatus() === ChatRequestStatus.CANCELLED
          ) {
            console.log('Request was cancelled, skipping further processing');
            return;
          }

          if (toolName !== 'notebook-wait_user_reply') {
            // Process the new conversation with the tool result - no need to pass history
            llmStateDisplay?.hidePendingDiffs();
            llmStateDisplay?.show('Generating...');
            await this.processConversation([], systemPromptMessages, mode);
          } else {
            llmStateDisplay?.show('Waiting for user reply...', true);
          }

          streamingToolCall = undefined;
          this.streamingElement = null;
        }
      }
    }

    // If we've reached this point and there were no tool calls, check for pending diffs
    if (
      hasToolCalls &&
      this.diffManager &&
      this.diffManager.hasPendingDiffs()
    ) {
      this.isActiveToolExecution = true; // Mark that we're handling diffs

      // Show pending diffs in LLMStateDisplay
      const llmStateDisplay =
        AppStateService.getChatContainerSafe()?.chatWidget.llmStateDisplay;
      if (llmStateDisplay) {
        llmStateDisplay.showPendingDiffs(this.notebookPath);
      }

      await this.checkPendingDiffs();
      this.isActiveToolExecution = false;

      // Hide pending diffs after processing
      // if (llmStateDisplay) {
      //   llmStateDisplay.hidePendingDiffs();
      // }
    }

    // Remove loading indicator at the end of processing
    this.loadingManager.removeLoadingIndicator();
  }

  /**
   * Check for pending diffs and prompt the user for approval if needed
   * @returns Promise that resolves to true if all diffs were approved or no diffs pending
   */
  private async checkPendingDiffs(): Promise<boolean> {
    if (!this.diffManager || !this.diffManager.hasPendingDiffs()) {
      return true; // No diffs to approve or no diff manager
    }

    // If autorun is enabled, auto-approve all diffs without showing dialog
    if (this.autoRun) {
      this.messageComponent.addSystemMessage(
        `Auto-approving ${this.diffManager.getPendingDiffCount()} changes (auto-run is enabled).`
      );

      // Approve all diffs automatically
      this.diffManager['approveAllDiffs'](this.notebookPath); // Using brackets notation to access private method
      await this.diffManager.applyApprovedDiffs(this.notebookPath);

      return true;
    }

    // Show the approval dialog embedded in the chat
    const approvalStatus = await this.diffManager.showApprovalDialog(
      this.chatHistory,
      true, // Use embedded mode for chat context
      false, // Not a run context
      this.notebookPath || undefined // Pass the notebook path (convert null to undefined)
    );

    // Make sure we scroll to see the dialog
    this.messageComponent.scrollToBottom();

    // Return true if all diffs were approved or partially approved
    return approvalStatus !== DiffApprovalStatus.REJECTED;
  }

  /**
   * Check for pending diffs specifically before code execution
   * @returns Promise that resolves to true if all diffs were approved or no diffs pending
   */
  private async checkPendingDiffsBeforeCodeExecution(): Promise<boolean> {
    if (!this.diffManager || !this.diffManager.hasPendingDiffs()) {
      return true; // No diffs to approve or no diff manager
    }

    // If autorun is enabled, auto-approve all diffs without showing dialog
    if (this.autoRun) {
      this.messageComponent.addSystemMessage(
        `Auto-approving ${this.diffManager.getPendingDiffCount()} changes (auto-run is enabled).`
      );

      // Approve all diffs automatically
      this.diffManager['approveAllDiffs'](this.notebookPath); // Using brackets notation to access private method
      await this.diffManager.applyApprovedDiffs(this.notebookPath);

      // Set the flag to execute all approved cells
      this.diffManager.setExecuteApprovedCells(true);

      return true;
    }

    // Traditional flow - show approval dialog
    this.messageComponent.addSystemMessage(
      `Before running code, ${this.diffManager.getPendingDiffCount()} pending changes to your notebook need approval.`
    );

    // Show the inline diff approval dialog for chat context with run context flag
    const approvalStatus = await this.diffManager.showApprovalDialog(
      this.chatHistory,
      true, // Use inline mode for chat context
      true, // This is in a run context
      this.notebookPath || undefined // Pass the notebook path (convert null to undefined)
    );

    // Make sure we scroll to see the dialog
    this.messageComponent.scrollToBottom();

    // Return true if all diffs were approved or partially approved
    return approvalStatus !== DiffApprovalStatus.REJECTED;
  }

  /**
   * Check if the model is actively executing tools or showing diff approvals
   * This helps determine if input should be enabled
   */
  public isActivelyExecutingTools(): boolean {
    return this.isActiveToolExecution;
  }

  /**
   * Check if there are any actions that can be undone
   * @returns True if there are actions in the history
   */
  public canUndo(): boolean {
    return this.actionHistory.canUndo();
  }

  /**
   * Get the description of the last action
   * @returns Description of the last action or null if none
   */
  public getLastActionDescription(): string | null {
    return this.actionHistory.getLastActionDescription();
  }

  /**
   * Undo the last action
   * @returns True if an action was undone, false if no actions to undo
   */
  public async undoLastAction(): Promise<boolean> {
    const action = this.actionHistory.popLastAction();
    if (!action) {
      return false;
    }

    try {
      this.loadingManager.updateLoadingIndicator('Undoing action...');

      switch (action.type) {
        case ActionType.ADD_CELL:
          await this.undoAddCell(action);
          break;

        case ActionType.EDIT_CELL:
          await this.undoEditCell(action);
          break;

        case ActionType.REMOVE_CELLS:
          await this.undoRemoveCells(action);
          break;
      }

      // Add a system message to indicate the action was undone
      this.messageComponent.addSystemMessage(
        `✓ Undid action: ${action.description}`
      );
      this.loadingManager.removeLoadingIndicator();
      return true;
    } catch (error) {
      console.error('Error undoing action:', error);
      this.messageComponent.addErrorMessage(
        `Failed to undo action: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
      this.loadingManager.removeLoadingIndicator();
      return false;
    }
  }

  /**
   * Undo adding a cell
   */
  private async undoAddCell(action: IActionHistoryEntry): Promise<void> {
    // Use trackingId if available, fallback to cellId for backward compatibility
    const trackingId = action.data.trackingId || action.data.cellId;

    // Remove the added cell using tracking ID
    await this.toolService.executeTool({
      id: 'undo_add_cell',
      name: 'notebook-remove_cells',
      input: {
        cell_ids: [trackingId],
        remove_from_notebook: true
      }
    });
  }

  /**
   * Undo editing a cell
   */
  private async undoEditCell(action: IActionHistoryEntry): Promise<void> {
    // Use trackingId if available, fallback to cellId for backward compatibility
    const trackingId = action.data.trackingId || action.data.cellId;

    // Restore the original cell content using tracking ID
    await this.toolService.executeTool({
      id: 'undo_edit_cell',
      name: 'notebook-edit_cell',
      input: {
        cell_id: trackingId,
        new_source: action.data.originalContent,
        summary: action.data.originalSummary || 'Restored by undo',
        is_tracking_id: true
      }
    });
  }

  /**
   * Undo removing cells
   */
  private async undoRemoveCells(action: IActionHistoryEntry): Promise<void> {
    // Re-add each removed cell
    if (action.data.removedCells) {
      for (let i = 0; i < action.data.removedCells.length; i++) {
        const cell = action.data.removedCells[i];
        // Generate a tracking ID if none was saved
        const trackingId = cell.trackingId || `restored-${Date.now()}-${i}`;

        await this.toolService.executeTool({
          id: 'undo_remove_cell',
          name: 'notebook-add_cell',
          input: {
            cell_type: cell.type,
            source: cell.content,
            summary: cell.custom?.summary || 'Restored by undo',
            position: cell.custom?.index, // Use index from custom metadata if available
            tracking_id: trackingId // Provide tracking ID to reuse
          }
        });
      }
    }
  }

  /**
   * Clear the action history
   */
  public clearActionHistory(): void {
    this.actionHistory.clear();
  }
}
