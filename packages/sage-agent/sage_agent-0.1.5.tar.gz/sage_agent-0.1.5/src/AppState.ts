import { BehaviorSubject } from 'rxjs';
import { INotebookTracker } from '@jupyterlab/notebook';
import { Contents } from '@jupyterlab/services';
import { ToolService } from './Services/ToolService';
import { NotebookTools } from './Notebook/NotebookTools';
import { NotebookContextManager } from './Notebook/NotebookContextManager';
import { PlanStateDisplay } from './Components/PlanStateDisplay';
import { WaitingUserReplyBoxManager } from './Notebook/WaitingUserReplyBoxManager';
import { ActionHistory } from './Chat/ActionHistory';
import { NotebookDiffManager } from './Notebook/NotebookDiffManager';
import { CellTrackingService } from './CellTrackingService';
import { TrackingIDUtility } from './TrackingIDUtility';
import { ContextCellHighlighter } from './Notebook/ContextCellHighlighter';
import { NotebookChatContainer } from './Notebook/NotebookChatContainer';

interface AppState {
  // Core services
  toolService: ToolService | null;
  notebookTracker: INotebookTracker | null;
  notebookTools: NotebookTools | null;
  notebookContextManager: NotebookContextManager | null;
  contentManager: Contents.IManager | null;

  // Managers
  planStateDisplay: PlanStateDisplay | null;
  waitingUserReplyBoxManager: WaitingUserReplyBoxManager | null;
  notebookDiffManager: NotebookDiffManager | null;

  // Additional services
  actionHistory: ActionHistory | null;
  cellTrackingService: CellTrackingService | null;
  trackingIDUtility: TrackingIDUtility | null;
  contextCellHighlighter: ContextCellHighlighter | null;

  // UI Containers
  chatContainer: NotebookChatContainer | null;

  // Application state
  currentNotebookPath: string | null;
  isInitialized: boolean;

  // Settings
  settings: {
    theme: string;
    tokenMode: boolean;
    claudeApiKey: string;
    claudeModelId: string;
    claudeModelUrl: string;
    databaseUrl: string;
  };
}

const initialState: AppState = {
  // Core services
  toolService: null,
  notebookTracker: null,
  notebookTools: null,
  notebookContextManager: null,
  contentManager: null,

  // Managers
  planStateDisplay: null,
  waitingUserReplyBoxManager: null,
  notebookDiffManager: null,

  // Additional services
  actionHistory: null,
  cellTrackingService: null,
  trackingIDUtility: null,
  contextCellHighlighter: null,

  // UI Containers
  chatContainer: null,

  // Application state
  currentNotebookPath: null,
  isInitialized: false,

  // Settings
  settings: {
    theme: 'light',
    tokenMode: false,
    claudeApiKey: '',
    claudeModelId: 'claude-3-7-sonnet-20250219',
    claudeModelUrl: 'https://sage.alpinex.ai:8760',
    databaseUrl: ''
  }
};

const state$ = new BehaviorSubject<AppState>(initialState);

