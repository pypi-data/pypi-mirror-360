import { NotebookDiffTools } from '../Notebook/NotebookDiffTools';
import { IDiffApplicationResult } from '../types';
import { AppStateService } from '../AppState';

export interface IDiffCell {
  cellId: string; // Now represents the tracking ID
  operation: 'add' | 'edit' | 'remove';
  summary: string;
  approved?: boolean;
  originalContent?: string;
  newContent?: string;
  notebookPath?: string | null; // Add notebook path for filtering
}

/**
 * Dialog callbacks interface
 */
interface IDiffApprovalCallbacks {
  onApprove: (trackingIds: string[]) => void;
  onReject: (trackingIds: string[]) => void;
  onApproveAll: (notebookPath: string | null) => void;
  onRejectAll: (notebookPath: string | null) => void;
  applyApprovedDiffs: (
    notebookPath: string | null
  ) => Promise<IDiffApplicationResult>;
  handleRejectedDiffs: (
    notebookPath: string | null
  ) => Promise<IDiffApplicationResult>;
  setExecuteApprovedCells: (execute: boolean) => void; // Add new callback
  onCellIdClick: (cellId: string) => void;
}

/**
 * A dialog for approving/rejecting cell diffs
 */
export class DiffApprovalDialog {
  private dialogElement: HTMLElement | null = null;
  private parentElement: HTMLElement | null = null;
  private callbacks: IDiffApprovalCallbacks | null = null;
  private diffCells: IDiffCell[] = [];
  private resolvePromise:
    | ((value: { approved: boolean; runImmediately: boolean }) => void)
    | null = null;
  private embedded: boolean = false;
  private isRunContext: boolean = false;
  private currentNotebookPath: string | null = null;
  private cellButtonElements: Map<
    string,
    { approveButton: HTMLElement; rejectButton: HTMLElement }
  > = new Map();

  /**
   * Set callbacks for the dialog actions
   */
  public setCallbacks(callbacks: IDiffApprovalCallbacks): void {
    this.callbacks = callbacks;
  }

  public updateNotebookPath(newPath: string): void {
    this.currentNotebookPath = newPath;
  }

