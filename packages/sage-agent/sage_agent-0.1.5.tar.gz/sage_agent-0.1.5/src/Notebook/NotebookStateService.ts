import { ToolService } from '../Services/ToolService';
import { ConfigService } from '../Config/ConfigService';
import { AppStateService } from '../AppState';

/**
 * Service responsible for fetching and processing notebook state information
 */
export class NotebookStateService {
  private toolService: ToolService;
  private currentNotebookPath: string | null = null;

  constructor(toolService: ToolService) {
    this.toolService = toolService;
  }

  public updateNotebookPath(newPath: string): void {
    this.currentNotebookPath = newPath;
  }

  /**
   * Set the current notebook path
   * @param notebookPath Path to the notebook
   */
  public setNotebookPath(notebookPath: string | null): void {
    if (this.currentNotebookPath !== notebookPath) {
      console.log(
        `[NotebookStateService] Setting notebook path to: ${notebookPath}`
      );
      this.currentNotebookPath = notebookPath;

      // Also update the tool service's current notebook path
      if (notebookPath) {
        this.toolService.setCurrentNotebookPath(notebookPath);
      }
    }
  }

  /**
   * Get the current notebook path
   * @returns The current notebook path
   */
  public getNotebookPath(): string | null {
    return this.currentNotebookPath;
  }

  private cleanResult(result: any): any {
    const cleanedResult = [];
    if (result && result.content) {
      for (const content of result.content) {
        try {
          cleanedResult.push({
            ...content,
            text: JSON.parse(content.text)
          });
        } catch (e) {
          cleanedResult.push(content);
          console.error(e);
        }
      }
    }
    return cleanedResult;
  }

  /**
   * Fetches the current notebook state including summary, content, and edit history
   */
  public async fetchNotebookState(): Promise<string> {
    try {
      // Ensure the tool service is using the correct notebook context
      if (this.currentNotebookPath) {
        this.toolService.setCurrentNotebookPath(this.currentNotebookPath);
      } else {
        console.log('No notebook path set, using default context.');
      }

      // Pass the current notebook path to ensure correct context
      console.log('Fetching notebook state for:', this.currentNotebookPath);
      const notebook_summary =
        await this.toolService.notebookTools?.getNotebookSummary(
          this.currentNotebookPath
        );

      console.log('Notebook Summary: ===', notebook_summary);

      const notebook_content = AppStateService.getNotebookTools().read_cells({
        notebook_path: this.currentNotebookPath
      });

      console.log('Notebook Content ===:', notebook_content);

      const cells: any[] = notebook_content?.cells || [];

      // Reverse the cells array
      const reversedCells = [...cells].reverse();

      // Take the first 3 cells from the reversed list (these are the most recent)
      const recentCells = reversedCells.slice(0, 3);

      // Format the recent cells for better readability
      let recentCellsStr =
        '\n\nMost Recent Cells From Most Recent To Oldest:\n';
      recentCells.forEach((cell, index) => {
        recentCellsStr += `\n--- ${index === 0 && 'Latest '}Cell ---\n${JSON.stringify(cell)}\n`;
      });

      // Use the local FilesystemTools instead of making HTTP request to MCP server
      let datasetsJson = '[]';
      try {
        if (this.toolService.filesystemTools) {
          const datasetsResult =
            await this.toolService.filesystemTools.list_datasets();
          datasetsJson = datasetsResult;
        } else {
          console.warn(
            'FilesystemTools not available, using empty dataset list'
          );
        }
      } catch (error) {
        console.error('Error fetching datasets via FilesystemTools:', error);
        datasetsJson = '[]';
      }

      console.log('Datasets:', datasetsJson);

      // Add the edit history
      let datasetStr = `\n\nAvailable Datasets:\n${datasetsJson}\n\n`;

      let summaryClean = '=== SUMMARY OF CELLS IN NOTEBOOK === \n\n';
      notebook_summary.forEach((cell: any) => {
        if (cell.id === 'planning_cell') {
          summaryClean += '- SAGE PLANNING CELL - \n';
          summaryClean += `cell_index: ${cell.index}, cell_id: ${cell.id}, summary: ${cell.summary}, cell_type: ${cell.cell_type}, next_step_string: ${cell.next_step_string}, current_step_string: ${cell.current_step_string}, empty: ${cell.empty}\n`;
          summaryClean += '- END SAGE PLANNING CELL -';
        } else {
          summaryClean += `cell_id: ${cell.id}, summary: ${cell.summary}, cell_index: ${cell.index}, cell_type: ${cell.cell_type}, empty: ${cell.empty}`;
        }

        summaryClean += '\n\n';
      });
      summaryClean += '=== END SUMMARY OF CELLS IN NOTEBOOK ===\n\n';
      console.log(summaryClean);

      const summaryToSend = summaryClean + datasetStr;
      console.log('Summary Sent to LLM: ', summaryToSend);

      return summaryToSend;
    } catch (error) {
      console.error('Failed to fetch notebook state:', error);
      return '';
    }
  }
}
