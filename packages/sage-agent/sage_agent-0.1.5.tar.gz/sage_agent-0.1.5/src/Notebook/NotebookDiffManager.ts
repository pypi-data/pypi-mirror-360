import { NotebookTools } from './NotebookTools';
import { ActionHistory, ActionType } from '../Chat/ActionHistory';
import { DiffApprovalDialog } from '../Components/DiffApprovalDialog';
import {
  DiffApprovalStatus,
  IDiffApplicationResult,
  IPendingDiff
} from '../types';
import { Widget } from '@lumino/widgets';
import { timeout } from '../utils';
import { AppStateService } from '../AppState';
import { ISignal, Signal } from '@lumino/signaling';

/**
 * Manager for handling notebook diffs and approvals
 */
export class NotebookDiffManager {
  private notebookTools: NotebookTools;
  private actionHistory: ActionHistory;
  private pendingDiffs: Map<string, IPendingDiff> = new Map(); // Map from tracking ID to pending diff record
  private cellIdMapping: Map<string, string> = new Map(); // Map from tracking ID to temporary cell ID after diff display
  public diffApprovalDialog: DiffApprovalDialog;
  private approvalStatus: DiffApprovalStatus = DiffApprovalStatus.PENDING;
  private notebookWidget: Widget | null = null;
  private lastUserApprovalTime: number = 0; // Track when the user last approved changes
  private _shouldRunImmediately: boolean = false; // Track if we should run immediately
  private _shouldExecuteApprovedCells: boolean = false; // Track if we should execute all approved cells
  private currentNotebookPath: string | null = null;

  // Signals for communicating diff state changes
  private _diffStateChanged = new Signal<this, { cellId: string; approved: boolean | undefined; notebookPath?: string | null }>(this);
  private _allDiffsResolved = new Signal<this, { notebookPath?: string | null }>(this);

  constructor(notebookTools: NotebookTools, actionHistory: ActionHistory) {
    this.notebookTools = notebookTools;
    this.actionHistory = actionHistory;
    this.diffApprovalDialog = new DiffApprovalDialog();

    // Set up callbacks for the dialog with direct diff application methods
    this.diffApprovalDialog.setCallbacks({
      onApprove: trackingIds => this.approveDiffs(trackingIds),
      onReject: trackingIds => this.rejectDiffs(trackingIds),
      onApproveAll: notebookPath => this.approveAllDiffs(notebookPath),
      onRejectAll: notebookPath => this.rejectAllDiffs(notebookPath),
      applyApprovedDiffs: notebookPath => this.applyApprovedDiffs(notebookPath),
      handleRejectedDiffs: notebookPath =>
        this.handleRejectedDiffs(notebookPath),
      setExecuteApprovedCells: execute => this.setExecuteApprovedCells(execute),
      onCellIdClick: cellId => this.notebookTools.scrollToCellById(cellId)
    });
  }

  /**
   * Signal emitted when a diff state changes (approved/rejected)
   */
  public get diffStateChanged(): ISignal<this, { cellId: string; approved: boolean | undefined; notebookPath?: string | null }> {
    return this._diffStateChanged;
  }

  /**
   * Signal emitted when all diffs have been resolved
   */
  public get allDiffsResolved(): ISignal<this, { notebookPath?: string | null }> {
    return this._allDiffsResolved;
  }

  /**
   * Set the notebook widget for better positioning of the diff dialog
   */
  public setNotebookWidget(widget: Widget): void {
    this.notebookWidget = widget;
  }

  /**
   * Set the current notebook path context
   * @param notebookPath Path to the notebook
   */
  public setNotebookPath(notebookPath: string | null): void {
    if (this.currentNotebookPath === notebookPath) {
      return; // No change needed
    }

    console.log(
      `[NotebookDiffManager] Setting current notebook path: ${notebookPath}`
    );
    this.currentNotebookPath = notebookPath;

    this.diffApprovalDialog.updateNotebookPath(notebookPath || '');
  }

