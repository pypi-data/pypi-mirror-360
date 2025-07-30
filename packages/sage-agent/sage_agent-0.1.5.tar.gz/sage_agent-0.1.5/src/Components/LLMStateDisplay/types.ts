import { IPendingDiff } from '../../types';

/**
 * Enum for LLM display states
 */
export enum LLMDisplayState {
  IDLE = 'idle',
  GENERATING = 'generating',
  USING_TOOL = 'using_tool',
  DIFF = 'diff'
}

/**
 * Interface for the LLM state
 */
export interface ILLMState {
  isVisible: boolean;
  state: LLMDisplayState;
  text: string;
  toolName?: string; // For USING_TOOL state
  diffs?: IPendingDiff[];
  waitingForUser?: boolean;
  isRunContext?: boolean; // For DIFF state, indicates if run context is being shown
}

/**
 * Props for DiffItem component
 */
export interface DiffItemProps {
  diff: IPendingDiff;
  showActionsOnHover?: boolean;
}
