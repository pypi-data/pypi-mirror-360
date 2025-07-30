import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';
import {
  ICommandPalette,
  IToolbarWidgetRegistry,
  WidgetTracker
} from '@jupyterlab/apputils';
import { INotebookTracker } from '@jupyterlab/notebook';
import { ToolService } from './Services/ToolService';
import { ConfigService } from './Config/ConfigService';
import { NotebookTools } from './Notebook/NotebookTools';
import { ActionHistory } from './Chat/ActionHistory';
import { NotebookDiffManager } from './Notebook/NotebookDiffManager';
import { CellTrackingService } from './CellTrackingService';
import { TrackingIDUtility } from './TrackingIDUtility';
import { NotebookChatContainer } from './Notebook/NotebookChatContainer';
import { NotebookContextManager } from './Notebook/NotebookContextManager';
import { addIcon } from '@jupyterlab/ui-components';
import { ContextCellHighlighter } from './Notebook/ContextCellHighlighter';
import { AppStateService } from './AppState';
import { NotebookSettingsContainer } from './NotebookSettingsContainer';
import { Widget } from '@lumino/widgets';
import { PlanStateDisplay } from './Components/PlanStateDisplay';
import { WaitingUserReplyBoxManager } from './Notebook/WaitingUserReplyBoxManager';
import { registerCommands } from './commands';
import { registerEvalCommands } from './eval_commands';

/**
 * Initialization data for the sage-ai extension.
 */