  /**
   * Get diffs for a specific notebook by filtering the main collection
   * @param notebookPath Path to the notebook
   * @returns Array of diffs for the specified notebook path
   */
  private getNotebookDiffs(notebookPath?: any): IPendingDiff[] {
    // If no path specified, return all diffs
    if (!notebookPath) {
      return Array.from(this.pendingDiffs.values());
    }

    // Filter diffs by notebook path
    return Array.from(this.pendingDiffs.values()).filter(
      diff => diff.notebookPath === notebookPath
    );
  }

  /**
   * Track a cell addition diff and store its info
   * @param notebookPath Optional path to the notebook
   */
  public trackAddCell(
    trackingId: string,
    content: string,
    summary: string,
    notebookPath?: string | null
  ): void {
    // Use current notebook path if none specified
    const path = notebookPath || this.currentNotebookPath;

    this.pendingDiffs.set(trackingId, {
      cellId: trackingId,
      type: 'add',
      newContent: content,
      updatedCellId: trackingId, // Initially the same as trackingId
      metadata: { summary },
      notebookPath: path
    });

    console.log(
      `[NotebookDiffManager] Tracked add diff for cell tracking ID ${trackingId} in notebook ${path || 'current'}`
    );
  }

  /**
   * Track a cell edit diff and store its info
   * @param notebookPath Optional path to the notebook
   */
  public trackEditCell(
    trackingId: string,
    originalContent: string,
    newContent: string,
    summary: string,
    notebookPath?: string | null
  ): void {
    // Use current notebook path if none specified
    const path = notebookPath || this.currentNotebookPath;

    this.pendingDiffs.set(trackingId, {
      cellId: trackingId,
      type: 'edit',
      originalContent,
      newContent,
      updatedCellId: trackingId, // Initially the same as trackingId
      metadata: { summary },
      notebookPath: path
    });

    console.log(
      `[NotebookDiffManager] Tracked edit diff for cell tracking ID ${trackingId} in notebook ${path || 'current'}`
    );
  }

  /**
   * Track a cell removal diff
   * @param notebookPath Optional path to the notebook
   */
  public trackRemoveCell(
    trackingId: string,
    originalContent: string,
    summary: string,
    notebookPath?: string | null
  ): void {
    // Use current notebook path if none specified
    const path = notebookPath || this.currentNotebookPath;

    this.pendingDiffs.set(trackingId, {
      cellId: trackingId,
      type: 'remove',
      originalContent,
      newContent: '', // Empty for remove
      metadata: { summary },
      notebookPath: path
    });

    console.log(
      `[NotebookDiffManager] Tracked remove diff for cell tracking ID ${trackingId} in notebook ${path || 'current'}`
    );
  }

  /**
   * Update the cell ID mapping when a cell ID changes due to diff display
   * @param notebookPath Optional path to the notebook
   */
  public updateCellIdMapping(
    originalCellId: string,
    updatedCellId: string,
    notebookPath?: string | null
  ): void {
    // Update the mapping
    this.cellIdMapping.set(originalCellId, updatedCellId);

    // Also update the pending diff record if it exists
    const diffRecord = this.pendingDiffs.get(originalCellId);
    if (diffRecord) {
      diffRecord.updatedCellId = updatedCellId;
      console.log(
        `[NotebookDiffManager] Updated cell ID mapping: ${originalCellId} → ${updatedCellId}`
      );
    }
  }

  /**
   * Get the current cell model ID using the mapping if available
   * This converts a tracking ID to the current cell model ID
   */
  public getCurrentCellId(trackingId: string): string {
    return this.cellIdMapping.get(trackingId) || trackingId;
  }

  public isDialogOpen(): boolean {
    return this.diffApprovalDialog.isDialogOpen();
  }

  /**
   * Check if there are any pending diffs
   */
  public hasPendingDiffs(): boolean {
    return this.pendingDiffs.size > 0;
  }

