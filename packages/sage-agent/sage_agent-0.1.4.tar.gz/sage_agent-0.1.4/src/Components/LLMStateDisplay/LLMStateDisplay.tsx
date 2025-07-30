import * as React from 'react';
import { Widget } from '@lumino/widgets';
import { ReactWidget } from '@jupyterlab/ui-components';
import { Signal, ISignal } from '@lumino/signaling';
import { AppStateService } from '../../AppState';
import { LLMStateContent } from './LLMStateContent';
import { ILLMState, LLMDisplayState } from './types';
import { IPendingDiff } from '../../types';

/**
 * Component for displaying LLM processing state above the chat input
 */
export class LLMStateDisplay extends ReactWidget {
  private _state: ILLMState;
  private _stateChanged = new Signal<this, ILLMState>(this);

  constructor() {
    super();
    this._state = {
      isVisible: false,
      state: LLMDisplayState.IDLE,
      text: ''
    };
    this.addClass('sage-ai-llm-state-widget');
    this.addClass('hidden');
  }

  /**
   * Get the signal that fires when state changes
   */
  public get stateChanged(): ISignal<this, ILLMState> {
    return this._stateChanged;
  }

  /**
   * Render the React component
   */
  render(): JSX.Element {
    this.handleIsVisibleChanges(this._state.isVisible);

    return (
      <LLMStateContent
        isVisible={this._state.isVisible}
        state={this._state.state}
        text={this._state.text}
        toolName={this._state.toolName}
        diffs={this._state.diffs}
        waitingForUser={this._state.waitingForUser}
        isRunContext={this._state.isRunContext}
      />
    );
  }

  private handleIsVisibleChanges(isVisible: boolean): void {
    if (isVisible) {
      this.removeClass('hidden');
    } else {
      this.addClass('hidden');
    }
  }

  /**
   * Show the LLM state in generating mode
   * @param text The status text to display
   * @param waitingForUser
   */
  public show(text: string = 'Generating...', waitingForUser?: boolean): void {
    this._state = {
      isVisible: true,
      state: LLMDisplayState.GENERATING,
      text,
      waitingForUser
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Show the LLM state in using tool mode
   * @param toolName The name of the tool being used
   * @param text Optional custom status text
   * @param onCancel Optional callback for canceling the operation
   */
  public showTool(toolName: string, text?: string): void {
    this._state = {
      isVisible: true,
      state: LLMDisplayState.USING_TOOL,
      text: text || '',
      toolName
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Show the diff state with pending diffs using NotebookDiffManager
   * @param notebookPath Optional path to filter diffs for a specific notebook
   * @param isRunContext
   */
  public showDiffsWithManager(
    notebookPath?: string,
    isRunContext?: boolean
  ): void {
    try {
      const diffManager = AppStateService.getNotebookDiffManager();
      const diffs = diffManager.getNotebookDiffsPublic(notebookPath || null);

      if (diffs.length === 0) {
        this.hide();
        return;
      }

      this._state = {
        isVisible: true,
        state: LLMDisplayState.DIFF,
        text: '',
        diffs,
        isRunContext: isRunContext || false
      };
      this._stateChanged.emit(this._state);
      this.update();
    } catch (error) {
      console.warn('Could not show diffs with manager:', error);
      this.hide();
    }
  }

  /**
   * Hide the LLM state display and set to idle
   */
  public hide(): void {
    this._state = {
      isVisible: false,
      state: LLMDisplayState.IDLE,
      text: '',
      waitingForUser: false
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Update the status text without changing visibility (only for generating/tool states)
   * @param text The new status text
   */
  public updateText(text: string): void {
    if (
      !this._state.isVisible ||
      (this._state.state !== LLMDisplayState.GENERATING &&
        this._state.state !== LLMDisplayState.USING_TOOL)
    ) {
      return;
    }

    this._state = {
      ...this._state,
      text
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Update the tool name for using tool state
   * @param toolName The new tool name
   */
  public updateToolName(toolName: string): void {
    if (
      !this._state.isVisible ||
      this._state.state !== LLMDisplayState.USING_TOOL
    ) {
      return;
    }

    this._state = {
      ...this._state,
      toolName
    };
    this._stateChanged.emit(this._state);
    this.update();
  }

  /**
   * Public method to show pending diffs
   * @param notebookPath Optional path to filter diffs for a specific notebook
   */
  public showPendingDiffs(
    notebookPath?: string | null,
    isRunContext?: boolean
  ): void {
    this.showDiffsWithManager(notebookPath || undefined, isRunContext);
  }

  /**
   * Public method to hide pending diffs
   */
  public hidePendingDiffs(): void {
    this.hide();
  }

  /**
   * Public method to check if there are pending diffs to show
   * @param notebookPath Optional path to filter diffs for a specific notebook
   * @returns Boolean indicating if there are pending diffs
   */
  public hasPendingDiffs(notebookPath?: string | null): boolean {
    try {
      const diffManager = AppStateService.getNotebookDiffManager();
      const diffs = diffManager.getNotebookDiffsPublic(notebookPath || null);
      return diffs.length > 0;
    } catch (error) {
      console.warn('Could not check pending diffs:', error);
      return false;
    }
  }

  /**
   * Get the current state
   */
  public getCurrentState(): LLMDisplayState {
    return this._state.state;
  }

  /**
   * Check if currently in diff state
   */
  public isDiffState(): boolean {
    return this._state.state === LLMDisplayState.DIFF;
  }

  /**
   * Check if currently in using tool state
   */
  public isUsingToolState(): boolean {
    return this._state.state === LLMDisplayState.USING_TOOL;
  }

  /**
   * Get the widget for adding to layout (for backwards compatibility)
   */
  public getWidget(): Widget {
    return this;
  }
}
