import Anthropic from '@anthropic-ai/sdk';

export interface MessageCreationParams {
  client: Anthropic;
  modelName: string;
  systemPrompt: string;
  systemPromptAskMode: string;
  systemPromptFastMode: string;
  isFastMode: boolean;
  toolBlacklist: string[];
  mode: 'agent' | 'ask' | 'fast';
  tools: any[];
  systemPromptMessages?: string[];
  fetchNotebookState?: () => Promise<string>;
  notebookContextManager?: any;
  notebookPath?: string;
  abortSignal: AbortSignal;
  errorLogger?: (message: any) => Promise<void>;
}

export interface PreparedMessages {
  initialMessages: any[];
  filteredHistory: any[];
  availableTools: any[];
  systemPrompt: string;
  extraSystemMessages: any[];
}

/**
 * Handles message preparation and stream creation for Anthropic API
 */
export class AnthropicMessageCreator {
  /**
   * Prepares messages and creates a stream
   */
  static async createMessageStream(
    params: MessageCreationParams,
    filteredHistory: any[],
    normalizeMessageContent: (
      messages: any[],
      errorLogger?: (message: any) => Promise<void>
    ) => any[]
  ): Promise<any> {
    const prepared = await this.prepareMessages(
      params,
      filteredHistory,
      normalizeMessageContent
    );

    return params.client.beta.messages.stream(
      {
        model: params.modelName,
        messages: [...prepared.initialMessages, ...prepared.filteredHistory],
        tools:
          prepared.availableTools.length > 0
            ? prepared.availableTools
            : undefined,
        max_tokens: 4096,
        system: [
          {
            text: prepared.systemPrompt,
            type: 'text',
            cache_control: {
              type: 'ephemeral'
            }
          },
          ...prepared.extraSystemMessages
        ] as Anthropic.Beta.Messages.BetaTextBlockParam[],
        betas: ['token-efficient-tools-2025-02-19']
      },
      {
        signal: params.abortSignal,
        headers: {
          'no-cors': 'true',
          'sec-fetch-mode': 'no-cors',
          mode: 'no-cors'
        }
      }
    );
  }

  /**
   * Prepares all messages and configuration for the API call
   */
  private static async prepareMessages(
    params: MessageCreationParams,
    filteredHistory: any[],
    normalizeMessageContent: (
      messages: any[],
      errorLogger?: (message: any) => Promise<void>
    ) => any[]
  ): Promise<PreparedMessages> {
    // Get notebook context
    const contextCellsContent = await this.getNotebookContext(params);

    // Prepare initial messages
    const initialMessages = this.prepareInitialMessages(contextCellsContent);

    // Normalize messages
    const normalizedInitialMessages = normalizeMessageContent(
      initialMessages,
      params.errorLogger
    );
    const normalizedFilteredHistory = normalizeMessageContent(
      filteredHistory,
      params.errorLogger
    );

    // Determine system prompt
    const systemPrompt = this.determineSystemPrompt(params);

    // Filter tools for fast mode
    const availableTools = this.filterTools(params);

    // Prepare extra system messages
    const extraSystemMessages = await this.prepareExtraSystemMessages(params);

    return {
      initialMessages: normalizedInitialMessages,
      filteredHistory: normalizedFilteredHistory,
      availableTools,
      systemPrompt,
      extraSystemMessages
    };
  }

  /**
   * Gets notebook context if available
   */
  private static async getNotebookContext(
    params: MessageCreationParams
  ): Promise<string> {
    try {
      if (params.notebookContextManager && params.notebookPath) {
        return params.notebookContextManager.formatContextAsMessage(
          params.notebookPath
        );
      }
    } catch (error) {
      await params.errorLogger?.({
        message: 'Error getting notebook context',
        error: error instanceof Error ? error.message : error,
        notebookPath: params.notebookPath,
        notebookContextManager: !!params.notebookContextManager
      });
    }
    return '';
  }

  /**
   * Prepares initial messages with context
   */
  private static prepareInitialMessages(contextCellsContent: string): any[] {
    const initialMessages = [];

    if (contextCellsContent && contextCellsContent.trim() !== '') {
      initialMessages.push({
        role: 'user',
        content: contextCellsContent
      });
    }

    return initialMessages;
  }

  /**
   * Determines which system prompt to use
   */
  private static determineSystemPrompt(params: MessageCreationParams): string {
    if (params.mode === 'ask') {
      return params.systemPromptAskMode;
    } else if (params.mode === 'fast') {
      return params.systemPromptFastMode;
    }
    return params.systemPrompt;
  }

  /**
   * Filters tools based on fast mode settings
   */
  private static filterTools(params: MessageCreationParams): any[] {
    if (params.isFastMode && params.toolBlacklist.length > 0) {
      return params.tools.filter(
        tool => tool.name && !params.toolBlacklist.includes(tool.name)
      );
    }
    return params.tools;
  }

  /**
   * Prepares extra system messages
   */
  private static async prepareExtraSystemMessages(
    params: MessageCreationParams
  ): Promise<any[]> {
    const extraSystemMessages: any[] = [];

    // Add system prompt messages
    if (params.systemPromptMessages) {
      extraSystemMessages.push(
        ...params.systemPromptMessages.map(msg => ({
          text: msg,
          type: 'text'
        }))
      );
    }

    // Add notebook state
    if (params.fetchNotebookState) {
      try {
        const notebookState = await params.fetchNotebookState();
        if (notebookState) {
          extraSystemMessages.push({
            type: 'text',
            text: `This is the current notebook summary with edit history: ${notebookState}`
          });
        }
      } catch (error) {
        await params.errorLogger?.({
          message: 'Error fetching notebook state',
          error: error instanceof Error ? error.message : error,
          fetchNotebookState: !!params.fetchNotebookState
        });
      }
    }

    return extraSystemMessages;
  }
}