  /**
   * Get the number of pending diffs
   */
  public getPendingDiffCount(): number {
    return this.pendingDiffs.size;
  }

  /**
   * Convert pending diffs to the format expected by DiffApprovalDialog
   * @param notebookPath Optional path to filter diffs by notebook
   */
  private getPendingDiffsForDialog(notebookPath?: any): any[] {
    // Get diffs for the specific notebook or all diffs if no path provided
    const diffs = this.getNotebookDiffs(notebookPath);

    return diffs.map(diff => ({
      cellId: diff.cellId,
      operation: diff.type,
      originalContent: diff.originalContent || '',
      newContent: diff.newContent || '',
      summary: diff.metadata?.summary || `${diff.type} cell`,
      notebookPath: diff.notebookPath
    }));
  }

  /**
   * Show the diff approval dialog with proper handling for Jupyter environment
   * @param parentElement Parent element to attach the dialog to
   * @param useEmbeddedMode If true, will use embedded styling for chat context
   * @param isRunContext If true, indicates this approval is in the context of running code
   * @param notebookPath Path to the notebook for filtering diffs
   * @returns Promise resolving to the approval status
   */
  public async showApprovalDialog(
    parentElement: HTMLElement,
    useEmbeddedMode: boolean = false,
    isRunContext: boolean = false,
    notebookPath?: string | null
  ): Promise<DiffApprovalStatus> {
    // Use current notebook path if none specified
    const path = notebookPath || this.currentNotebookPath;

    console.log(
      '[NotebookDiffManager] Showing approval dialog for notebook:',
      path
    );

    // Check if there are any diffs for this notebook path
    const diffs = this.getNotebookDiffs(path);
    if (diffs.length === 0) {
      return DiffApprovalStatus.APPROVED; // No diffs to approve
    }

    // For Jupyter environment, we need to make sure the dialog is properly positioned
    // and doesn't interfere with the notebook UI
    const diffCells = this.getPendingDiffsForDialog(path);

    // Before showing the dialog, ensure we're showing the diff displays
    await this.displayDiffsInCells(path);

    // Use notebook element as parent if available, otherwise document.body
    const notebookElement = this.notebookWidget
      ? this.notebookWidget.node
      : document.body;

    // Choose the parent element based on the mode
    const dialogParent = useEmbeddedMode ? parentElement : notebookElement;

    // Show the dialog and wait for it to complete
    console.log('[NotebookDiffManager] Showing Dialogue');

    const result = await this.diffApprovalDialog.showDialog(
      diffCells,
      dialogParent,
      useEmbeddedMode,
      isRunContext,
      path
    );

    // Store the run immediately flag if present
    if (result.runImmediately) {
      this._shouldRunImmediately = true;
    }

    // Return the current approval status - no need to call applyApprovedDiffs/handleRejectedDiffs
    // as they are now called directly by the dialog
    return this.approvalStatus;
  }

  /**
   * Show approval dialog specifically for cancellation scenario
   * This version shows the dialog with only approve/reject options (no run option)
   * @param parentElement Parent element for the dialog
   * @param notebookPath Path to the notebook for filtering diffs
   * @returns Promise resolving to approval status
   */
  public async showCancellationApprovalDialog(
    parentElement: HTMLElement,
    notebookPath?: string | null
  ): Promise<DiffApprovalStatus> {
    // Use current notebook path if none specified
    const path = notebookPath || this.currentNotebookPath;

    // Check if there are any diffs for this notebook path
    const diffs = this.getNotebookDiffs(path);
    if (diffs.length === 0) {
      return DiffApprovalStatus.APPROVED; // No diffs to approve
    }

    // For Jupyter environment, we need to make sure the dialog is properly positioned
    // and doesn't interfere with the notebook UI
    const diffCells = this.getPendingDiffsForDialog(path);

    // Before showing the dialog, ensure we're showing the diff displays
    await this.displayDiffsInCells(path);

    // Use notebook element as parent if available, otherwise document.body
    const notebookElement = this.notebookWidget
      ? this.notebookWidget.node
      : document.body;

    // Choose the parent element based on embedded mode for chat context
    const dialogParent = parentElement;

    // Show the dialog and wait for it to complete - explicitly set isRunContext to false
    // since this is post-cancellation and shouldn't have a run option
    const result = await this.diffApprovalDialog.showDialog(
      diffCells,
      dialogParent,
      true, // Use embedded mode for chat context
      false, // Not a run context - no "run" option
      path
    );

    // Return the current approval status
    return this.approvalStatus;
  }