  /**
   * Show the approval dialog for the given cells
   * @param diffCells Array of cells with pending diffs
   * @param parentElement The parent element to attach the dialog to
   * @param embedded Whether to use embedded styling for chat context
   * @param isRunContext Whether this approval is in the context of running code
   * @param notebookPath Path of the current notebook for filtering diffs
   * @returns Promise that resolves when approvals are complete with status and run flag
   */
  public async showDialog(
    diffCells: IDiffCell[],
    parentElement: HTMLElement,
    embedded: boolean = false,
    isRunContext: boolean = false,
    notebookPath: string | null = null
  ): Promise<{ approved: boolean; runImmediately: boolean }> {
    this.diffCells = diffCells.filter(
      cell =>
        // Filter cells to only show those for the current notebook
        notebookPath === null ||
        cell.notebookPath === null ||
        cell.notebookPath === notebookPath
    );
    this.parentElement = parentElement;
    this.embedded = embedded;
    this.isRunContext = isRunContext;
    this.currentNotebookPath = notebookPath;

    // Create dialog element
    this.createDialog();
    const llmStateDisplay =
      AppStateService.getChatContainerSafe()?.chatWidget.llmStateDisplay;
    if (llmStateDisplay) {
      llmStateDisplay.showPendingDiffs(notebookPath, isRunContext);
    }

    // Auto-scroll to show the dialog if embedded
    if (this.embedded && this.dialogElement) {
      setTimeout(() => {
        this.dialogElement?.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest'
        });
        this.parentElement!.scrollTop = this.parentElement!.scrollHeight;
      }, 100);
    }

    // Return a promise that will be resolved when the dialog is completed
    return new Promise<{ approved: boolean; runImmediately: boolean }>(
      resolve => {
        this.resolvePromise = resolve;
      }
    );
  }

  public isDialogOpen(): boolean {
    return this.dialogElement !== null;
  }

  /**
   * Create the dialog UI
   */
  private createDialog(): void {
    if (!this.parentElement) {
      console.error('Parent element not provided for diff approval dialog');
      return;
    }

    // Create the dialog container with appropriate class
    this.dialogElement = document.createElement('div');
    this.dialogElement.className = this.embedded
      ? 'sage-ai-diff-approval-dialog-embedded'
      : 'sage-ai-diff-approval-dialog';

    // Add description
    const description = document.createElement('p');
    const notebookLabel = this.currentNotebookPath
      ? ` in notebook "${this.currentNotebookPath.split('/').pop()}"`
      : '';
    description.textContent = `Review and approve/reject the following changes${notebookLabel}:`;
    if (this.embedded) {
      description.className = 'sage-ai-diff-summary';
    }

    // Create the list of diff cells
    const diffList = document.createElement('div');
    diffList.className = 'sage-ai-diff-list';

    // Add each diff cell to the list
    this.diffCells.forEach(diffCell => {
      const cellItem = this.createDiffCellItem(diffCell);
      diffList.appendChild(cellItem);
    });

    this.dialogElement.appendChild(diffList);

    // Create bottom action buttons
    const actionButtons = document.createElement('div');
    actionButtons.className = this.embedded
      ? 'sage-ai-inline-diff-actions'
      : 'sage-ai-diff-approval-actions';

    // Reject all button
    const rejectAllButton = document.createElement('button');
    rejectAllButton.className = 'sage-ai-reject-button';
    rejectAllButton.textContent = 'Reject All';
    rejectAllButton.onclick = () => this.rejectAll();

    // Approve all button - change text if in run context
    const approveAllButton = document.createElement('button');
    approveAllButton.className = 'sage-ai-confirm-button';
    approveAllButton.textContent = this.isRunContext
      ? 'Approve All and Run'
      : 'Approve All';
    approveAllButton.onclick = () => this.approveAll();

    actionButtons.appendChild(rejectAllButton);
    actionButtons.appendChild(approveAllButton);

    this.dialogElement.appendChild(actionButtons);

    // Add the dialog to the parent element
    this.parentElement.appendChild(this.dialogElement);
  }

  /**
   * Create a diff cell item for the dialog
   */
  private createDiffCellItem(diffCell: IDiffCell): HTMLElement {
    const cellItem = document.createElement('div');
    cellItem.className = 'sage-ai-diff-cell-item';
    cellItem.dataset.cellId = diffCell.cellId; // Store tracking ID in data attribute

    // Create header with summary and type
    const cellHeader = document.createElement('div');
    cellHeader.className = 'sage-ai-diff-cell-header';

    const diffContentCollapseIcon = document.createElement('span');
    diffContentCollapseIcon.className = 'sage-ai-diff-content-collapse-icon';
    diffContentCollapseIcon.innerHTML = COLLAPSE_ICON;
    diffContentCollapseIcon.onclick = () =>
      (diffContent.style.display =
        diffContent.style.display === 'none' ? 'block' : 'none');
    cellHeader.appendChild(diffContentCollapseIcon);

    const cellIdLabel = document.createElement('span');
    cellIdLabel.className = 'sage-ai-diff-cell-id-label';
    cellIdLabel.textContent = diffCell.cellId;
    cellIdLabel.onclick = () => this.callbacks?.onCellIdClick(diffCell.cellId);
    cellHeader.appendChild(cellIdLabel);

    cellItem.appendChild(cellHeader);

    // Create diff content display with collapse/expand functionality
    const diffContent = document.createElement('div');
    diffContent.className = 'sage-ai-diff-content';
    diffContent.title = 'Click to expand/collapse diff content';

    diffContent.innerHTML = NotebookDiffTools.generateHtmlDiff(
      diffCell.originalContent || '',
      diffCell.newContent || ''
    );

    const isContentClickable = diffContent.querySelectorAll('tr').length > 9;
    if (isContentClickable) {
      diffContent.style.cursor = 'pointer';

      // Create gradient overlay that stays at bottom when scrolling
      const gradientOverlay = document.createElement('div');
      gradientOverlay.className = 'sage-ai-diff-gradient-overlay';

      // Add scroll event listener to hide gradient when near bottom
      diffContent.addEventListener('scroll', () => {
        const scrollTop = diffContent.scrollTop;
        const scrollHeight = diffContent.scrollHeight;
        const clientHeight = diffContent.clientHeight;
        const distanceFromBottom = scrollHeight - scrollTop - clientHeight;

        if (distanceFromBottom <= 20) {
          gradientOverlay.style.display = 'none';
        } else {
          gradientOverlay.style.display = 'block';
        }
      });

      // Add click handler to the entire diff content area
      diffContent.onclick = () => {
        const isExpanded = diffContent.classList.contains(
          'sage-ai-diff-expanded'
        );

        if (isExpanded) {
          diffContent.classList.remove('sage-ai-diff-expanded');
          diffContent.title = 'Click to expand diff content';
          gradientOverlay.style.display = 'block';
        } else {
          diffContent.classList.add('sage-ai-diff-expanded');
          diffContent.title = 'Click to collapse diff content';
          gradientOverlay.style.display = 'none';
        }
      };

      // Append the gradient overlay to the diff content
      diffContent.appendChild(gradientOverlay);
    }

    cellItem.appendChild(diffContent);

    // Create hover buttons container
    const hoverButtons = document.createElement('div');
    hoverButtons.className = 'sage-ai-diff-hover-buttons';

    // Create approve button
    const approveButton = document.createElement('button');
    approveButton.className = 'sage-ai-diff-approve-button';
    approveButton.innerHTML = `<svg width="15" height="16" viewBox="0 0 15 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12.5 4.25L5.625 11.125L2.5 8" stroke="#22C55E" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`;
    approveButton.title = 'Approve this change';
    approveButton.style.cssText = `
      background-color: transparent;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-weight: bold;
    `;

    // Create reject button
    const rejectButton = document.createElement('button');
    rejectButton.className = 'sage-ai-diff-reject-button';
    rejectButton.innerHTML = `<svg width="15" height="16" viewBox="0 0 15 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M11.25 4.25L3.75 11.75M3.75 4.25L11.25 11.75" stroke="#FF2323" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`;
    rejectButton.title = 'Reject this change';
    rejectButton.style.cssText = `
      background-color: transparent;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 12px;
      font-weight: bold;
    `;

    const copyButton = document.createElement('button');
    copyButton.className = 'sage-ai-diff-copy-button';
    copyButton.innerHTML = `<svg width="15" height="16" viewBox="0 0 15 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M2.5 10.5C1.8125 10.5 1.25 9.9375 1.25 9.25V3C1.25 2.3125 1.8125 1.75 2.5 1.75H8.75C9.4375 1.75 10 2.3125 10 3M6.25 5.5H12.5C13.1904 5.5 13.75 6.05964 13.75 6.75V13C13.75 13.6904 13.1904 14.25 12.5 14.25H6.25C5.55964 14.25 5 13.6904 5 13V6.75C5 6.05964 5.55964 5.5 6.25 5.5Z" stroke="#949494" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`;
    copyButton.title = 'Copy the cell';
    copyButton.style.cssText = `
      background-color: transparent;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 12px;
      font-weight: bold;
    `;

    copyButton.onclick = e => {
      e.stopPropagation();
      diffCell.newContent && navigator.clipboard.writeText(diffCell.newContent);
    };

    // Add click handlers
    approveButton.onclick = e => {
      e.stopPropagation();
      this.approveCell(diffCell.cellId);
    };

    rejectButton.onclick = e => {
      e.stopPropagation();
      this.rejectCell(diffCell.cellId);
    };

    hoverButtons.appendChild(rejectButton);
    hoverButtons.appendChild(approveButton);
    diffCell.operation !== 'remove' && hoverButtons.appendChild(copyButton);

    // Store button references for styling updates
    this.cellButtonElements.set(diffCell.cellId, {
      approveButton,
      rejectButton
    });

    // Set relative positioning for the cell item to contain absolute positioned elements
    cellItem.style.position = 'relative';

    cellHeader.appendChild(hoverButtons);

    return cellItem;
  }

  /**
   * Approve a specific cell
   */
  public approveCell(trackingId: string): void {
    if (this.callbacks) {
      this.callbacks.onApprove([trackingId]);

      // Update the UI to show the cell is approved
      const cellElement = this.dialogElement?.querySelector(
        `[data-cell-id="${trackingId}"]`
      );
      if (cellElement) {
        cellElement.classList.add('sage-ai-diff-approved');
      }

      // Update button styles
      const buttons = this.cellButtonElements.get(trackingId);
      if (buttons) {
        buttons.approveButton.style.opacity = '0.6';
        buttons.rejectButton.style.opacity = '0';
      }

      this.callbacks.applyApprovedDiffs(this.currentNotebookPath);

      // Check if all cells are now approved
      this.checkAllCellsStatus();
    }
  }

  /**
   * Reject a specific cell
   */
  public rejectCell(trackingId: string): void {
    if (this.callbacks) {
      this.callbacks.onReject([trackingId]);

      // Update the UI to show the cell is rejected
      const cellElement = this.dialogElement?.querySelector(
        `[data-cell-id="${trackingId}"]`
      );
      if (cellElement) {
        cellElement.classList.add('sage-ai-diff-rejected');
      }

      // Update button styles
      const buttons = this.cellButtonElements.get(trackingId);
      if (buttons) {
        buttons.rejectButton.style.opacity = '0.6';
        buttons.approveButton.style.opacity = '0';
      }

      this.callbacks.handleRejectedDiffs(this.currentNotebookPath);

      // Check if all cells are now handled
      this.checkAllCellsStatus();
    }
  }

  /**
   * Approve all cells
   */
  public async approveAll(): Promise<void> {
    if (this.callbacks) {
      const loadingOverlay = this.showLoadingOverlay('Applying changes...');

      try {
        this.callbacks.onApproveAll(this.currentNotebookPath);

        // If in run context, set the flag to execute all approved cells
        if (this.isRunContext) {
          this.callbacks.setExecuteApprovedCells(true);
        }

        // Apply the diffs immediately
        await this.callbacks.applyApprovedDiffs(this.currentNotebookPath);
        this.close(true);
      } catch (error) {
        console.error('Error applying approved diffs:', error);
        this.showError('Failed to apply changes. Please try again.');
      } finally {
        if (loadingOverlay && this.dialogElement?.contains(loadingOverlay)) {
          this.dialogElement.removeChild(loadingOverlay);
        }
      }
    }
  }

  /**
   * Reject all cells
   */
  public async rejectAll(): Promise<void> {
    if (this.callbacks) {
      const loadingOverlay = this.showLoadingOverlay('Rejecting changes...');

      try {
        this.callbacks.onRejectAll(this.currentNotebookPath);
        // Handle the rejected diffs immediately
        await this.callbacks.handleRejectedDiffs(this.currentNotebookPath);
        this.close(false);
      } catch (error) {
        console.error('Error handling rejected diffs:', error);
        this.showError('Failed to reject changes. Please try again.');
      } finally {
        if (loadingOverlay && this.dialogElement?.contains(loadingOverlay)) {
          this.dialogElement.removeChild(loadingOverlay);
        }
      }
    }
  }

  /**
   * Display a loading overlay while applying/rejecting diffs
   */
  private showLoadingOverlay(message: string): HTMLElement {
    const overlay = document.createElement('div');
    overlay.className = 'sage-ai-loading-overlay';
    overlay.style.position = 'absolute';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.backgroundColor = 'rgba(0,0,0,0.7)';
    overlay.style.display = 'flex';
    overlay.style.justifyContent = 'center';
    overlay.style.alignItems = 'center';
    overlay.style.zIndex = '1000';
    overlay.style.color = 'white';
    overlay.style.fontSize = '16px';

    const content = document.createElement('div');
    content.textContent = message;
    overlay.appendChild(content);

    if (this.dialogElement) {
      this.dialogElement.style.position = 'relative';
      this.dialogElement.appendChild(overlay);
    }

    return overlay;
  }

  /**
   * Show an error message in the dialog
   */
  private showError(message: string): void {
    const errorMessage = document.createElement('div');
    errorMessage.className = 'sage-ai-error-message';
    errorMessage.style.color = '#ff4d4f';
    errorMessage.style.padding = '10px';
    errorMessage.style.margin = '10px';
    errorMessage.style.borderRadius = '4px';
    errorMessage.style.backgroundColor = 'rgba(255,77,79,0.1)';
    errorMessage.textContent = message;

    if (this.dialogElement) {
      this.dialogElement.prepend(errorMessage);

      // Remove the error message after 5 seconds
      setTimeout(() => {
        if (errorMessage.parentNode === this.dialogElement) {
          this.dialogElement?.removeChild(errorMessage);
        }
      }, 5000);
    }
  }

  /**
   * Check if all cells have been handled
   */
  private async checkAllCellsStatus(): Promise<void> {
    if (!this.dialogElement) return;

    // Count approved and rejected cells
    const cellElements = this.dialogElement.querySelectorAll(
      '.sage-ai-diff-cell-item'
    );
    let approvedCount = 0;
    let rejectedCount = 0;

    cellElements.forEach(cell => {
      if (cell.classList.contains('sage-ai-diff-approved')) {
        approvedCount++;
      } else if (cell.classList.contains('sage-ai-diff-rejected')) {
        rejectedCount++;
      }
    });

    // If all cells are handled, apply/reject diffs and close the dialog
    if (approvedCount + rejectedCount === cellElements.length) {
      const loadingOverlay = this.showLoadingOverlay(
        approvedCount > 0 ? 'Applying changes...' : 'Rejecting changes...'
      );

      try {
        if (approvedCount > 0) {
          await this.callbacks?.applyApprovedDiffs(this.currentNotebookPath);
        }

        if (rejectedCount > 0) {
          await this.callbacks?.handleRejectedDiffs(this.currentNotebookPath);
        }

        this.close(approvedCount > 0);
      } catch (error) {
        console.error('Error processing diffs:', error);
        this.showError('Failed to process changes. Please try again.');
      } finally {
        if (loadingOverlay && this.dialogElement?.contains(loadingOverlay)) {
          this.dialogElement.removeChild(loadingOverlay);
        }
      }
    }
  }

  /**
   * Close the dialog
   * Made public so it can be called externally
   */
  public close(approved: boolean): void {
    // Remove the dialog from DOM
    if (
      this.dialogElement &&
      this.parentElement &&
      this.parentElement.contains(this.dialogElement)
    ) {
      this.parentElement.removeChild(this.dialogElement);
    }

    // Resolve the promise with both approval status and run flag
    if (this.resolvePromise) {
      // If approved is true and this is a run context, set runImmediately to true
      const runImmediately = approved && this.isRunContext;
      this.resolvePromise({ approved, runImmediately });
      this.resolvePromise = null;
    }

    // Clean up
    this.dialogElement = null;
  }
}