export const plugin: JupyterFrontEndPlugin<void> = {
  id: 'sage-agent:plugin',
  description: 'Sage AI - Your AI Data Partner',
  autoStart: true,
  requires: [INotebookTracker, ICommandPalette],
  optional: [ISettingRegistry, IToolbarWidgetRegistry],
  activate: (
    app: JupyterFrontEnd,
    notebooks: INotebookTracker,
    palette: ICommandPalette,
    settingRegistry: ISettingRegistry | null,
    toolbarRegistry: IToolbarWidgetRegistry | null
  ) => {
    console.log('JupyterLab extension sage-agent is activated!');
    const contentManager = app.serviceManager.contents;

    // Ensure 'templates' directory exists and create 'rule.default.md' if missing
    const ensureTemplatesDirAndFile = async () => {
      try {
        // Check if 'templates' directory exists
        let dirExists = false;
        try {
          const dir = await contentManager.get('templates');
          dirExists = dir.type === 'directory';
        } catch (e) {
          dirExists = false;
        }
        if (!dirExists) {
          // Create untitled directory, then rename to 'templates'
          const untitledDir = await contentManager.newUntitled({
            type: 'directory',
            path: ''
          });
          await contentManager.rename(untitledDir.path, 'templates');
          console.log("Created 'templates' directory.");
        }
        // Check if 'rule.default.md' exists
        let fileExists = false;
        try {
          await contentManager.get('templates/rule.example.md');
          fileExists = true;
        } catch (e) {
          fileExists = false;
        }
        if (!fileExists) {
          await contentManager.save('templates/rule.example.md', {
            type: 'file',
            format: 'text',
            content:
              '# EXAMPLE TEMPLATE FILE\n' +
              '\n' +
              '# Description: \n' +
              'When called, look into the requested function or codeblock and see if you find any parallelizale code. You can use the following embarringly parallel code template to speed up those function computations\n' +
              '\n' +
              '# Code:\n' +
              '```python\n' +
              'from joblib import Parallel, delayed\n' +
              '\n' +
              'def run_in_batches(fn_name):\n' +
              '    tickers = get_sp500_tickers()\n' +
              '    \n' +
              '    # Process in smaller batches to control memory usage\n' +
              '    results = Parallel(\n' +
              '        n_jobs=-1, \n' +
              '        batch_size=10,  # Process 10 items per batch\n' +
              "        backend='multiprocessing'\n" +
              '    )(delayed(test_ticket)(ticker) for ticker in tickers)\n' +
              '    \n' +
              '    return dict(zip(tickers, results))\n' +
              '```'
          });
          console.log(
            "Created 'templates/rule.default.md' with placeholder content."
          );
        }
      } catch (err) {
        console.error(
          'Error ensuring templates directory and rule.default.md:',
          err
        );
      }
    };
    ensureTemplatesDirAndFile();

    // Load settings if available
    if (settingRegistry) {
      settingRegistry
        .load(plugin.id)
        .then(settings => {
          console.log('Loaded settings for sage-agent');
          const defaultService = settings.get('defaultService')
            .composite as string;
          // Store the default service in ConfigService
          if (defaultService) {
            ConfigService.setActiveModelType(defaultService);
          }

          // Watch for setting changes
          settings.changed.connect(() => {
            const newDefaultService = settings.get('defaultService')
              .composite as string;
            ConfigService.setActiveModelType(newDefaultService);
            console.log(`Default service changed to ${newDefaultService}`);
          });
        })
        .catch(error => {
          console.error('Failed to load settings for sage-agent', error);
        });
    }

    // Create a shared ToolService instance that has access to the notebook context
    const toolService = new ToolService();

    const planStateDisplay = new PlanStateDisplay();
    const waitingUserReplyBoxManager = new WaitingUserReplyBoxManager();

    // Set the notebook tracker in the tool service
    toolService.setNotebookTracker(notebooks, waitingUserReplyBoxManager);

    // Set the content manager in the tool service
    toolService.setContentManager(contentManager);

    // Initialize NotebookContextManager with the shared tool service
    const notebookContextManager = new NotebookContextManager(toolService);

    // Set the context manager in the tool service
    toolService.setContextManager(notebookContextManager);

    // Initialize action history
    const actionHistory = new ActionHistory();

    // Initialize NotebookTools
    const notebookTools = new NotebookTools(
      notebooks,
      waitingUserReplyBoxManager
    );

    // Initialize the AppState with core services
    AppStateService.initializeCoreServices(
      toolService,
      notebooks,
      notebookTools,
      notebookContextManager,
      contentManager
    );

    // Initialize managers in AppState
    AppStateService.initializeManagers(
      planStateDisplay,
      waitingUserReplyBoxManager
    );

    // Initialize additional services
    AppStateService.initializeAdditionalServices(
      actionHistory,
      new CellTrackingService(notebookTools, notebooks),
      new TrackingIDUtility(notebooks),
      new ContextCellHighlighter(
        notebooks,
        notebookContextManager,
        notebookTools,
        async (cell, promptText) => {
          // This is the callback executed when a prompt is submitted from the quick generation input
          console.log(
            'Prompt submitted for cell',
            (cell as any).model?.id || cell.id,
            ':',
            promptText
          );

          // Get the cell ID (use tracking ID if available, fallback to model.id or id)
          const cellId =
            (cell as any).model?.sharedModel.getMetadata()?.cell_tracker
              ?.trackingId ||
            (cell as any).model?.id ||
            (cell as any).id ||
            '[unknown]';

          if (cellId === '[unknown]') {
            console.error(
              'Could not determine cell ID for prompt submission.',
              cell
            );
            // Optionally provide user feedback
            return;
          }

          // Fetch quick_edit prompt and blacklist from config
          try {
            const config = await ConfigService.getConfig();
            const quickEditPrompt = config.quick_edit.system_prompt;
            const quickEditBlacklist = config.quick_edit.tool_blacklist || [];

            // Get the chatbox widget instance from the container
            const chatContainer = AppStateService.getChatContainerSafe();
            const chatbox = chatContainer?.chatWidget;

            if (chatbox && !chatbox.isDisposed) {
              // Set the quick edit prompt and blacklist in the chatbox
              chatbox.setAnthropicPromptAndBlacklist(
                quickEditPrompt,
                quickEditBlacklist
              );

              const cellContext = notebookTools
                .findCellByTrackingId(cellId)
                ?.cell.model.sharedModel.getSource();

              // Set the main chat input value
              chatbox.inputManager.setInputValue(promptText);

              // Open/activate the main chatbox
              app.shell.activateById(chatContainer!.id);

              // Automatically send the message
              chatbox.sendMessage(
                `The user is creating a prompt using cell with ID ${cellId} as context. The cell content is "${cellContext}. I will use this as context for the user's prompt. \n"`
              );

              console.log(
                'Prompt placed in main chat input and sent (quick_edit mode).'
              );
            } else {
              console.error('Chatbox widget not available or disposed.');
            }
          } catch (err) {
            console.error('Failed to fetch quick_edit config:', err);
          }
        }
      )
    );

    // Initialize CellTrackingService - now retrieved from AppState
    const cellTrackingService = AppStateService.getCellTrackingService();

    // Initialize ContextCellHighlighter - now retrieved from AppState
    const contextCellHighlighter = AppStateService.getContextCellHighlighter();

    // Initialize NotebookDiffManager
    const diffManager = new NotebookDiffManager(notebookTools, actionHistory);

    // Update AppState with the diff manager
    AppStateService.setState({ notebookDiffManager: diffManager });

    // Set up notebook tracking to provide the active notebook widget to the diffManager
    notebooks.currentChanged.connect((_, notebook) => {
      if (notebook) {
        let oldPath = notebook.context.path;

        notebook.context.pathChanged.connect((_, path) => {
          if (oldPath !== path) {
            diffManager.setNotebookPath(path);

            const chatContainer = AppStateService.getChatContainerSafe();
            chatContainer?.updateNotebookPath(oldPath, path);

            oldPath = path;
          }
        });

        diffManager.setNotebookWidget(notebook);
        // Initialize tracking metadata for existing cells
        cellTrackingService.initializeExistingCells();

        // Update the context for this notebook path
        if (notebook.context.path) {
          notebookContextManager.getContext(notebook.context.path);
        }

        // Update the chat widget with the new notebook path
        AppStateService.switchChatContainerToNotebook(notebook.context.path);
      }
    });

    // Initialize the tracking ID utility - now retrieved from AppState
    const trackingIDUtility = AppStateService.getTrackingIDUtility();

    // Create the widget tracker
    const tracker = new WidgetTracker<Widget>({
      namespace: 'sage-ai-widgets'
    });

    // Initialize the containers
    let settingsContainer: NotebookSettingsContainer | undefined;

    const initializeChatContainer = () => {
      // Get existing chat container from AppState
      const existingChatContainer = AppStateService.getState().chatContainer;

      // Create a new chat container
      const createContainer = () => {
        // Pass the shared tool service, diff manager, and notebook context manager to the container
        const newContainer = new NotebookChatContainer(
          toolService,
          notebookContextManager
        );
        tracker.add(newContainer);

        // Add the container to the right side panel
        app.shell.add(newContainer, 'right', { rank: 1000 });

        // If there's a current notebook, set its path
        if (notebooks.currentWidget) {
          newContainer.switchToNotebook(notebooks.currentWidget.context.path);
        }

        // Store in AppState
        AppStateService.setChatContainer(newContainer);

        return newContainer;
      };

      if (!existingChatContainer || existingChatContainer.isDisposed) {
        const chatContainer = createContainer();

        // Set the chat container reference in the context cell highlighter
        contextCellHighlighter.setChatContainer(chatContainer);

        return chatContainer;
      }

      return existingChatContainer;
    };

    const initializeSettingsContainer = () => {
      // Create a new settings container
      const createContainer = () => {
        // Pass the shared tool service, diff manager, and notebook context manager to the container
        const newContainer = new NotebookSettingsContainer(
          toolService,
          diffManager,
          notebookContextManager
        );
        tracker.add(newContainer);

        // Add the container to the right side panel
        app.shell.add(newContainer, 'right', { rank: 1001 });

        return newContainer;
      };

      if (!settingsContainer || settingsContainer.isDisposed) {
        settingsContainer = createContainer();
      }

      return settingsContainer;
    };

    // Initialize both containers
    initializeChatContainer();
    settingsContainer = initializeSettingsContainer();

    // Set up notebook tracking to switch to the active notebook
    notebooks.currentChanged.connect((_, notebook) => {
      if (notebook) {
        // Fix for old notebooks having undeletable first cells
        if (notebook.model && notebook.model.cells.length > 0) {
          notebook.model.cells.get(0).setMetadata('deletable', true);
        }

        diffManager.setNotebookWidget(notebook);
        diffManager.setNotebookPath(notebook.context.path);
        // Initialize tracking metadata for existing cells
        cellTrackingService.initializeExistingCells();

        // Update the context for this notebook path
        if (notebook.context.path) {
          notebookContextManager.getContext(notebook.context.path);
        }

        // Update both containers with the new notebook path
        const chatContainer = AppStateService.getState().chatContainer;
        if (chatContainer && !chatContainer.isDisposed) {
          chatContainer.switchToNotebook(notebook.context.path);
        }

        const planCell = notebookTools.getPlanCell(notebook.context.path);

        if (planCell) {
          const currentStep =
            (planCell.model.sharedModel.getMetadata().custom as any)
              ?.current_step_string || '';
          const nextStep =
            (planCell.model.sharedModel.getMetadata().custom as any)
              ?.next_step_string || '';
          const source = planCell.model.sharedModel.getSource() || '';

          console.log('Updating step floating box', currentStep, nextStep);

          void AppStateService.getPlanStateDisplay().updatePlan(
            currentStep,
            nextStep,
            source
          );
        } else if (!planCell) {
          void AppStateService.getPlanStateDisplay().updatePlan(
            undefined,
            undefined,
            undefined
          );
        }

        notebook?.model?.cells.changed.connect(() => {
          // Update the context cell highlighting when cells change
          trackingIDUtility.fixTrackingIDs(notebook.context.path);
          contextCellHighlighter.refreshHighlighting(notebook);

          const planCell = notebookTools.getPlanCell(notebook.context.path);

          if (planCell) {
            const currentStep =
              (planCell.model.sharedModel.getMetadata().custom as any)
                ?.current_step_string || '';
            const nextStep =
              (planCell.model.sharedModel.getMetadata().custom as any)
                ?.next_step_string || '';
            const source = planCell.model.sharedModel.getSource() || '';

            console.log('Updating step floating box', currentStep, nextStep);

            void AppStateService.getPlanStateDisplay().updatePlan(
              currentStep,
              nextStep,
              source
            );
          } else if (!planCell) {
            void AppStateService.getPlanStateDisplay().updatePlan(
              undefined,
              undefined,
              undefined
            );
          }

          if (notebook.model?.cells) {
            for (const cell of notebook.model.cells) {
              cell.metadataChanged.connect(() => {
                // Refresh the context cell highlighting when metadata changes
                contextCellHighlighter.refreshHighlighting(notebook);
              });
            }
          }
        });
      }
    });

    // Register all commands
    registerCommands(app, palette);
    registerEvalCommands(app, palette);

    // Set up notebook tracking to update button state
    notebooks.activeCellChanged.connect((_, cell) => {
      if (cell) {
        // Get the current notebook path
        const notebookPath = notebooks.currentWidget?.context.path;
        if (!notebookPath) return;

        // Check if the cell has tracking ID metadata
        const metadata = cell.model.sharedModel.getMetadata() || {};
        let trackingId = '';

        if (
          metadata &&
          typeof metadata === 'object' &&
          'cell_tracker' in metadata &&
          metadata.cell_tracker &&
          typeof metadata.cell_tracker === 'object' &&
          'trackingId' in metadata.cell_tracker
        ) {
          trackingId = String(metadata.cell_tracker.trackingId);
        }

        // Update the button state based on whether this cell is in context
        const isInContext = trackingId
          ? notebookContextManager.isCellInContext(notebookPath, trackingId)
          : notebookContextManager.isCellInContext(notebookPath, cell.model.id);

        // Find the button
        const buttonNode = document.querySelector(
          '.jp-ToolbarButtonComponent[data-command="sage-ai-add-to-context"]'
        );
        if (buttonNode) {
          if (isInContext) {
            // Set to "Remove from Chat" state
            buttonNode.classList.add('in-context');

            const icon = buttonNode.querySelector('.jp-icon3');
            if (icon) {
              // Create a minus icon
              const minusIcon =
                '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"><path fill="currentColor" d="M5 13v-2h14v2z"/></svg>';
              icon.innerHTML = minusIcon;
            }

            const textSpan = buttonNode.querySelector('.button-text');
            if (textSpan) {
              textSpan.textContent = 'Remove from Chat';
            }
          } else {
            // Set to "Add to Chat" state
            buttonNode.classList.remove('in-context');

            const icon = buttonNode.querySelector('.jp-icon3');
            if (icon) {
              icon.innerHTML = addIcon.svgstr;
            }

            const textSpan = buttonNode.querySelector('.button-text');
            if (textSpan) {
              textSpan.textContent = 'Add to Context';
            }
          }
        }
      }
    });

    // Initialize the chat widget
    initializeChatContainer();
    initializeSettingsContainer();
  }
};
