import { ToolService } from '../Services/ToolService';
import { NotebookStateService } from './NotebookStateService';

/**
 * Interface for notebook-specific context data
 */
export interface INotebookContext {
  notebookPath: string;
  toolService: ToolService;
  stateService: NotebookStateService;
  lastAccessed: number;
  flowId?: string; // Unique ID for this LLM flow/conversation
  contextCells: IContextCell[]; // Array of cells added to context
}

/**
 * Interface for a cell added to context
 */
export interface IContextCell {
  cellId: string;
  trackingId?: string;
  content: string;
  cellType: string;
  addedAt: number;
}

/**
 * Manager for maintaining notebook-specific contexts for LLM flows
 */
export class NotebookContextManager {
  // Map from notebook paths to their contexts
  private notebookContexts: Map<string, INotebookContext> = new Map();
  // Shared toolService instance
  private sharedToolService: ToolService;

  constructor(toolService: ToolService) {
    this.sharedToolService = toolService;
  }

  /**
   * Get or create a context for a specific notebook
   * @param notebookPath Path to the notebook
   * @returns The notebook context object
   */
  public getContext(notebookPath: string): INotebookContext {
    if (!this.notebookContexts.has(notebookPath)) {
      console.log(
        `[NotebookContextManager] Creating new context for notebook: ${notebookPath}`
      );

      // Set the current notebook path in the tool service
      this.sharedToolService.setCurrentNotebookPath(notebookPath);

      // Create a notebook-specific state service using the shared tool service
      const stateService = new NotebookStateService(this.sharedToolService);
      stateService.setNotebookPath(notebookPath);

      // Create the context
      const context: INotebookContext = {
        notebookPath,
        toolService: this.sharedToolService,
        stateService,
        lastAccessed: Date.now(),
        flowId: this.generateFlowId(),
        contextCells: [] // Initialize with empty array of context cells
      };

      this.notebookContexts.set(notebookPath, context);
      return context;
    }

    // Update last accessed time and return existing context
    const context = this.notebookContexts.get(notebookPath)!;
    context.lastAccessed = Date.now();

    // Ensure the tool service is set to the correct notebook path
    this.sharedToolService.setCurrentNotebookPath(notebookPath);

    return context;
  }

  public updateNotebookPath(oldPath: string, newPath: string): void {
    const context = this.notebookContexts.get(oldPath);
    if (context) {
      context.notebookPath = newPath;
      this.notebookContexts.set(newPath, context);
      this.notebookContexts.delete(oldPath);
    }
  }

  /**
   * Add a cell to the context for a notebook
   * @param notebookPath Path to the notebook
   * @param cellId ID of the cell
   * @param trackingId Optional tracking ID of the cell
   * @param content Content of the cell
   * @param cellType Type of the cell (code, markdown)
   * @returns true if the cell was added, false if it was already in context
   */
  public addCellToContext(
    notebookPath: string,
    cellId: string,
    trackingId: string | undefined,
    content: string,
    cellType: string
  ): boolean {
    // Get or create the context for this notebook
    const context = this.getContext(notebookPath);

    // Check if this cell is already in context
    if (context.contextCells.some(c => c.cellId === cellId)) {
      return false; // Already in context
    }

    // Add the cell to context
    context.contextCells.push({
      cellId,
      trackingId,
      content,
      cellType,
      addedAt: Date.now()
    });

    console.log(`[NotebookContextManager] Added cell to context: ${cellId}`);
    return true;
  }

  /**
   * Remove a cell from the context
   * @param notebookPath Path to the notebook
   * @param cellId ID of the cell to remove
   * @returns true if the cell was removed, false if it wasn't in context
   */
  public removeCellFromContext(notebookPath: string, cellId: string): boolean {
    // Get the context for this notebook
    if (!this.notebookContexts.has(notebookPath)) {
      return false;
    }

    const context = this.notebookContexts.get(notebookPath)!;
    const initialLength = context.contextCells.length;

    // Filter out the cell to remove
    context.contextCells = context.contextCells.filter(
      c => c.cellId !== cellId
    );

    // Return true if a cell was removed
    return context.contextCells.length < initialLength;
  }

  /**
   * Check if a cell is in context
   * @param notebookPath Path to the notebook
   * @param cellId ID of the cell to check
   * @returns true if the cell is in context, false otherwise
   */
  public isCellInContext(notebookPath: string, cellId: string): boolean {
    if (!this.notebookContexts.has(notebookPath)) {
      return false;
    }

    const context = this.notebookContexts.get(notebookPath)!;
    return context.contextCells.some(c => c.cellId === cellId);
  }

  /**
   * Get all cells in context for a notebook
   * @param notebookPath Path to the notebook
   * @returns Array of context cells or empty array if notebook has no context
   */
  public getContextCells(notebookPath: string): IContextCell[] {
    if (!this.notebookContexts.has(notebookPath)) {
      return [];
    }

    return [...this.notebookContexts.get(notebookPath)!.contextCells];
  }

  /**
   * Format the context cells as a message for sending to the LLM
   * @param notebookPath Path to the notebook
   * @returns Formatted context message in XML format
   */
  public formatContextAsMessage(notebookPath: string): string {
    const cells = this.getContextCells(notebookPath);

    if (cells.length === 0) {
      return '';
    }

    // Format the cells in an XML-style format for better LLM understanding
    let formattedContent =
      'Here are the cells from the notebook that the user has provided as additional context:\n\n';

    cells.forEach(cell => {
      const found = this.sharedToolService.notebookTools?.findCellByAnyId(
        cell.trackingId!
      );
      if (found) {
        formattedContent += `==== CELL Context - Cell ID: ${cell.trackingId} ====\n`;
        formattedContent += found.cell.model.sharedModel.getSource().trim();
        formattedContent += `\n==== End Cell Context ====\n\n`;
      }
    });

    return formattedContent;
  }

  /**
   * Get a summary of what's in context for display purposes
   * @param notebookPath Path to the notebook
   * @returns Array of context summaries
   */
  public getContextSummary(notebookPath: string): Array<{
    type: 'cell';
    id: string;
    name: string;
    preview: string;
  }> {
    const cells = this.getContextCells(notebookPath);

    return cells.map(cell => {
      const found = this.sharedToolService.notebookTools?.findCellByAnyId(
        cell.trackingId!
      );

      if (found) {
        const content = found.cell.model.sharedModel.getSource();
        const preview =
          content.length > 50 ? content.substring(0, 50) + '...' : content;

        return {
          type: 'cell' as const,
          id: cell.trackingId!,
          name: `Cell ${cell.trackingId}`,
          preview: preview
        };
      }

      return {
        type: 'cell' as const,
        id: cell.trackingId!,
        name: `Cell ${cell.trackingId}`,
        preview: 'Cell content unavailable'
      };
    });
  }

  /**
   * Generate a unique flow ID
   */
  private generateFlowId(): string {
    return (
      'flow-' + Date.now() + '-' + Math.random().toString(36).substring(2, 9)
    );
  }
}
