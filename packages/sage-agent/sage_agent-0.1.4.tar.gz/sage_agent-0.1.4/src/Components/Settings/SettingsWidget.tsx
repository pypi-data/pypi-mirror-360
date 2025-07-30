import * as React from 'react';
import { Widget } from '@lumino/widgets';
import { ReactWidget } from '@jupyterlab/ui-components';
import { Signal, ISignal } from '@lumino/signaling';
import { ToolService } from '../../Services/ToolService';
import { CodebaseManager } from '../../CodebaseManager';
import { AppStateService } from '../../AppState';

/**
 * Interface for the Settings state
 */
export interface ISettingsState {
  isVisible: boolean;
  sageTokenMode: boolean;
  claudeApiKey: string;
  claudeModelId: string;
  claudeModelUrl: string;
  databaseUrl: string;
}

/**
 * React component for displaying Settings content
 */
function SettingsContent({
  isVisible,
  sageTokenMode,
  claudeApiKey,
  claudeModelId,
  claudeModelUrl,
  databaseUrl,
  onTokenModeChange,
  onClaudeApiKeyChange,
  onClaudeModelIdChange,
  onClaudeModelUrlChange,
  onDatabaseUrlChange,
  toolService
}: {
  isVisible: boolean;
  sageTokenMode: boolean;
  claudeApiKey: string;
  claudeModelId: string;
  claudeModelUrl: string;
  databaseUrl: string;
  onTokenModeChange: (enabled: boolean) => void;
  onClaudeApiKeyChange: (value: string) => void;
  onClaudeModelIdChange: (value: string) => void;
  onClaudeModelUrlChange: (value: string) => void;
  onDatabaseUrlChange: (value: string) => void;
  toolService: ToolService;
}): JSX.Element | null {
  const [codebaseManager, setCodebaseManager] =
    React.useState<CodebaseManager | null>(null);
  const codebaseContainerRef = React.useRef<HTMLDivElement>(null);

  // Initialize codebase manager when toolService is available
  React.useEffect(() => {
    if (toolService && codebaseContainerRef.current && !codebaseManager) {
      const manager = new CodebaseManager(toolService);
      setCodebaseManager(manager);
      codebaseContainerRef.current.appendChild(manager.getElement());
    }
  }, [toolService, codebaseManager]);

  // Cleanup codebase manager on unmount
  React.useEffect(() => {
    return () => {
      if (codebaseManager && codebaseContainerRef.current) {
        const element = codebaseManager.getElement();
        if (element.parentNode) {
          element.parentNode.removeChild(element);
        }
      }
    };
  }, [codebaseManager]);

  if (!isVisible) {
    return null;
  }

  const handleTokenModeChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    onTokenModeChange(event.target.checked);
  };

  return (
    <div className="sage-ai-settings-container">
      <h2 className="sage-ai-settings-title">Sage AI Settings</h2>

      {/* Codebase Manager Container */}
      <div ref={codebaseContainerRef} />

      {/* Claude API Configuration */}
      <div className="sage-ai-config-section">
        <h3 className="sage-ai-config-title">Claude API Configuration</h3>

        <div className="sage-ai-field-container">
          <label className="sage-ai-field-label">Claude API Key:</label>
          <input
            type="password"
            value={claudeApiKey}
            onChange={e => onClaudeApiKeyChange(e.target.value)}
            placeholder="Enter your Claude API key"
            className="sage-ai-field-input"
          />
        </div>

        <div className="sage-ai-field-container">
          <label className="sage-ai-field-label">Claude Model ID:</label>
          <input
            type="text"
            value={claudeModelId}
            onChange={e => onClaudeModelIdChange(e.target.value)}
            placeholder="claude-3-7-sonnet-20250219"
            className="sage-ai-field-input"
          />
        </div>

        <div className="sage-ai-field-container">
          <label className="sage-ai-field-label">Claude Model URL:</label>
          <input
            type="text"
            value={claudeModelUrl}
            onChange={e => onClaudeModelUrlChange(e.target.value)}
            placeholder="https://sage.alpinex.ai:8760"
            className="sage-ai-field-input"
          />
        </div>
      </div>

      {/* Database Configuration */}
      <div className="sage-ai-config-section">
        <h3 className="sage-ai-config-title">Database Configuration</h3>

        <div className="sage-ai-field-container">
          <label className="sage-ai-field-label">Database URL:</label>
          <input
            type="text"
            value={databaseUrl}
            onChange={e => onDatabaseUrlChange(e.target.value)}
            placeholder="Enter your database URL"
            className="sage-ai-field-input"
          />
        </div>
      </div>

      {/* Sage Token Mode Checkbox */}
      <div className="sage-token-mode-container">
        <label className="sage-token-mode-label">
          <input
            type="checkbox"
            checked={sageTokenMode}
            onChange={handleTokenModeChange}
            className="sage-token-mode-checkbox"
          />
          <span>Sage Token Debug Mode</span>
        </label>
      </div>
    </div>
  );
}

