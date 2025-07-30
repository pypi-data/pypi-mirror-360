/**
 * Interface for chat message
 */
export interface IChatMessage {
  role: string;
  content: string | any[];
}

/**
 * Interface for tool call
 */
export interface IToolCall {
  id: string;
  name: string;
  input: any;
}

/**
 * Interface for tool result
 */
export interface IToolResult {
  type: string;
  tool_use_id: string;
  content: string;
}

/**
 * Interface for message handler events
 */
export interface IMessageHandlers {
  onUserMessage?: (message: string) => void;
  onAIResponse?: (message: string) => void;
  onSystemMessage?: (message: string) => void;
  onErrorMessage?: (message: string) => void;
  onToolCall?: (toolCalls: IToolCall[]) => void;
  onToolResult?: (toolName: string, result: any) => void;
}

/**
 * Enum representing the status of a chat request
 */
export enum ChatRequestStatus {
  IDLE = 'idle',
  PENDING = 'pending',
  COMPLETED = 'completed',
  ERROR = 'error',
  CANCELLED = 'cancelled',
  RETRYING = 'retrying'
}

/**
 * Interface for AI response with additional metadata
 */
export interface IAIResponse {
  content: any[];
  needsFreshContext?: boolean;
  role: string;
}

/**
 * Interface for diff approval results
 */
export interface IDiffApproval {
  approved: boolean;
  cellIds: string[];
  allApproved: boolean;
  executeCells: boolean;
  executeApprovedCells: boolean; // Flag to indicate if all approved cells should be executed
}

/**
 * Interface for a pending diff in the notebook
 */
export interface IPendingDiff {
  cellId: string;
  type: 'add' | 'edit' | 'remove';
  summary?: string;
  approved?: boolean;
  originalContent?: string;
  newContent?: string;
  updatedCellId?: string; // Track ID changes
  metadata?: any;
  notebookPath?: string | null; // Add notebook path
  userDecision?: 'approved' | 'rejected' | null; // Track user's decision state
}

/**
 * Diff approval status
 */
export enum DiffApprovalStatus {
  PENDING = 'pending',
  APPROVED = 'approved', 
  REJECTED = 'rejected',
  PARTIAL = 'partial'
}

/**
 * Result of applying/handling diffs
 */
export interface IDiffApplicationResult {
  success: boolean;
  status: DiffApprovalStatus;
}

/**
 * Interface for cell tracking metadata
 */
export interface ICellTrackingMetadata {
  trackingId: string;
  createdAt: string;
  lastModified: string;
  origin: 'user' | 'ai' | 'system';
  summary?: string;
}

/**
 * Interface for notebook-specific diff information
 */
export interface INotebookDiffInfo {
  count: number;
  status: DiffApprovalStatus;
}