  /**
   * Display diffs in their respective cells if they aren't already displayed
   * @param notebookPath Optional path to the notebook containing the cells
   */
  private async displayDiffsInCells(
    notebookPath?: string | null
  ): Promise<void> {
    const path = notebookPath || this.currentNotebookPath;
    const diffs = this.getNotebookDiffs(path);

    for (const diff of diffs) {
      await timeout(200);

      // Skip if already displayed
      if (diff.updatedCellId && diff.updatedCellId !== diff.cellId) {
        continue; // Already displayed
      }

      try {
        // Find the cell by tracking ID in the specific notebook
        const cellInfo = this.notebookTools.findCellByAnyId(diff.cellId, path);
        if (!cellInfo) {
          console.warn(
            `Cannot find cell with tracking ID ${diff.cellId} in notebook ${path || 'current'} to display diff`
          );
          continue;
        }

        // Display the diff based on the operation type
        if (diff.type === 'add') {
          const diffResult = this.notebookTools.display_diff(
            cellInfo.cell,
            '', // Original content is empty for new cells
            diff.newContent || '',
            'add'
          );
        } else if (diff.type === 'edit') {
          const diffResult = this.notebookTools.display_diff(
            cellInfo.cell,
            diff.originalContent || '',
            diff.newContent || '',
            'edit'
          );
        } else if (diff.type === 'remove') {
          const diffResult = this.notebookTools.display_diff(
            cellInfo.cell,
            diff.originalContent || '',
            '', // New content is empty for removes
            'remove'
          );
        }
      } catch (error) {
        console.error(
          `Error displaying diff for cell ${diff.cellId} in notebook ${path}:`,
          error
        );
      }
    }
  }

  /**
   * Approve specific diffs by cell IDs
   */
  private approveDiffs(cellIds: string[]): void {
    for (const cellId of cellIds) {
      const diff = this.pendingDiffs.get(cellId);
      if (diff) {
        diff.approved = true;
        diff.userDecision = 'approved';
        // Emit signal for each approved diff
        this._diffStateChanged.emit({ 
          cellId, 
          approved: true, 
          notebookPath: diff.notebookPath 
        });
      }
    }

    this.checkApprovalStatus();
  }

  /**
   * Reject specific diffs by cell IDs
   */
  private rejectDiffs(cellIds: string[]): void {
    for (const cellId of cellIds) {
      const diff = this.pendingDiffs.get(cellId);
      if (diff) {
        diff.approved = false;
        diff.userDecision = 'rejected';
        // Emit signal for each rejected diff
        this._diffStateChanged.emit({ 
          cellId, 
          approved: false, 
          notebookPath: diff.notebookPath 
        });
      }
    }

    this.checkApprovalStatus();
  }

  /**
   * Approve all pending diffs
   * @param notebookPath Optional path to the notebook to approve diffs for
   */
  private approveAllDiffs(notebookPath: string | null = null): void {
    // Get diffs for the specified notebook or all diffs
    const diffs = this.getNotebookDiffs(notebookPath);

    // Set approved flag on all diffs and emit signals
    for (const diff of diffs) {
      const pendingDiff = this.pendingDiffs.get(diff.cellId);
      if (pendingDiff) {
        pendingDiff.approved = true;
        pendingDiff.userDecision = 'approved';
        // Emit signal for each approved diff
        this._diffStateChanged.emit({ 
          cellId: diff.cellId, 
          approved: true, 
          notebookPath: diff.notebookPath 
        });
      }
    }

    this.approvalStatus = DiffApprovalStatus.APPROVED;
    this.checkApprovalStatus();
  }