/**
 * React-based Widget that contains the settings for Sage AI
 */
export class SettingsWidget extends ReactWidget {
  private toolService: ToolService;
  private _state: ISettingsState;
  private _stateChanged = new Signal<this, ISettingsState>(this);
  public static SAGE_TOKEN_MODE: boolean = false;
  private static readonly SAGE_TOKEN_MODE_KEY = 'sage-ai-token-mode';
  private static readonly CLAUDE_API_KEY_KEY = 'sage-ai-claude-api-key';
  private static readonly CLAUDE_MODEL_ID_KEY = 'sage-ai-claude-model-id';
  private static readonly CLAUDE_MODEL_URL_KEY = 'sage-ai-claude-model-url';
  private static readonly DATABASE_URL_KEY = 'sage-ai-database-url';

  constructor(toolService: ToolService) {
    super();

    this.id = 'sage-ai-settings';
    this.title.label = 'Settings';
    this.title.closable = false;
    this.addClass('sage-ai-settings');

    this.toolService = toolService;

    // Load cached settings from localStorage and update AppState
    this.loadAndSyncSettings();

    // Get initial state from AppState
    const appSettings = AppStateService.getClaudeSettings();
    this.loadTokenModeSetting(); // This sets SettingsWidget.SAGE_TOKEN_MODE
    const tokenMode = SettingsWidget.SAGE_TOKEN_MODE;

    // Update AppState with token mode
    AppStateService.updateSettings({ tokenMode });

    // Initialize state
    this._state = {
      isVisible: true,
      sageTokenMode: tokenMode,
      claudeApiKey: appSettings.claudeApiKey,
      claudeModelId: appSettings.claudeModelId,
      claudeModelUrl: appSettings.claudeModelUrl,
      databaseUrl: appSettings.databaseUrl
    };
  }

  /**
   * Get the signal that fires when state changes
   */
  public get stateChanged(): ISignal<this, ISettingsState> {
    return this._stateChanged;
  }

  /**
   * Render the React component
   */
  render(): JSX.Element {
    return (
      <SettingsContent
        isVisible={this._state.isVisible}
        sageTokenMode={this._state.sageTokenMode}
        claudeApiKey={this._state.claudeApiKey}
        claudeModelId={this._state.claudeModelId}
        claudeModelUrl={this._state.claudeModelUrl}
        databaseUrl={this._state.databaseUrl}
        onTokenModeChange={this.handleTokenModeChange.bind(this)}
        onClaudeApiKeyChange={this.handleClaudeApiKeyChange.bind(this)}
        onClaudeModelIdChange={this.handleClaudeModelIdChange.bind(this)}
        onClaudeModelUrlChange={this.handleClaudeModelUrlChange.bind(this)}
        onDatabaseUrlChange={this.handleDatabaseUrlChange.bind(this)}
        toolService={this.toolService}
      />
    );
  }

  /**
   * Load the Sage Token Mode setting from localStorage
   */
  private loadTokenModeSetting(): void {
    const cached = localStorage.getItem(SettingsWidget.SAGE_TOKEN_MODE_KEY);
    if (cached !== null) {
      SettingsWidget.SAGE_TOKEN_MODE = cached === 'true';
    }
  }

  /**
   * Save the Sage Token Mode setting to localStorage
   */
  private saveTokenModeSetting(value: boolean): void {
    localStorage.setItem(SettingsWidget.SAGE_TOKEN_MODE_KEY, value.toString());
  }

  /**
   * Generic method to load a setting from localStorage
   */
  private loadSetting(key: string, defaultValue: string): string {
    return localStorage.getItem(key) || defaultValue;
  }

