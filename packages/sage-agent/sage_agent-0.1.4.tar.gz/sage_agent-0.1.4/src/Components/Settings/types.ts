import { ToolService } from '../../Services/ToolService';

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
 * Props for SettingsContent component
 */
export interface SettingsContentProps {
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
}