  /**
   * Reject all pending diffs
   * @param notebookPath Optional path to the notebook to reject diffs for
   */
  public rejectAllDiffs(notebookPath: string | null = null): void {
    // Get diffs for the specified notebook or all diffs
    const diffs = this.getNotebookDiffs(notebookPath);

    // Set rejected flag on all diffs and emit signals
    for (const diff of diffs) {
      const pendingDiff = this.pendingDiffs.get(diff.cellId);
      if (pendingDiff) {
        pendingDiff.approved = false;
        pendingDiff.userDecision = 'rejected';
        // Emit signal for each rejected diff
        this._diffStateChanged.emit({ 
          cellId: diff.cellId, 
          approved: false, 
          notebookPath: diff.notebookPath 
        });
      }
    }

    this.approvalStatus = DiffApprovalStatus.REJECTED;
    this.checkApprovalStatus();
  }

  /**
   * Check and update the overall approval status
   */
  private checkApprovalStatus(): void {
    let approved = 0;
    let rejected = 0;

    for (const diff of this.pendingDiffs.values()) {
      if (diff.approved === true) {
        approved++;
      } else if (diff.approved === false) {
        rejected++;
      }
    }

    const previousStatus = this.approvalStatus;

    if (approved === this.pendingDiffs.size) {
      this.approvalStatus = DiffApprovalStatus.APPROVED;
    } else if (rejected === this.pendingDiffs.size) {
      this.approvalStatus = DiffApprovalStatus.REJECTED;
    } else if (approved + rejected === this.pendingDiffs.size) {
      this.approvalStatus = DiffApprovalStatus.PARTIAL;
    } else {
      this.approvalStatus = DiffApprovalStatus.PENDING;
    }

    // Emit signal when all diffs are resolved (all approved, all rejected, or mixed but all decided)
    if (previousStatus === DiffApprovalStatus.PENDING && 
        this.approvalStatus !== DiffApprovalStatus.PENDING) {
      this._allDiffsResolved.emit({ notebookPath: this.currentNotebookPath });
    }
  }