const ACTION_ICONS = {
  add: '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 12 12" fill="none"><path d="M9.5 5.5H6.5V2.5C6.5 2.36739 6.44732 2.24021 6.35355 2.14645C6.25979 2.05268 6.13261 2 6 2C5.86739 2 5.74021 2.05268 5.64645 2.14645C5.55268 2.24021 5.5 2.36739 5.5 2.5V5.5H2.5C2.36739 5.5 2.24021 5.55268 2.14645 5.64645C2.05268 5.74021 2 5.86739 2 6C2 6.13261 2.05268 6.25979 2.14645 6.35355C2.24021 6.44732 2.36739 6.5 2.5 6.5H5.5V9.5C5.5 9.63261 5.55268 9.75979 5.64645 9.85355C5.74021 9.94732 5.86739 10 6 10C6.13261 10 6.25979 9.94732 6.35355 9.85355C6.44732 9.75979 6.5 9.63261 6.5 9.5V6.5H9.5C9.63261 6.5 9.75979 6.44732 9.85355 6.35355C9.94732 6.25979 10 6.13261 10 6C10 5.86739 9.94732 5.74021 9.85355 5.64645C9.75979 5.55268 9.63261 5.5 9.5 5.5Z" fill="#447F44"/></svg>',
  edit: '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 12 12" fill="none"><path d="M1.5 8.73V10.25C1.5 10.39 1.61 10.5 1.75 10.5H3.27C3.335 10.5 3.4 10.475 3.445 10.425L8.905 4.97L7.03 3.095L1.575 8.55C1.525 8.6 1.5 8.66 1.5 8.73ZM10.355 3.52C10.4014 3.47374 10.4381 3.4188 10.4632 3.35831C10.4883 3.29783 10.5012 3.23299 10.5012 3.1675C10.5012 3.10202 10.4883 3.03718 10.4632 2.97669C10.4381 2.9162 10.4014 2.86126 10.355 2.815L9.185 1.645C9.13874 1.59865 9.0838 1.56188 9.02331 1.53679C8.96283 1.51169 8.89798 1.49878 8.8325 1.49878C8.76702 1.49878 8.70217 1.51169 8.64169 1.53679C8.5812 1.56188 8.52626 1.59865 8.48 1.645L7.565 2.56L9.44 4.435L10.355 3.52Z" fill="#1E78D3"/></svg>',
  remove:
    '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 12 12" fill="none"><path d="M3.37903 8.62154L6.00053 6.00004M6.00053 6.00004L8.62203 3.37854M6.00053 6.00004L3.37903 3.37854M6.00053 6.00004L8.62203 8.62154" stroke="#9A3434" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
};

