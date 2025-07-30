import { PanelLayout, Widget } from '@lumino/widgets';
import { ChatBoxWidget } from '../Components/chatbox';
import { ToolService } from '../Services/ToolService';
import { NotebookContextManager } from './NotebookContextManager';

/**
 * Container widget that holds only the chat widget
 */
export class NotebookChatContainer extends Widget {
  public chatWidget: ChatBoxWidget;
  private toolService: ToolService;
  private contextManager: NotebookContextManager | null;
  private currentNotebookPath: string | null = null;

  constructor(
    toolService: ToolService,
    contextManager: NotebookContextManager | null | undefined
  ) {
    super();

    this.id = 'sage-ai-chat-container';
    this.title.label = 'Sage AI Chat';
    this.title.closable = true;
    this.addClass('sage-ai-chat-container');
    this.toolService = toolService;
    this.contextManager = contextManager || null;

    // Set the minimum width of the widget's node
    this.node.style.minWidth = 'calc(100vw / 4)';

    // Create chat widget with contextCellHighlighter
    this.chatWidget = new ChatBoxWidget();

    // Create layout for the container
    const layout = new PanelLayout();
    layout.addWidget(this.chatWidget);

    // Set the layout properly
    this.layout = layout;
  }

  public updateNotebookPath(oldPath: string, newPath: string): void {
    this.contextManager?.updateNotebookPath(oldPath, newPath);

    this.chatWidget.chatHistoryManager.updateNotebookPath(oldPath, newPath);

    this.chatWidget.updateNotebookPath(newPath);

    this.toolService.updateNotebookPath(oldPath, newPath);

    this.currentNotebookPath = newPath;
  }

  /**
   * Switch to a different notebook
   * @param notebookPath Path to the notebook
   */
  public switchToNotebook(notebookPath: string): void {
    if (this.currentNotebookPath === notebookPath) {
      // Already on this notebook, nothing to do
      return;
    }

    console.log(
      `[NotebookChatContainer] Switching to notebook: ${notebookPath}`
    );
    this.currentNotebookPath = notebookPath;

    // Update the tool service with the new notebook path
    this.toolService.setCurrentNotebookPath(notebookPath);

    // Update the notebook context manager if available
    if (this.contextManager) {
      this.contextManager.getContext(notebookPath);
    }

    // Update the widget with the new notebook path
    this.chatWidget.setNotebookPath(notebookPath);
  }

  /**
   * Handle a cell added to context
   * @param notebookPath Path of the notebook containing the cell
   * @param cellId ID of the cell added to context
   */
  public onCellAddedToContext(notebookPath: string): void {
    if (
      !this.currentNotebookPath ||
      this.currentNotebookPath !== notebookPath
    ) {
      console.warn(
        `Cannot add cell from ${notebookPath} to context when current notebook is ${this.currentNotebookPath}`
      );
      return;
    }

    // Pass the event to the chatbox
    this.chatWidget.onCellAddedToContext(notebookPath);
  }

  /**
   * Handle a cell removed from context
   * @param notebookPath Path of the notebook containing the cell
   */
  public onCellRemovedFromContext(notebookPath: string): void {
    if (
      !this.currentNotebookPath ||
      this.currentNotebookPath !== notebookPath
    ) {
      console.warn(
        `Cannot remove cell from ${notebookPath} context when current notebook is ${this.currentNotebookPath}`
      );
      return;
    }

    // Pass the event to the chatbox
    this.chatWidget.onCellRemovedFromContext(notebookPath);
  }
}