  /**
   * Apply all approved diffs
   * @param notebookPath Optional path to the notebook containing the cells
   * @returns Promise resolving to a result object with success status and approval status
   */
  public async applyApprovedDiffs(
    notebookPath?: string | null
  ): Promise<IDiffApplicationResult> {
    const path = notebookPath || this.currentNotebookPath;

    // Filter diffs by notebook path (if specified) and approval status
    const approvedDiffs = Array.from(this.pendingDiffs.values()).filter(
      diff => diff.approved === true && (!path || diff.notebookPath === path)
    );

    console.log(
      `[NotebookDiffManager] Applying ${approvedDiffs.length} approved diffs in notebook ${path || 'current'}`
    );

    try {
      for (const diff of approvedDiffs) {
        await timeout(200);
        const trackingId = diff.cellId; // This is the tracking ID
        // The updatedCellId may be a temporary model ID after displaying diff
        const tempModelId =
          diff.updatedCellId !== diff.cellId ? diff.updatedCellId : undefined;

        console.log('Searching for cell with tracking ID:', trackingId);

        // First try to find cell by tracking ID
        let cellInfo = this.notebookTools.findCellByAnyId(trackingId, path);

        if (!cellInfo) {
          console.error(
            `[NotebookDiffManager] Cannot find cell with tracking ID ${trackingId} in notebook ${path || 'current'} to apply diff`
          );
          continue;
        }

        // Apply the diff based on type
        if (diff.type === 'add' || diff.type === 'edit') {
          // For add and edit, apply directly to the found cell
          const result = this.notebookTools.apply_diff(cellInfo.cell, true);
          if (!result.success) {
            console.error(
              `[NotebookDiffManager] Failed to apply diff to cell with tracking ID ${trackingId}`
            );
            continue;
          }

          // Add to action history with tracking ID for reliable reference
          this.actionHistory.addAction(
            diff.type === 'add' ? ActionType.ADD_CELL : ActionType.EDIT_CELL,
            {
              trackingId: trackingId,
              originalContent: diff.originalContent,
              newContent: diff.newContent,
              summary: diff.metadata?.summary
            },
            `${diff.type === 'add' ? 'Added' : 'Edited'} cell: ${diff.metadata?.summary || trackingId}`
          );
        } else if (diff.type === 'remove') {
          // Add to action history
          this.actionHistory.addAction(
            ActionType.REMOVE_CELLS,
            {
              trackingIds: [trackingId],
              removedCells: [
                {
                  content: diff.originalContent,
                  type: cellInfo.cell.model.type,
                  custom: diff.metadata
                }
              ]
            },
            `Removed cell: ${diff.metadata?.summary || trackingId}`
          );

          this.notebookTools.remove_cells({
            cell_ids: [trackingId],
            remove_from_notebook: true
          });
        }
      }

      // Update the last approval time when changes are successfully applied
      if (approvedDiffs.length > 0) {
        this.lastUserApprovalTime = Date.now();
      }

      // Clear the approved diffs from pending
      for (const diff of approvedDiffs) {
        this.pendingDiffs.delete(diff.cellId);
      }

      // Clear mappings related to approved diffs
      for (const [trackingId, _] of this.cellIdMapping) {
        if (!this.pendingDiffs.has(trackingId)) {
          this.cellIdMapping.delete(trackingId);
        }
      }

      return {
        success: true,
        status: this.approvalStatus
      };
    } catch (error) {
      console.error('Error applying approved diffs:', error);
      return {
        success: false,
        status: this.approvalStatus
      };
    }
  }

  /**
   * Handle rejected diffs (revert them)
   * @param notebookPath Optional path to the notebook containing the cells
   * @returns Promise resolving to a result object with success status and approval status
   */
  public async handleRejectedDiffs(
    notebookPath?: string | null
  ): Promise<IDiffApplicationResult> {
    const path = notebookPath || this.currentNotebookPath;

    // Filter diffs by notebook path (if specified) and rejection status
    const rejectedDiffs = Array.from(this.pendingDiffs.values()).filter(
      diff => diff.approved === false && (!path || diff.notebookPath === path)
    );

    console.log(
      `[NotebookDiffManager] Handling ${rejectedDiffs.length} rejected diffs in notebook ${path || 'current'}`
    );

    try {
      for (const diff of rejectedDiffs) {
        const trackingId = diff.cellId; // This is the tracking ID
        const tempModelId =
          diff.updatedCellId !== diff.cellId ? diff.updatedCellId : undefined;

        // First try to find cell by tracking ID
        let cellInfo = this.notebookTools.findCellByAnyId(trackingId, path);

        // If not found and we have a temporary model ID, try that as fallback
        if (!cellInfo && tempModelId) {
          cellInfo = this.notebookTools.findCellByAnyId(tempModelId);
        }

        if (!cellInfo) {
          console.error(
            `[NotebookDiffManager] Cannot find cell with tracking ID ${trackingId} in notebook ${path || 'current'} to reject diff`
          );
          continue;
        }

        // Handle based on diff type
        if (diff.type === 'add') {
          // For rejected adds, remove the cell
          this.notebookTools.remove_cells({
            cell_ids: [trackingId],
            remove_from_notebook: true
          });
        } else if (diff.type === 'edit') {
          // For rejected edits, revert to original content
          const success = this.notebookTools.apply_diff(cellInfo.cell, false);
          if (!success) {
            console.error(
              `[NotebookDiffManager] Failed to reject diff for cell with tracking ID ${trackingId}`
            );
          }
        } else if (diff.type === 'remove') {
          const success = this.notebookTools.apply_diff(cellInfo.cell, false);
          if (!success) {
            console.error(
              `[NotebookDiffManager] Failed to reject diff for cell with tracking ID ${trackingId}`
            );
          }
          // For rejected removes, do nothing (cell stays)
        }
      }

      // Clear the rejected diffs from pending
      for (const diff of rejectedDiffs) {
        this.pendingDiffs.delete(diff.cellId);
      }

      // Clear mappings related to rejected diffs
      for (const [trackingId, _] of this.cellIdMapping) {
        if (!this.pendingDiffs.has(trackingId)) {
          this.cellIdMapping.delete(trackingId);
        }
      }

      return {
        success: true,
        status: this.approvalStatus
      };
    } catch (error) {
      console.error('Error handling rejected diffs:', error);
      return {
        success: false,
        status: this.approvalStatus
      };
    }
  }