const COLLAPSE_ICON =
  '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 10 10" fill="none"><path d="M2.62081 5.95419C2.58175 5.99293 2.55076 6.03901 2.5296 6.08979C2.50845 6.14056 2.49756 6.19502 2.49756 6.25003C2.49756 6.30503 2.50845 6.35949 2.5296 6.41027C2.55076 6.46104 2.58175 6.50712 2.62081 6.54586L4.70414 8.62919C4.74288 8.66825 4.78896 8.69924 4.83973 8.7204C4.89051 8.74155 4.94497 8.75244 4.99997 8.75244C5.05498 8.75244 5.10944 8.74155 5.16021 8.7204C5.21099 8.69924 5.25707 8.66825 5.29581 8.62919L7.37914 6.54586C7.41819 6.50712 7.44919 6.46104 7.47035 6.41027C7.4915 6.35949 7.50239 6.30503 7.50239 6.25003C7.50239 6.19502 7.4915 6.14056 7.47035 6.08979C7.44919 6.03901 7.41819 5.99293 7.37914 5.95419C7.34041 5.91514 7.29432 5.88414 7.24355 5.86299C7.19277 5.84183 7.13831 5.83094 7.08331 5.83094C7.0283 5.83094 6.97384 5.84183 6.92307 5.86299C6.87229 5.88414 6.82621 5.91514 6.78747 5.95419L4.99997 7.74586L3.21247 5.95419C3.17374 5.91514 3.12766 5.88414 3.07688 5.86299C3.02611 5.84183 2.97165 5.83094 2.91664 5.83094C2.86164 5.83094 2.80718 5.84183 2.7564 5.86299C2.70563 5.88414 2.65954 5.91514 2.62081 5.95419ZM4.70414 1.37086L2.62081 3.45419C2.58196 3.49304 2.55114 3.53916 2.53012 3.58992C2.50909 3.64068 2.49827 3.69508 2.49827 3.75003C2.49827 3.86098 2.54235 3.9674 2.62081 4.04586C2.65966 4.08471 2.70578 4.11553 2.75654 4.13655C2.8073 4.15758 2.8617 4.1684 2.91664 4.1684C3.0276 4.1684 3.13401 4.12432 3.21247 4.04586L4.99997 2.25419L6.78747 4.04586C6.82621 4.08491 6.87229 4.11591 6.92307 4.13706C6.97384 4.15822 7.0283 4.16911 7.08331 4.16911C7.13831 4.16911 7.19277 4.15822 7.24355 4.13706C7.29432 4.11591 7.34041 4.08491 7.37914 4.04586C7.41819 4.00712 7.44919 3.96104 7.47035 3.91027C7.4915 3.85949 7.50239 3.80503 7.50239 3.75003C7.50239 3.69502 7.4915 3.64056 7.47035 3.58979C7.44919 3.53901 7.41819 3.49293 7.37914 3.45419L5.29581 1.37086C5.25707 1.33181 5.21099 1.30081 5.16021 1.27965C5.10944 1.2585 5.05498 1.24761 4.99997 1.24761C4.94497 1.24761 4.89051 1.2585 4.83973 1.27965C4.78896 1.30081 4.74288 1.33181 4.70414 1.37086Z" fill="#999999"/></svg>';
