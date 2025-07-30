import * as React from 'react';
import { ILLMState, LLMDisplayState } from './types';
import { DiffItem } from './DiffItem';
import { AppStateService } from '../../AppState';
import { IPendingDiff } from '../../types';
import { MENU_CLOSE_ICON, MENU_ICON } from './icons';
import { getToolDisplayMessage, getToolIcon } from '../../utils/toolDisplay';

/**
 * React component for displaying LLM processing state content
 */
export function LLMStateContent({
  isVisible,
  state,
  text,
  toolName,
  diffs,
  waitingForUser,
  isRunContext
}: ILLMState): JSX.Element | null {
  const [isExpanded, setIsExpanded] = React.useState(false);
  const [allDiffsResolved, setAllDiffsResolved] = React.useState(false);

  // Subscribe to all diffs resolved signal
  React.useEffect(() => {
    const diffManager = AppStateService.getNotebookDiffManager();
    const onAllDiffsResolved = () => {
      setAllDiffsResolved(true);
    };

    diffManager.allDiffsResolved.connect(onAllDiffsResolved);

    return () => {
      diffManager.allDiffsResolved.disconnect(onAllDiffsResolved);
    };
  }, []);

  // Check allDiffsResolved when diffs change
  React.useEffect(() => {
    if (diffs && diffs.length > 0) {
      // Check if all diffs have decisions (approved or rejected)
      const allDecided = diffs.every(
        diff =>
          diff.userDecision === 'approved' ||
          diff.userDecision === 'rejected' ||
          diff.approved === true ||
          diff.approved === false
      );
      setAllDiffsResolved(allDecided);
    } else {
      setAllDiffsResolved(false);
    }
  }, [diffs]);

  // Helper function to calculate total additions and deletions
  const calculateTotals = (diffs: IPendingDiff[]) => {
    let totalAdded = 0;
    let totalRemoved = 0;

    diffs.forEach(diff => {
      const originalLines = diff.originalContent?.split('\n').length || 0;
      const newLines = diff.newContent?.split('\n').length || 0;

      if (diff.type === 'add') {
        totalAdded += newLines;
      } else if (diff.type === 'remove') {
        totalRemoved += originalLines;
      } else if (diff.type === 'edit') {
        totalAdded += Math.max(0, newLines - originalLines);
        totalRemoved += Math.max(0, originalLines - newLines);
      }
    });

    return { totalAdded, totalRemoved };
  };
  if (!isVisible) {
    return null;
  }

  // Idle state - don't show anything
  if (state === LLMDisplayState.IDLE) {
    return null;
  }

  // Generating state - show thinking indicator
  if (state === LLMDisplayState.GENERATING) {
    return (
      <div
        className="sage-ai-llm-state-display sage-ai-generating"
        style={{ display: 'flex' }}
      >
        <div className="sage-ai-llm-state-content">
          <div className="sage-ai-blob-loader" />
          <span className="sage-ai-llm-state-text">{text}</span>
        </div>

        {!waitingForUser && (
          <button
            className="sage-ai-llm-state-stop-button"
            onClick={() => {
              AppStateService.getChatContainerSafe()?.chatWidget.cancelMessage();
            }}
            title="Stop generation"
          >
            Stop
          </button>
        )}
      </div>
    );
  }

  // Using tool state - show tool usage indicator
  if (state === LLMDisplayState.USING_TOOL) {
    const toolIcon = toolName ? getToolIcon(toolName) : null;
    const toolMessage = toolName
      ? getToolDisplayMessage(toolName)
      : text || 'Using tool...';

    return (
      <div
        className="sage-ai-llm-state-display sage-ai-using-tool"
        style={{ display: 'flex' }}
      >
        <div className="sage-ai-llm-state-content">
          {toolIcon ? (
            <div
              className="sage-ai-tool-icon-container"
              dangerouslySetInnerHTML={{ __html: toolIcon }}
            />
          ) : (
            <div className="sage-ai-tool-loader" />
          )}
          <span className="sage-ai-llm-state-text">{toolMessage}</span>
        </div>

        <button
          className="sage-ai-llm-state-stop-button"
          onClick={() => {
            AppStateService.getChatContainerSafe()?.chatWidget.cancelMessage();
          }}
          title="Stop tool execution"
        >
          Stop
        </button>
      </div>
    );
  }

  // Diff state - show diff review interface
  if (state === LLMDisplayState.DIFF && diffs && diffs.length > 0) {
    const { totalAdded, totalRemoved } = calculateTotals(diffs);

    return (
      <div className="sage-ai-llm-state-display sage-ai-diff-state">
        <div
          className="sage-ai-diff-summary-bar"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="sage-ai-diff-summary-info">
            <span className="sage-ai-diff-icon">
              {!isExpanded ? (
                <MENU_ICON.react className="sage-ai-diff-menu-icon" />
              ) : (
                <MENU_CLOSE_ICON.react className="sage-ai-diff-menu-icon" />
              )}
            </span>
            <span className="sage-ai-diff-cell-count">
              {diffs.length} cell{diffs.length !== 1 ? 's' : ''} modified
            </span>
            {totalAdded > 0 && (
              <span className="sage-ai-diff-added-count">+{totalAdded}</span>
            )}
            {totalRemoved > 0 && (
              <span className="sage-ai-diff-removed-count">
                -{totalRemoved}
              </span>
            )}
          </div>
          <div className="sage-ai-diff-summary-actions">
            {!allDiffsResolved && (
              <>
                <button
                  className="sage-ai-diff-btn sage-ai-diff-reject-all"
                  onClick={async e => {
                    e.stopPropagation();
                    await AppStateService.getNotebookDiffManager().diffApprovalDialog.rejectAll();
                    setAllDiffsResolved(true);
                  }}
                  title="Reject all changes"
                >
                  Reject All
                </button>
                <button
                  className="sage-ai-diff-btn sage-ai-diff-approve-all"
                  onClick={async e => {
                    e.stopPropagation();
                    await AppStateService.getNotebookDiffManager().diffApprovalDialog.approveAll();
                    setAllDiffsResolved(true);
                  }}
                  title="Approve all changes"
                >
                  {isRunContext ? 'Run All' : 'Approve All'}
                </button>
              </>
            )}
          </div>
        </div>
        {isExpanded && (
          <div className="sage-ai-diff-list">
            {diffs.map((diff, index) => (
              <DiffItem
                key={`${diff.cellId}-${index}`}
                diff={diff}
                showActionsOnHover={true}
              />
            ))}
          </div>
        )}
      </div>
    );
  }

  return null;
}