  public async applyAllDiffs() {
    const notebook = AppStateService.getState().currentNotebookPath;
    await this.applyApprovedDiffs(notebook);
    await this.handleRejectedDiffs(notebook);
    this.clearDiffs();
    this.diffApprovalDialog.close(this._shouldRunImmediately);
  }

  /**
   * Clear all pending diffs
   */
  public clearDiffs(): void {
    this.pendingDiffs.clear();
    this.cellIdMapping.clear();
    this.approvalStatus = DiffApprovalStatus.PENDING;
    console.log('[NotebookDiffManager] All diffs cleared');
  }

  /**
   * Check if we should run code immediately after approval
   * This flag is set when "Approve All and Run" is clicked
   * and should be consumed after checking once
   */
  public shouldRunImmediately(): boolean {
    const should = this._shouldRunImmediately;
    this._shouldRunImmediately = false; // Consume the flag
    return should;
  }

  /**
   * Check if we should execute all approved cells after approval
   * This flag is set when "Approve All and Run" is clicked
   * and should be consumed after checking once
   */
  public shouldExecuteApprovedCells(): boolean {
    const should = this._shouldExecuteApprovedCells;
    this._shouldExecuteApprovedCells = false; // Consume the flag
    return should;
  }

  /**
   * Get all approved cell IDs (tracking IDs)
   * @param notebookPath Optional path to filter by notebook
   * @returns Array of approved cell tracking IDs
   */
  public getApprovedCellIds(notebookPath?: string | null): string[] {
    const path = notebookPath || this.currentNotebookPath;
    const approvedCells = Array.from(this.pendingDiffs.values()).filter(
      diff =>
        diff.approved === true &&
        (!path || diff.notebookPath === path) &&
        (diff.type === 'add' || diff.type === 'edit') // Only include cells that can be executed
    );

    return approvedCells.map(diff => diff.cellId);
  }

  /**
   * Set the flag to execute all approved cells
   */
  public setExecuteApprovedCells(execute: boolean): void {
    this._shouldExecuteApprovedCells = execute;
  }

  /**
   * Get diffs for a specific notebook (public method)
   * @param notebookPath Path to the notebook
   * @returns Array of diffs for the specified notebook path
   */
  public getNotebookDiffsPublic(notebookPath?: string | null): IPendingDiff[] {
    return this.getNotebookDiffs(notebookPath);
  }

  /**
   * Approve a single diff by cell ID (public method)
   * @param cellId The cell ID to approve
   */
  public approveDiff(cellId: string): void {
    this.approveDiffs([cellId]);
    this.diffApprovalDialog;
  }

  /**
   * Reject a single diff by cell ID (public method)
   * @param cellId The cell ID to reject
   */
  public rejectDiff(cellId: string): void {
    this.rejectDiffs([cellId]);
  }

  /**
   * Approve all diffs (public method)
   * @param notebookPath Optional path to the notebook
   */
  public approveAllDiffsPublic(notebookPath?: string | null): void {
    this.approveAllDiffs(notebookPath);
  }
}