  /**
   * Generic method to save a setting to localStorage
   */
  private saveSetting(key: string, value: string): void {
    localStorage.setItem(key, value);
  }

  /**
   * Load settings from localStorage and sync with AppState
   */
  private loadAndSyncSettings(): void {
    const claudeApiKey = this.loadSetting(
      SettingsWidget.CLAUDE_API_KEY_KEY,
      ''
    );
    const claudeModelId = this.loadSetting(
      SettingsWidget.CLAUDE_MODEL_ID_KEY,
      'claude-3-7-sonnet-20250219'
    );
    const claudeModelUrl = this.loadSetting(
      SettingsWidget.CLAUDE_MODEL_URL_KEY,
      'https://sage.alpinex.ai:8760'
    );
    const databaseUrl = this.loadSetting(SettingsWidget.DATABASE_URL_KEY, '');

    // Update AppState with loaded settings
    AppStateService.updateClaudeSettings({
      claudeApiKey,
      claudeModelId,
      claudeModelUrl,
      databaseUrl
    });
  }

  /**
   * Handle token mode change
   */
  private handleTokenModeChange(enabled: boolean): void {
    SettingsWidget.SAGE_TOKEN_MODE = enabled;
    this.saveTokenModeSetting(enabled);

    // Update AppState
    AppStateService.updateSettings({ tokenMode: enabled });

    // Update state
    this._state = {
      ...this._state,
      sageTokenMode: enabled
    };

    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Handle Claude API key change
   */
  private handleClaudeApiKeyChange(value: string): void {
    this.saveSetting(SettingsWidget.CLAUDE_API_KEY_KEY, value);

    // Update AppState
    AppStateService.updateClaudeSettings({ claudeApiKey: value });

    this._state = {
      ...this._state,
      claudeApiKey: value
    };

    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Handle Claude model ID change
   */
  private handleClaudeModelIdChange(value: string): void {
    this.saveSetting(SettingsWidget.CLAUDE_MODEL_ID_KEY, value);

    // Update AppState
    AppStateService.updateClaudeSettings({ claudeModelId: value });

    this._state = {
      ...this._state,
      claudeModelId: value
    };

    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Handle Claude model URL change
   */
  private handleClaudeModelUrlChange(value: string): void {
    this.saveSetting(SettingsWidget.CLAUDE_MODEL_URL_KEY, value);

    // Update AppState
    AppStateService.updateClaudeSettings({ claudeModelUrl: value });

    this._state = {
      ...this._state,
      claudeModelUrl: value
    };

    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Handle database URL change
   */
  private handleDatabaseUrlChange(value: string): void {
    this.saveSetting(SettingsWidget.DATABASE_URL_KEY, value);

    // Update AppState
    AppStateService.updateClaudeSettings({ databaseUrl: value });

    this._state = {
      ...this._state,
      databaseUrl: value
    };

    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Show the settings widget
   */
  public show(): void {
    this._state = {
      ...this._state,
      isVisible: true
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Hide the settings widget
   */
  public hide(): void {
    this._state = {
      ...this._state,
      isVisible: false
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Get the current state
   */
  public getState(): ISettingsState {
    return { ...this._state };
  }

  /**
   * Check if the widget is currently visible
   */
  public getIsVisible(): boolean {
    return this._state.isVisible;
  }

  /**
   * Get the current Claude API key
   */
  public getClaudeApiKey(): string {
    return this._state.claudeApiKey;
  }

  /**
   * Get the current Claude model ID
   */
  public getClaudeModelId(): string {
    return this._state.claudeModelId;
  }

  /**
   * Get the current Claude model URL
   */
  public getClaudeModelUrl(): string {
    return this._state.claudeModelUrl;
  }

  /**
   * Get the current database URL
   */
  public getDatabaseUrl(): string {
    return this._state.databaseUrl;
  }

  /**
   * Get all Claude settings as an object
   */
  public getClaudeSettings(): {
    apiKey: string;
    modelId: string;
    modelUrl: string;
  } {
    return {
      apiKey: this._state.claudeApiKey,
      modelId: this._state.claudeModelId,
      modelUrl: this._state.claudeModelUrl
    };
  }

  /**
   * Get the widget for adding to layout (for backwards compatibility)
   */
  public getWidget(): Widget {
    return this;
  }
}
