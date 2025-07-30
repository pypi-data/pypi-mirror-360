import { AppStateService } from '../AppState';
/**
 * Interface for model configuration data
 */
export interface IModelConfig {
  system_prompt: string;
  model_name: string;
  model_url: string;
  api_key: string;
  tool_blacklist?: string[];
}

/**
 * Combined configuration interface
 */
export interface IConfig {
  claude: IModelConfig;
  claude_ask_mode: IModelConfig;
  quick_edit: IModelConfig;
  fast_mode: IModelConfig;
  active_model_type?: string;
}

/**
 * Service for managing local configuration data
 */
export class ConfigService {
  private static activeModelType: string = 'claude'; // Default to claude

  /**
   * Get the active model type
   */
  public static getActiveModelType(): string {
    return this.activeModelType;
  }

  /**
   * Set the active model type
   */
  public static setActiveModelType(modelType: string): void {
    this.activeModelType = modelType;
  }

  /**
   * Get hardcoded model configurations
   */
  private static getModelConfigurations(): Record<
    string,
    { model_name: string; tool_blacklist: string[] }
  > {
    return {
      claude: {
        model_name: 'claude-sonnet-4-20250514',
        tool_blacklist: []
      },
      claude_ask_mode: {
        model_name: 'claude-sonnet-4-20250514',
        tool_blacklist: []
      },
      quick_edit: {
        model_name: 'claude-sonnet-4-20250514',
        tool_blacklist: ['notebook-read_notebook_summary']
      },
      fast_mode: {
        model_name: 'claude-sonnet-4-20250514',
        tool_blacklist: [
          'codebase-list_repos',
          'notebook-edit_plan',
          'notebook-get_cell_info',
          'notebook-read_cells',
          'web-search_dataset',
          'web-download_dataset',
          'filesystem-read_dataset',
          'filesystem-list_datasets',
          'filesystem-delete_dataset',
          'notebook-read_notebook_summary',
          'notebook-wait_user_reply'
        ]
      }
    };
  }

  /**
   * Build configuration for a specific model type
   */
  private static async buildModelConfig(
    modelType: string,
    modelUrl: string,
    apiKey: string
  ): Promise<IModelConfig> {
    const modelConfigs = this.getModelConfigurations();
    const modelConfig = modelConfigs[modelType];

    if (!modelConfig) {
      throw new Error(`Unknown model type: ${modelType}`);
    }

    const system_prompt = require(
      `./prompts/${this.getPromptFileName(modelConfig.model_name)}.md`
    );

    return {
      system_prompt,
      model_name: modelConfig.model_name,
      model_url: modelUrl,
      api_key: apiKey,
      tool_blacklist: modelConfig.tool_blacklist || []
    };
  }

  /**
   * Get the prompt file name for a model type
   */
  private static getPromptFileName(modelType: string): string {
    switch (modelType) {
      case 'claude':
        return 'claude_system_prompt';
      case 'claude_ask_mode':
        return 'claude_system_prompt_ask_mode';
      case 'quick_edit':
        return 'claude_system_prompt_cell_edit_mode';
      case 'fast_mode':
        return 'claude_system_prompt_fast_mode';
      default:
        return 'claude_system_prompt';
    }
  }

  /**
   * Get configuration with model settings
   */
  public static async getConfig(
    modelUrl: string = '',
    apiKey: string = ''
  ): Promise<IConfig> {
    try {
      // If no explicit parameters provided, get from AppState
      if (!modelUrl || !apiKey) {
        const claudeSettings = AppStateService.getClaudeSettings();
        modelUrl = modelUrl || claudeSettings.claudeModelUrl;
        apiKey = apiKey || claudeSettings.claudeApiKey;
      }

      const config: IConfig = {
        claude: await this.buildModelConfig('claude', modelUrl, apiKey),
        claude_ask_mode: await this.buildModelConfig(
          'claude_ask_mode',
          modelUrl,
          apiKey
        ),
        quick_edit: await this.buildModelConfig('quick_edit', modelUrl, apiKey),
        fast_mode: await this.buildModelConfig('fast_mode', modelUrl, apiKey),
        active_model_type: this.activeModelType
      };

      return config;
    } catch (error) {
      console.error('Error building configuration:', error);
      // Return a minimal default configuration if building fails
      return this.getDefaultConfig();
    }
  }

  public static async getTools() {
    return require('./tools.json');
  }

  /**
   * Get default configuration (fallback)
   */
  private static getDefaultConfig(): IConfig {
    return {
      claude: {
        system_prompt:
          'You are a world-class data scientist and quantitative analyst.',
        model_name: 'claude-3-7-sonnet-20250219',
        model_url: '',
        api_key: '',
        tool_blacklist: []
      },
      claude_ask_mode: {
        system_prompt:
          'You are a world-class data scientist and quantitative analyst.',
        model_name: 'claude-3-7-sonnet-20250219',
        model_url: '',
        api_key: '',
        tool_blacklist: []
      },
      quick_edit: {
        system_prompt:
          'You are a world-class data scientist and quantitative analyst.',
        model_name: 'claude-3-7-sonnet-20250219',
        model_url: '',
        api_key: '',
        tool_blacklist: ['notebook-read_notebook_summary']
      },
      fast_mode: {
        system_prompt:
          'You are a world-class data scientist and quantitative analyst.',
        model_name: 'claude-3-7-sonnet-20250219',
        model_url: '',
        api_key: '',
        tool_blacklist: [
          'codebase-list_repos',
          'notebook-edit_plan',
          'notebook-get_cell_info',
          'notebook-read_cells',
          'web-search_dataset',
          'web-download_dataset',
          'filesystem-read_dataset',
          'filesystem-list_datasets',
          'filesystem-delete_dataset',
          'notebook-read_notebook_summary',
          'notebook-wait_user_reply'
        ]
      },
      active_model_type: 'claude'
    };
  }
}
