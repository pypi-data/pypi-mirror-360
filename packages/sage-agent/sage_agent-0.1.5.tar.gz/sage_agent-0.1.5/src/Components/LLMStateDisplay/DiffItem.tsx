import * as React from 'react';
import { IPendingDiff } from '../../types';
import { DiffItemProps } from './types';
import { AppStateService } from '../../AppState';

/**
 * Component for displaying individual diff item
 */
export function DiffItem({
  diff,
  showActionsOnHover = false
}: DiffItemProps): JSX.Element {
  const [diffState, setDiffState] = React.useState(diff);

  // Subscribe to diff state changes from NotebookDiffManager
  React.useEffect(() => {
    const diffManager = AppStateService.getNotebookDiffManager();
    const onDiffStateChanged = (
      sender: any,
      data: {
        cellId: string;
        approved: boolean | undefined;
        notebookPath?: string | null;
      }
    ) => {
      if (data.cellId === diff.cellId) {
        // Update the local state to reflect the new decision
        setDiffState(prev => ({
          ...prev,
          approved: data.approved,
          userDecision:
            data.approved === true
              ? 'approved'
              : data.approved === false
                ? 'rejected'
                : null
        }));
      }
    };

    diffManager.diffStateChanged.connect(onDiffStateChanged);

    return () => {
      diffManager.diffStateChanged.disconnect(onDiffStateChanged);
    };
  }, [diff.cellId]);

  const getLineChanges = (
    diff: IPendingDiff
  ): { added: number; removed: number } => {
    const originalLines = diff.originalContent?.split('\n').length || 0;
    const newLines = diff.newContent?.split('\n').length || 0;

    if (diff.type === 'add') {
      return { added: newLines, removed: 0 };
    } else if (diff.type === 'remove') {
      return { added: 0, removed: originalLines };
    } else if (diff.type === 'edit') {
      return {
        added: Math.max(0, newLines - originalLines),
        removed: Math.max(0, originalLines - newLines)
      };
    }
    return { added: 0, removed: 0 };
  };

  const { added, removed } = getLineChanges(diffState);
  const getOperationIcon = (type: string) => {
    switch (type) {
      case 'add':
        return '+';
      case 'edit':
        return '~';
      case 'remove':
        return '−';
      default:
        return '?';
    }
  };

  const isDecisionMade =
    diffState.userDecision !== null && diffState.userDecision !== undefined;

  return (
    <div
      className={`sage-ai-diff-item ${showActionsOnHover ? 'sage-ai-diff-item-hover-actions' : ''}`}
      onClick={() => {
        AppStateService.getNotebookTools().scrollToCellById(diffState.cellId);
      }}
    >
      <div className="sage-ai-diff-info">
        <span
          className={`sage-ai-diff-operation sage-ai-diff-${diffState.type}`}
        >
          {getOperationIcon(diffState.type)}
        </span>
        <span className="sage-ai-diff-summary">{diffState.cellId}</span>
        <div className="sage-ai-diff-changes">
          {added > 0 && <span className="sage-ai-diff-added">+{added}</span>}
          {removed > 0 && (
            <span className="sage-ai-diff-removed">−{removed}</span>
          )}
          {/* Show user decision */}
          {isDecisionMade && (
            <span
              className={`sage-ai-diff-decision sage-ai-diff-decision-${diffState.userDecision}`}
            >
              {diffState.userDecision === 'approved' ? '✓' : '✕'}
            </span>
          )}
        </div>
      </div>
      {!isDecisionMade && (
        <div className="sage-ai-diff-actions">
          <button
            className="sage-ai-diff-btn sage-ai-diff-approve"
            onClick={() => {
              AppStateService.getNotebookDiffManager().approveDiff(
                diffState.cellId
              );
              AppStateService.getNotebookDiffManager().diffApprovalDialog.approveCell(
                diffState.cellId
              );
            }}
            disabled={isDecisionMade}
            title="Approve this change"
          >
            ✓
          </button>
          <button
            className="sage-ai-diff-btn sage-ai-diff-reject"
            onClick={() => {
              AppStateService.getNotebookDiffManager().rejectDiff(
                diffState.cellId
              );
              AppStateService.getNotebookDiffManager().diffApprovalDialog.rejectCell(
                diffState.cellId
              );
            }}
            disabled={isDecisionMade}
            title="Reject this change"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
}