export const AppStateService = {
  /**
   * Get the current application state
   */
  getState: () => state$.getValue(),

  /**
   * Update the application state with partial values
   */
  setState: (partial: Partial<AppState>) =>
    state$.next({ ...state$.getValue(), ...partial }),

  /**
   * Subscribe to state changes
   */
  changes: state$.asObservable(),

  /**
   * Initialize core services
   */
  initializeCoreServices: (
    toolService: ToolService,
    notebookTracker: INotebookTracker,
    notebookTools: NotebookTools,
    notebookContextManager: NotebookContextManager,
    contentManager: Contents.IManager
  ) => {
    AppStateService.setState({
      toolService,
      notebookTracker,
      notebookTools,
      notebookContextManager,
      contentManager
    });
  },

  /**
   * Initialize managers
   */
  initializeManagers: (
    planStateDisplay: PlanStateDisplay,
    waitingUserReplyBoxManager: WaitingUserReplyBoxManager,
    notebookDiffManager?: NotebookDiffManager
  ) => {
    AppStateService.setState({
      planStateDisplay,
      waitingUserReplyBoxManager,
      notebookDiffManager
    });
  },

  /**
   * Initialize additional services
   */
  initializeAdditionalServices: (
    actionHistory: ActionHistory,
    cellTrackingService: CellTrackingService,
    trackingIDUtility: TrackingIDUtility,
    contextCellHighlighter: ContextCellHighlighter
  ) => {
    AppStateService.setState({
      actionHistory,
      cellTrackingService,
      trackingIDUtility,
      contextCellHighlighter
    });
  },

  /**
   * Mark the application as initialized
   */
  markAsInitialized: () => {
    AppStateService.setState({ isInitialized: true });
  },

  /**
   * Update the current notebook path
   */
  setCurrentNotebookPath: (notebookPath: string | null) => {
    AppStateService.setState({ currentNotebookPath: notebookPath });
  },

  /**
   * Update settings
   */
  updateSettings: (settings: Partial<AppState['settings']>) => {
    const currentState = AppStateService.getState();
    AppStateService.setState({
      settings: { ...currentState.settings, ...settings }
    });
  },

  /**
   * Update Claude settings specifically
   */
  updateClaudeSettings: (settings: {
    claudeApiKey?: string;
    claudeModelId?: string;
    claudeModelUrl?: string;
    databaseUrl?: string;
  }) => {
    const currentState = AppStateService.getState();
    AppStateService.setState({
      settings: { ...currentState.settings, ...settings }
    });
  },

  /**
   * Get Claude settings
   */
  getClaudeSettings: (): {
    claudeApiKey: string;
    claudeModelId: string;
    claudeModelUrl: string;
    databaseUrl: string;
  } => {
    const { settings } = AppStateService.getState();
    return {
      claudeApiKey: settings.claudeApiKey,
      claudeModelId: settings.claudeModelId,
      claudeModelUrl: settings.claudeModelUrl,
      databaseUrl: settings.databaseUrl
    };
  },

  /**
   * Get Claude API key
   */
  getClaudeApiKey: (): string => {
    return AppStateService.getState().settings.claudeApiKey;
  },

  /**
   * Get Claude model URL
   */
  getClaudeModelUrl: (): string => {
    return AppStateService.getState().settings.claudeModelUrl;
  },

  /**
   * Get Claude model ID
   */
  getClaudeModelId: (): string => {
    return AppStateService.getState().settings.claudeModelId;
  },

  /**
   * Get a specific service safely
   */
  getToolService: (): ToolService => {
    const toolService = AppStateService.getState().toolService;
    if (!toolService) {
      throw new Error('ToolService not initialized in AppState');
    }
    return toolService;
  },

  getNotebookTracker: (): INotebookTracker => {
    const notebookTracker = AppStateService.getState().notebookTracker;
    if (!notebookTracker) {
      throw new Error('NotebookTracker not initialized in AppState');
    }
    return notebookTracker;
  },

  getNotebookTools: (): NotebookTools => {
    const notebookTools = AppStateService.getState().notebookTools;
    if (!notebookTools) {
      throw new Error('NotebookTools not initialized in AppState');
    }
    return notebookTools;
  },

  getNotebookContextManager: (): NotebookContextManager => {
    const notebookContextManager =
      AppStateService.getState().notebookContextManager;
    if (!notebookContextManager) {
      throw new Error('NotebookContextManager not initialized in AppState');
    }
    return notebookContextManager;
  },

  getContentManager: (): Contents.IManager => {
    const contentManager = AppStateService.getState().contentManager;
    if (!contentManager) {
      throw new Error('ContentManager not initialized in AppState');
    }
    return contentManager;
  },

  getPlanStateDisplay: (): PlanStateDisplay => {
    const planStateDisplay = AppStateService.getState().planStateDisplay;
    if (!planStateDisplay) {
      throw new Error('PlanStateDisplay not initialized in AppState');
    }
    return planStateDisplay;
  },

  getWaitingUserReplyBoxManager: (): WaitingUserReplyBoxManager => {
    const waitingUserReplyBoxManager =
      AppStateService.getState().waitingUserReplyBoxManager;
    if (!waitingUserReplyBoxManager) {
      throw new Error('WaitingUserReplyBoxManager not initialized in AppState');
    }
    return waitingUserReplyBoxManager;
  },

  getActionHistory: (): ActionHistory => {
    const actionHistory = AppStateService.getState().actionHistory;
    if (!actionHistory) {
      throw new Error('ActionHistory not initialized in AppState');
    }
    return actionHistory;
  },

  getCellTrackingService: (): CellTrackingService => {
    const cellTrackingService = AppStateService.getState().cellTrackingService;
    if (!cellTrackingService) {
      throw new Error('CellTrackingService not initialized in AppState');
    }
    return cellTrackingService;
  },

  getNotebookDiffManager: (): NotebookDiffManager => {
    const notebookDiffManager = AppStateService.getState().notebookDiffManager;
    if (!notebookDiffManager) {
      throw new Error('NotebookDiffManager not initialized in AppState');
    }
    return notebookDiffManager;
  },

  getTrackingIDUtility: (): TrackingIDUtility => {
    const trackingIDUtility = AppStateService.getState().trackingIDUtility;
    if (!trackingIDUtility) {
      throw new Error('TrackingIDUtility not initialized in AppState');
    }
    return trackingIDUtility;
  },

  getContextCellHighlighter: (): ContextCellHighlighter => {
    const contextCellHighlighter =
      AppStateService.getState().contextCellHighlighter;
    if (!contextCellHighlighter) {
      throw new Error('ContextCellHighlighter not initialized in AppState');
    }
    return contextCellHighlighter;
  },

  getChatContainer: (): NotebookChatContainer => {
    const chatContainer = AppStateService.getState().chatContainer;
    if (!chatContainer) {
      throw new Error('ChatContainer not initialized in AppState');
    }
    return chatContainer;
  },

  /**
   * Set the chat container
   */
  setChatContainer: (chatContainer: NotebookChatContainer) => {
    AppStateService.setState({ chatContainer });
  },

  /**
   * Get the chat container safely (returns null if not initialized)
   */
  getChatContainerSafe: (): NotebookChatContainer | null => {
    return AppStateService.getState().chatContainer;
  },

  /**
   * Update chat container with new notebook path
   */
  updateChatContainerNotebookPath: (oldPath: string, newPath: string) => {
    const chatContainer = AppStateService.getState().chatContainer;
    if (chatContainer && !chatContainer.isDisposed) {
      chatContainer.updateNotebookPath(oldPath, newPath);
    }
  },

  /**
   * Switch chat container to a notebook
   */
  switchChatContainerToNotebook: (notebookPath: string) => {
    const chatContainer = AppStateService.getState().chatContainer;
    if (chatContainer && !chatContainer.isDisposed) {
      chatContainer.switchToNotebook(notebookPath);
    }
  }
};

// Example usage:

// Read from state
// const { toolService, settings } = AppStateService.getState();

// Update state
// AppStateService.setState({ currentNotebookPath: '/path/to/notebook.ipynb' });

// Subscribe to changes
// AppStateService.changes.subscribe(state => {
//   console.log('New state!', state);
// });

// Use convenience methods
// const toolService = AppStateService.getToolService();
// AppStateService.updateSettings({ theme: 'dark' });
