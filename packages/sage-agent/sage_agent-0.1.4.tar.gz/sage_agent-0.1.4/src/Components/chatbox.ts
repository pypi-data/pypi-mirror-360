import { ChatMessages } from '../Chat/ChatMessages';
import { ConversationService } from '../Chat/ConversationService';
import { PanelLayout, Widget } from '@lumino/widgets';
import { Message } from '@lumino/messaging';
import { ConfigService } from '../Config/ConfigService';
import { IChatService } from '../Services/IChatService';
import { ServiceFactory, ServiceProvider } from '../Services/ServiceFactory';
import { ChatHistoryManager, IChatThread } from '../Chat/ChatHistoryManager';
import { ThreadManager } from '../ThreadManager';
import { ChatInputManager } from '../Chat/ChatInputManager';
import { RichTextChatInput } from '../Chat/RichTextChatInput';
import { ChatUIHelper } from '../Chat/ChatUIHelper';
import { AnthropicService } from '../Services/AnthropicService';
import { AppStateService } from '../AppState';
import { ChatboxContext } from './ChatboxContext';
import { NewChatDisplayWidget } from './NewChatDisplayWidget';
import { LLMStateDisplay } from './LLMStateDisplay/LLMStateDisplay';
import {
  HANDS_ON_MODE_ICON,
  ASK_ICON,
  MODE_ICON,
  OPEN_MODE_SELECTOR_ICON,
  SEND_ICON
} from './icons';
import { PlanStateDisplay } from './PlanStateDisplay';
import { MoreOptionsDisplay, IMoreOptionsActions } from './MoreOptionsDisplay';
import { Subscription } from 'rxjs';

// Recommended prompts for new chat display
const RECOMMENDED_PROMPTS: string[] = [
  // 'Analyze the data in my notebook',
  // 'Create a visualization from my data',
  // 'Help me clean and preprocess this dataset',
  // 'Build a machine learning model',
  // 'Explain this code and suggest improvements'
];

/**
 * ChatBoxWidget: A widget for interacting with AI services via a chat interface
 */
export class ChatBoxWidget extends Widget {
  private chatHistory: HTMLDivElement;
  private chatInput: RichTextChatInput;
  private sendButton: HTMLButtonElement;
  private newChatButton: HTMLButtonElement;
  private undoButton: HTMLButtonElement;
  private autorunCheckbox: HTMLInputElement;

  private threadSelectorButton: HTMLButtonElement;
  private modeSelector: HTMLDivElement;
  private threadNameDisplay: HTMLSpanElement;
  private modeSelectorDropdown: HTMLDivElement;
  private modeSelectorOptions: Map<string, HTMLDivElement> = new Map();
  private modeName: 'agent' | 'ask' | 'fast' = 'agent';

  // Widget management
  private historyWidget: Widget | null = null;
  private newChatDisplayWidget: NewChatDisplayWidget | null = null;
  public llmStateDisplay: LLMStateDisplay;
  private planStateDisplay: PlanStateDisplay;
  private moreOptionsDisplay: MoreOptionsDisplay;

  // Chat services
  private messageComponent: ChatMessages;
  private chatService: IChatService;
  public conversationService: ConversationService;
  private currentServiceProvider: ServiceProvider = ServiceProvider.ANTHROPIC;
  public chatHistoryManager: ChatHistoryManager;

  // Helper classes
  public threadManager: ThreadManager;
  public inputManager: ChatInputManager;
  private uiHelper: ChatUIHelper;
  private contextHandler: ChatboxContext;

  // Observer cleanup
  private resizeObserver?: ResizeObserver;
  private mutationObserver?: MutationObserver;
  private llmStateConnection?: any;
  private planStateConnection?: any;
  private appStateSubscription?: Subscription;
  private lastClaudeSettings?: {
    claudeApiKey: string;
    claudeModelId: string;
    claudeModelUrl: string;
  };

  constructor() {
    super();
    this.id = 'sage-ai-chat';
    this.title.label = 'AI Chat';
    this.title.closable = true;
    this.addClass('sage-ai-chatbox');

    // Initialize the chat history manager
    this.chatHistoryManager = new ChatHistoryManager();

    // Initialize services
    this.chatService = ServiceFactory.createService(
      this.currentServiceProvider
    );

    // Create layout for the chat box
    const layout = new PanelLayout();
    this.layout = layout;

    // Create toolbar
    const toolbar = document.createElement('div');
    toolbar.className = 'sage-ai-toolbar';

    // Create thread selector button
    this.threadSelectorButton = document.createElement('button');
    this.threadSelectorButton.className =
      'sage-ai-icon-button-md sage-ai-thread-selector-button';

    // Add chat icon SVG
    this.threadSelectorButton.innerHTML = `
     <svg width="20" height="21" viewBox="0 0 20 21" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M2.5 10.5H17.5M2.5 5.5H17.5M2.5 15.5H17.5" stroke="#949494" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `;
    this.threadSelectorButton.title = 'Select conversation thread';

    toolbar.appendChild(this.threadSelectorButton);

    // Create thread name display
    this.threadNameDisplay = document.createElement('span');
    this.threadNameDisplay.className = 'sage-ai-thread-name';
    this.threadNameDisplay.textContent =
      this.chatHistoryManager.getCurrentThread()?.name || 'New Chat';
    toolbar.appendChild(this.threadNameDisplay);

    // Create autorun checkbox container
    const checkboxContainer = document.createElement('div');
    checkboxContainer.className =
      'sage-ai-checkbox-container sage-ai-autorun-toggle sage-ai-control-base';

    this.autorunCheckbox = document.createElement('input');
    this.autorunCheckbox.id = 'sage-ai-autorun';
    this.autorunCheckbox.type = 'checkbox';
    this.autorunCheckbox.className = 'sage-ai-checkbox sage-ai-toggle-input';
    this.autorunCheckbox.title = 'Automatically run code without confirmation';

    const checkboxLabel = document.createElement('label');
    checkboxLabel.htmlFor = 'sage-ai-autorun';
    checkboxLabel.className = 'sage-ai-checkbox-label sage-ai-toggle-label';
    checkboxLabel.innerHTML = `
      <span class="sage-ai-toggle-switch"></span>
      Auto Run
    `;
    checkboxLabel.title = 'Automatically run code without confirmation';

    checkboxContainer.appendChild(this.autorunCheckbox);
    checkboxContainer.appendChild(checkboxLabel);

    // Create new chat button (previously reset button)
    this.newChatButton = document.createElement('button');
    this.newChatButton.className = 'sage-ai-reset-button sage-ai-control-base';
    this.newChatButton.innerHTML = `
      <svg width="16" height="17" viewBox="0 0 16 17" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3.3335 8.49992H12.6668M8.00016 3.83325V13.1666" stroke="var(--jp-ui-font-color0)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `;
    this.newChatButton.title = 'Start a new chat';
    this.newChatButton.addEventListener('click', () => this.createNewChat());

    // Create undo button
    this.undoButton = document.createElement('button');
    this.undoButton.className = 'sage-ai-undo-button sage-ai-control-base';
    this.undoButton.innerHTML = `
      <svg width="16" height="17" viewBox="0 0 16 17" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M5.99984 9.83341L2.6665 6.50008M2.6665 6.50008L5.99984 3.16675M2.6665 6.50008H9.6665C10.148 6.50008 10.6248 6.59492 11.0697 6.77919C11.5145 6.96346 11.9187 7.23354 12.2592 7.57402C12.5997 7.9145 12.8698 8.31871 13.0541 8.76357C13.2383 9.20844 13.3332 9.68523 13.3332 10.1667C13.3332 10.6483 13.2383 11.1251 13.0541 11.5699C12.8698 12.0148 12.5997 12.419 12.2592 12.7595C11.9187 13.1 11.5145 13.37 11.0697 13.5543C10.6248 13.7386 10.148 13.8334 9.6665 13.8334H7.33317" stroke="var(--jp-ui-font-color0)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `;
    this.undoButton.disabled = true;
    this.undoButton.title = 'No action to undo';
    this.undoButton.addEventListener('click', () => this.undoLastAction());

    // Create a button to show more options
    const moreOptionsButton = document.createElement('button');
    moreOptionsButton.className =
      'sage-ai-more-options-button sage-ai-icon-button-md';
    moreOptionsButton.innerHTML = `
      <svg width="18" height="19" viewBox="0 0 18 19" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M9 10.25C9.41421 10.25 9.75 9.91421 9.75 9.5C9.75 9.08579 9.41421 8.75 9 8.75C8.58579 8.75 8.25 9.08579 8.25 9.5C8.25 9.91421 8.58579 10.25 9 10.25Z" stroke="var(--jp-ui-font-color0)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M14.25 10.25C14.6642 10.25 15 9.91421 15 9.5C15 9.08579 14.6642 8.75 14.25 8.75C13.8358 8.75 13.5 9.08579 13.5 9.5C13.5 9.91421 13.8358 10.25 14.25 10.25Z" stroke="var(--jp-ui-font-color0)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M3.75 10.25C4.16421 10.25 4.5 9.91421 4.5 9.5C4.5 9.08579 4.16421 8.75 3.75 8.75C3.33579 8.75 3 9.08579 3 9.5C3 9.91421 3.33579 10.25 3.75 10.25Z" stroke="var(--jp-ui-font-color0)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `;
    moreOptionsButton.title = 'More options';
    moreOptionsButton.addEventListener('click', () => this.showMoreOptions());

    // Add buttons to toolbar
    toolbar.appendChild(checkboxContainer);
    toolbar.appendChild(this.undoButton);
    toolbar.appendChild(this.newChatButton);
    toolbar.appendChild(moreOptionsButton);

    // Create chat history container
    const historyContainer = document.createElement('div');
    historyContainer.className = 'sage-ai-history-container';
    this.chatHistory = document.createElement('div');
    this.chatHistory.className = 'sage-ai-chat-history';
    historyContainer.appendChild(this.chatHistory);

    // Create the initial history widget
    this.historyWidget = new Widget({ node: historyContainer });

    // Initialize LLM state display
    this.llmStateDisplay = new LLMStateDisplay();

    this.planStateDisplay = AppStateService.getPlanStateDisplay();

    // Initialize more options display
    this.moreOptionsDisplay = new MoreOptionsDisplay({
      onRenameChat: () => this.handleRenameChat(),
      onDeleteChat: () => this.handleDeleteChat()
    });

    // Initialize message component with the chat history manager
    this.messageComponent = new ChatMessages(
      this.chatHistory,
      this.chatHistoryManager,
      AppStateService.getNotebookTools()
    );

    // Create input container with text input and send button
    const inputContainer = document.createElement('div');
    inputContainer.className = 'sage-ai-input-container';
    inputContainer.style.position = 'relative'; // Add relative positioning

    // Create inner chatbox wrapper for the focused styling
    const chatboxWrapper = document.createElement('div');
    chatboxWrapper.className = 'sage-ai-chatbox-wrapper';

    // Create context row (first row)
    const contextRow = document.createElement('div');
    contextRow.className = 'sage-ai-context-row';

    // Create "Add Context" button with @ icon
    const addContextButton = document.createElement('button');
    addContextButton.className = 'sage-ai-add-context-button';
    addContextButton.innerHTML = '@';
    addContextButton.title = 'Add context';
    addContextButton.type = 'button';

    // Add click handler for the Add Context button
    addContextButton.addEventListener('click', e => {
      e.preventDefault();
      e.stopPropagation();
      // Focus the input and trigger mention dropdown by inserting @
      this.chatInput.focus();
      const currentText = this.chatInput.getPlainText();
      const cursorPosition = this.chatInput.getSelectionStart();
      const newText =
        currentText.slice(0, cursorPosition) +
        '@' +
        currentText.slice(cursorPosition);
      this.chatInput.setPlainText(newText);
      // Set cursor position after the @
      setTimeout(() => {
        this.chatInput.setSelectionRange(
          cursorPosition + 1,
          cursorPosition + 1
        );
        // Trigger input event to activate mention dropdown
        const inputEvent = new Event('input', { bubbles: true });
        this.chatInput.getInputElement().dispatchEvent(inputEvent);
      }, 0);
    });

    // Create context display container
    const contextDisplay = document.createElement('div');
    contextDisplay.className = 'sage-ai-context-display-inline';

    contextRow.appendChild(addContextButton);
    contextRow.appendChild(contextDisplay);

    // Create input row (second row)
    const inputRow = document.createElement('div');
    inputRow.className = 'sage-ai-input-row';

    // Replace input with rich text input
    this.chatInput = new RichTextChatInput(
      'What would you like me to generate or analyze?'
    );
    this.chatInput.getInputElement().style.paddingRight = '60px'; // Add padding to make room for the button

    // Handle keydown events for submission
    this.chatInput.addEventListener('keydown', (event: Event) => {
      const keyEvent = event as KeyboardEvent;
      // Submit on Enter (without shift for newlines)
      if (
        keyEvent.key === 'Enter' &&
        !keyEvent.shiftKey &&
        this.chatInput.getPlainText().trim() !== '' &&
        !this.inputManager.getIsProcessingMessage()
      ) {
        keyEvent.preventDefault(); // Prevent newline
        this.inputManager.sendMessage();
      }
    });

    this.sendButton = document.createElement('button');
    SEND_ICON.render(this.sendButton);
    this.sendButton.className = 'sage-ai-send-button';
    this.sendButton.style.position = 'absolute'; // Set absolute positioning
    this.sendButton.style.bottom = '25px'; // Position at bottom
    this.sendButton.style.right = '25px'; // Position at right
    this.sendButton.addEventListener('click', () => {
      if (this.inputManager.getIsProcessingMessage()) {
        this.cancelMessage();
      } else if (this.chatInput.getPlainText().trim() !== '') {
        this.inputManager.sendMessage();
      }
    });

    // Create mode selector
    this.modeSelector = document.createElement('div');
    this.modeSelector.className = 'sage-ai-mode-selector';
    this.modeSelector.title = 'Select chat mode';

    // Create dropdown container
    this.modeSelectorDropdown = document.createElement('div');
    this.modeSelectorDropdown.className = 'sage-ai-mode-dropdown hidden';

    // Create content wrapper for flexbox layout
    const dropdownContent = document.createElement('div');
    dropdownContent.className = 'sage-ai-mode-dropdown-content';

    // Create options
    const agentOption = this.createOption(
      'agent',
      'Agent',
      MODE_ICON.svgstr,
      'Prepare datasets. Build models. Test ideas.'
    );
    const askOption = this.createOption(
      'ask',
      'Ask',
      ASK_ICON.svgstr,
      'Ask Sage about your notebook or your data.'
    );
    const handsOnOption = this.createOption(
      'fast',
      'Hands-on',
      HANDS_ON_MODE_ICON.svgstr,
      'Manually decide what gets added to the context.'
    );

    dropdownContent.appendChild(agentOption);
    dropdownContent.appendChild(askOption);
    dropdownContent.appendChild(handsOnOption);
    this.modeSelectorDropdown.appendChild(dropdownContent);

    // Set initial display (Agent selected by default)
    this.updateModeSelectorDisplay('agent');

    // Add click handler to toggle dropdown
    this.modeSelector.addEventListener('click', e => {
      e.stopPropagation();
      this.toggleModeDropdown();
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', () => {
      this.closeModeDropdown();
    });

    // Assemble the input structure
    inputRow.appendChild(this.chatInput.getElement());
    inputRow.appendChild(this.sendButton);
    inputRow.appendChild(this.modeSelector);

    chatboxWrapper.appendChild(contextRow);
    chatboxWrapper.appendChild(inputRow);
    inputContainer.appendChild(chatboxWrapper);
    // Note: modeSelectorDropdown will be appended to body when opened

    const newPromptCTA = document.createElement('div');
    newPromptCTA.className = 'sage-ai-new-prompt-cta';
    const text = document.createElement('p');
    text.textContent = 'Want to start a new prompt?';
    const chatCTA = document.createElement('a');
    chatCTA.textContent = 'Create a New Chat';
    chatCTA.onclick = () => {
      this.createNewChat();
      return false; // Prevent default link behavior
    };
    newPromptCTA.appendChild(text);
    newPromptCTA.appendChild(chatCTA);

    this.newChatDisplayWidget = new NewChatDisplayWidget(
      {
        onPromptSelected: prompt => {
          this.inputManager.setInputValue(prompt);
          this.inputManager.sendMessage();
          this.showHistoryWidget();
        },
        onRemoveDisplay: () => {
          this.showHistoryWidget();
        }
      },
      RECOMMENDED_PROMPTS
    );

    // Add components to the layout
    layout.addWidget(new Widget({ node: toolbar }));
    layout.addWidget(this.historyWidget);
    layout.addWidget(this.newChatDisplayWidget);

    this.showHistoryWidget();

    const inputContainerWidget = new Widget({ node: inputContainer });

    // Create wrapper for state displays with fixed positioning and flexbox
    const stateDisplayContainer = document.createElement('div');
    stateDisplayContainer.className = 'sage-ai-state-display-container';
    stateDisplayContainer.style.position = 'fixed';
    stateDisplayContainer.style.bottom = '0';
    stateDisplayContainer.style.left = '0';
    stateDisplayContainer.style.right = '0';
    stateDisplayContainer.style.pointerEvents = 'none'; // Allow clicks to pass through
    stateDisplayContainer.style.zIndex = '1';
    stateDisplayContainer.style.display = 'flex';
    stateDisplayContainer.style.flexDirection = 'column';
    stateDisplayContainer.style.alignItems = 'stretch';
    stateDisplayContainer.style.gap = '4px';

    // Widget nodes will get their styles from CSS classes
    const planStateNode = this.planStateDisplay.getWidget().node;
    const llmStateNode = this.llmStateDisplay.getWidget().node;

    // Create spacer for input container height
    const inputSpacer = document.createElement('div');
    inputSpacer.className = 'sage-ai-input-spacer';
    inputSpacer.style.order = '3'; // Input spacer appears last
    inputSpacer.style.flexShrink = '0';

    // Function to update container positioning based on input container height
    const updateWrapperPositions = () => {
      const inputHeight = inputContainer.offsetHeight;

      // Update the spacer height to match input container + some spacing
      inputSpacer.style.height = `${inputHeight + 16}px`;

      // Use requestAnimationFrame to ensure DOM updates are complete before calculating heights
      requestAnimationFrame(() => {
        setTimeout(() => {
          // Calculate dynamic padding for history container
          let totalStateHeight = 0;

          // Check if LLM state display is hidden
          const isLLMHidden =
            this.llmStateDisplay.node.classList.contains('hidden');

          // Add LLM state height if visible
          if (!isLLMHidden && this.llmStateDisplay.node.offsetHeight > 0) {
            totalStateHeight += this.llmStateDisplay.node.offsetHeight;
          }

          // Add plan state height if visible
          if (
            this.planStateDisplay.getIsVisible() &&
            this.planStateDisplay.node.offsetHeight > 0
          ) {
            totalStateHeight += this.planStateDisplay.node.offsetHeight;
          }

          // Apply the dynamic padding to history container
          this.chatHistory.parentElement!.style.paddingBottom = `${totalStateHeight - 16}px`;
        }, 200); // Additional delay to ensure transitions/animations complete
      });
    };

    // Store the positioning function for later use
    (this as any).updateStateDisplayPositions = updateWrapperPositions;

    // Connect to state change signals instead of overriding methods
    this.llmStateConnection = this.llmStateDisplay.stateChanged.connect(() => {
      setTimeout(updateWrapperPositions, 100);
    });

    this.planStateConnection = this.planStateDisplay.stateChanged.connect(
      () => {
        setTimeout(updateWrapperPositions, 100);
      }
    );

    // Initial positioning
    setTimeout(updateWrapperPositions, 100); // Increased timeout to ensure DOM is rendered

    // Update positioning when window resizes or layout changes
    this.resizeObserver = new ResizeObserver(updateWrapperPositions);
    this.resizeObserver.observe(inputContainer);

    // Add MutationObserver to watch for content changes in state displays
    this.mutationObserver = new MutationObserver(() => {
      setTimeout(updateWrapperPositions, 100); // Increased delay to ensure DOM updates complete
    });

    // Observe both state displays for changes (mainly for expanded content size changes)
    this.mutationObserver.observe(this.llmStateDisplay.node, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class'] // Focus on class changes like 'hidden'
    });

    this.mutationObserver.observe(this.planStateDisplay.node, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class'] // Focus on class changes and content size changes
    });

    // Add widgets directly to container in order: plan state, LLM state, input spacer
    stateDisplayContainer.appendChild(planStateNode);
    stateDisplayContainer.appendChild(llmStateNode);
    stateDisplayContainer.appendChild(inputSpacer);

    // Add the container to the layout
    layout.addWidget(inputContainerWidget);
    layout.addWidget(new Widget({ node: stateDisplayContainer }));
    layout.addWidget(new Widget({ node: newPromptCTA }));
    layout.addWidget(this.moreOptionsDisplay);

    // Initialize helper classes
    this.threadManager = new ThreadManager(
      this.chatHistoryManager,
      this.messageComponent,
      this.chatService,
      this.threadNameDisplay,
      this.node
    );

    this.inputManager = new ChatInputManager(
      this.chatInput,
      this.chatHistoryManager,
      inputContainer,
      AppStateService.getContentManager(),
      AppStateService.getToolService(),
      context => {
        // Handle context selection - add to ChatMessages
        this.messageComponent.addMentionContext(context);
        this.contextHandler.updateContextDisplay();
        console.log('Context added:', context);
      },
      contextId => {
        // Handle context removal - remove from ChatMessages
        this.messageComponent.removeMentionContext(contextId);
        this.contextHandler.updateContextDisplay();
        console.log(`Context removed: ${contextId}`);
      },
      () => this.createNewChat() // Handle reset chat
    );

    this.uiHelper = new ChatUIHelper(
      this.chatHistory,
      this.messageComponent,
      this.llmStateDisplay
    );

    // Initialize context handler early so it can be used in other components
    this.contextHandler = new ChatboxContext(
      this.messageComponent,
      this.inputManager,
      this.node
    );

    // Initialize the conversation service with the diffManager
    this.conversationService = new ConversationService(
      this.chatService,
      AppStateService.getToolService(),
      AppStateService.getContentManager(),
      this.messageComponent,
      this.chatHistory,
      this
    );

    // Set the diff manager in the conversation service if available
    const diffManager = AppStateService.getState().notebookDiffManager;
    if (diffManager) {
      this.conversationService.setDiffManager(diffManager);
    }

    // Set up event handlers
    this.setupEventHandlers();

    // Initialize services
    this.initializeServices();

    // Subscribe to AppState changes to re-initialize services when Claude settings change
    this.subscribeToAppStateChanges();

    // Set dependencies in input manager for sendMessage and revertAndSend
    this.inputManager.setDependencies({
      chatService: this.chatService,
      conversationService: this.conversationService,
      messageComponent: this.messageComponent,
      uiHelper: this.uiHelper,
      contextHandler: this.contextHandler,
      sendButton: this.sendButton,
      modeSelector: this.modeSelector,
      updateUndoButtonState: () => this.updateUndoButtonState(),
      cancelMessage: () => this.cancelMessage(),
      onMessageSent: () => this.showHistoryWidget()
    });

    // Set up polling to update undo button state
    setInterval(() => this.updateUndoButtonState(), 1000);

    // Initialize managers

    const waitingUserReplyBoxManager =
      AppStateService.getWaitingUserReplyBoxManager();
    waitingUserReplyBoxManager.initialize(inputContainer);

    // Initialize context display after everything is set up
    this.contextHandler.updateContextDisplay();

    if (this.messageComponent.getMessageHistory().length === 0)
      this.showNewChatDisplay();
  }

  /**
   * Create a custom option element for the mode selector dropdown
   * @param value The value of the option
   * @param text The display text
   * @param iconSvg The SVG icon string
   * @returns The HTML div element representing the option
   */
  private createOption(
    value: string,
    text: string,
    iconSvg: string,
    description: string
  ): HTMLDivElement {
    const option = document.createElement('div');
    option.className = 'sage-ai-mode-option';
    option.setAttribute('data-value', value);

    const iconContainer = document.createElement('div');
    iconContainer.className = 'sage-ai-mode-option-icon';
    iconContainer.innerHTML = iconSvg;

    const textElement = document.createElement('div');
    textElement.innerHTML = `
      <p class="sage-ai-mode-option-title">
      ${text}
       </p>
       <p class="sage-ai-mode-option-description">
      ${description}
       </p>
    `;
    textElement.className = 'sage-ai-mode-option-text';

    option.appendChild(iconContainer);
    option.appendChild(textElement);

    // Store reference for easy access
    this.modeSelectorOptions.set(value, option);

    // Add click handler
    option.addEventListener('click', e => {
      e.stopPropagation();
      this.selectMode(value);
    });

    return option;
  }

  /**
   * Update the mode selector display to show the selected mode
   * @param mode The selected mode ('agent' or 'ask')
   */
  private updateModeSelectorDisplay(mode: string): void {
    const selectedOption = this.modeSelectorOptions.get(mode);
    if (selectedOption) {
      // Clear current display
      this.modeSelector.innerHTML = '';

      // Create a display option without description
      const displayOption = document.createElement('div');
      displayOption.className = 'sage-ai-mode-display';

      // Clone only the icon from the selected option
      const originalIcon = selectedOption.querySelector(
        '.sage-ai-mode-option-icon'
      );
      if (originalIcon) {
        const iconContainer = originalIcon.cloneNode(true) as HTMLDivElement;
        displayOption.appendChild(iconContainer);
      }

      // Create text element with only the title (no description)
      const originalText = selectedOption.querySelector(
        '.sage-ai-mode-option-text'
      );
      if (originalText) {
        const titleElement = originalText.querySelector(
          '.sage-ai-mode-option-title'
        );
        if (titleElement) {
          const textElement = document.createElement('div');
          textElement.className = 'sage-ai-mode-option-text';
          textElement.innerHTML = titleElement.innerHTML;
          displayOption.appendChild(textElement);
        }
      }

      // Add dropdown arrow
      const arrow = document.createElement('div');
      arrow.className = 'sage-ai-mode-selector-arrow';
      OPEN_MODE_SELECTOR_ICON.render(arrow);

      this.modeSelector.appendChild(displayOption);
      this.modeSelector.appendChild(arrow);
    }
  }

  /**
   * Toggle the visibility of the mode dropdown
   */
  private toggleModeDropdown(): void {
    if (this.modeSelectorDropdown.classList.contains('hidden')) {
      this.openModeDropdown();
    } else {
      this.closeModeDropdown();
    }
  }

  /**
   * Open the mode dropdown
   */
  private openModeDropdown(): void {
    // Add opening class to mode selector
    this.modeSelector.classList.add('open');

    // Position the dropdown above the selector
    const rect = this.modeSelector.getBoundingClientRect();
    this.modeSelectorDropdown.style.position = 'absolute';
    this.modeSelectorDropdown.style.bottom = `${window.innerHeight - rect.top + 8}px`;
    this.modeSelectorDropdown.style.left = `${rect.left}px`;
    this.modeSelectorDropdown.style.minWidth = `${rect.width}px`;

    // Append to body to ensure it appears above other elements
    document.body.appendChild(this.modeSelectorDropdown);

    // Remove hidden class and add visible class with slight delay for animation
    this.modeSelectorDropdown.classList.remove('hidden');
    this.modeSelectorDropdown.classList.add('opening');

    // Use requestAnimationFrame to ensure the element is rendered before adding visible class
    requestAnimationFrame(() => {
      this.modeSelectorDropdown.classList.add('visible');
    });

    // Clean up animation class after animation completes
    setTimeout(() => {
      this.modeSelectorDropdown.classList.remove('opening');
    }, 300);
  }

  /**
   * Close the mode dropdown
   */
  private closeModeDropdown(): void {
    // Remove open class from mode selector
    this.modeSelector.classList.remove('open');

    // Add closing animation
    this.modeSelectorDropdown.classList.add('closing');
    this.modeSelectorDropdown.classList.remove('visible');

    // Remove from DOM after animation completes
    setTimeout(() => {
      this.modeSelectorDropdown.classList.add('hidden');
      this.modeSelectorDropdown.classList.remove('closing');

      // Remove from body if it was appended there
      if (this.modeSelectorDropdown.parentNode === document.body) {
        document.body.removeChild(this.modeSelectorDropdown);
      }
    }, 200);
  }

  /**
   * Select a mode and update the UI
   * @param mode The mode to select ('agent' or 'ask')
   */
  private selectMode(mode: string): void {
    this.modeName = mode as 'agent' | 'ask' | 'fast';
    this.inputManager.setModeName(this.modeName);

    // Handle fast mode when "fast" (Hands-on) mode is selected
    if (this.chatService instanceof AnthropicService) {
      const isFastMode = mode === 'fast';
      // Display appropriate system message
      if (isFastMode) {
        const toolBlacklist = (
          this.chatService as AnthropicService
        ).getToolBlacklist();
        this.messageComponent.addSystemMessage(
          `Hands-on mode enabled. Using optimized prompt and limiting certain tools: ${toolBlacklist.join(', ')}`
        );
      }
    }

    this.updateModeSelectorDisplay(mode);
    this.closeModeDropdown();

    const displayName =
      mode === 'agent' ? 'Agent' : mode === 'ask' ? 'Ask' : 'Hands-on';
    this.messageComponent.addSystemMessage(`Mode switched to: ${displayName}`);
  }

  public updateNotebookPath(newPath: string): void {
    AppStateService.setCurrentNotebookPath(newPath);
    this.threadManager.updateNotebookPath(newPath);
    this.conversationService.updateNotebookPath(newPath);
  }

  /**
   * Setup event handlers
   */
  private setupEventHandlers(): void {
    // Add click event to open left side banner
    this.threadSelectorButton.addEventListener('click', () => {
      this.threadManager.openBanner();
    });

    // Add event listener to autorun checkbox to update the conversation service
    this.autorunCheckbox.addEventListener('change', () => {
      this.conversationService.setAutoRun(this.autorunCheckbox.checked);

      // Display a system message to confirm the change
      if (this.autorunCheckbox.checked) {
        this.messageComponent.addSystemMessage(
          'Auto-run mode enabled. Code will execute automatically without confirmation.'
        );
      } else {
        this.messageComponent.addSystemMessage(
          'Auto-run mode disabled. You will be prompted for code execution.'
        );
      }
    });
  }

  /**
   * Initialize all services
   */
  private async initializeServices(): Promise<void> {
    try {
      // Get configuration from server
      const config = await ConfigService.getConfig();

      // Initialize chat service with config from server
      const initialized = await this.chatService.initialize();
      console.log('Chat service initialized:', initialized);

      if (initialized) {
        const modelName = this.chatService.getModelName();
        // this.messageComponent.addSystemMessage(
        //   `✅ Configuration loaded successfully. Using model: ${modelName}`
        // );
      } else {
        this.messageComponent.addSystemMessage(
          '⚠️ Failed to initialize with API key from config. Please check the server.'
        );
      }

      // Initialize tool service
      const toolService = AppStateService.getToolService();
      await toolService.initialize();
      console.log('Connected to MCP server successfully.');
      console.log(
        `Loaded ${toolService.getTools().length} tools from MCP server.`
      );
    } catch (error) {
      console.error('Failed to connect to MCP server:', error);
      this.messageComponent.addSystemMessage(
        '❌ Failed to connect to MCP server. Some features may not work.'
      );
    }
  }

  /**
   * Update the notebook path and load its chat history
   * @param notebookPath Path to the notebook
   */
  public setNotebookPath(notebookPath: string | undefined): void {
    if (!notebookPath) {
      AppStateService.setCurrentNotebookPath(null);
      this.threadManager.setNotebookPath(null);
      return;
    }

    const currentNotebookPath = AppStateService.getState().currentNotebookPath;
    if (notebookPath !== currentNotebookPath) {
      console.log(`[ChatBoxWidget] Switching to notebook: ${notebookPath}`);
      AppStateService.setCurrentNotebookPath(notebookPath);

      // Load the chat history for this notebook
      this.chatHistoryManager.setCurrentNotebook(notebookPath);

      // Update the thread manager with the current notebook path
      this.threadManager.setNotebookPath(notebookPath);

      // Show appropriate widget based on whether there are messages
      this.showNewChatDisplayOrHistory();

      // Update conversation service with the current notebook path
      this.conversationService.setNotebookPath(notebookPath);
    }

    // Refresh user message history when switching notebooks
    this.inputManager.loadUserMessageHistory();

    // Update context cells indicator when switching notebooks
    const contextManager = AppStateService.getState().notebookContextManager;
    if (contextManager) {
      const contextCells = contextManager.getContextCells(notebookPath);
      this.contextHandler.updateContextCellsIndicator(contextCells.length);
    }
  }

  /**
   * Create a new chat thread
   */
  private async createNewChat(): Promise<void> {
    // Hide the waiting reply box when user cancels
    AppStateService.getWaitingUserReplyBoxManager().hide();

    // Only proceed if we have an active notebook
    const currentNotebookPath = AppStateService.getState().currentNotebookPath;
    if (!currentNotebookPath) {
      this.messageComponent.addSystemMessage('Please open a notebook first.');
      return;
    }

    // Cancel any ongoing request - make sure to update the UI state as well
    if (this.inputManager.getIsProcessingMessage()) {
      this.cancelMessage();
    } else {
      // Even if not visibly processing, cancel any pending requests
      this.chatService.cancelRequest();
    }

    // Create a new thread
    const newThread = this.threadManager.createNewThread();

    if (newThread) {
      // Clear action history
      this.conversationService.clearActionHistory();
      this.updateUndoButtonState();
      this.contextHandler.updateContextDisplay();

      // Switch to new chat display since there are no messages
      this.showNewChatDisplay();
    }
  }

  /**
   * Update the state of the undo button based on available actions
   */
  private updateUndoButtonState(): void {
    if (this.conversationService.canUndo()) {
      const actionDesc = this.conversationService.getLastActionDescription();
      this.undoButton.disabled = false;
      this.undoButton.title = `Undo: ${actionDesc}`;
    } else {
      this.undoButton.disabled = true;
      this.undoButton.title = 'No action to undo';
    }
  }

  /**
   * Undo the last action
   */
  private async undoLastAction(): Promise<void> {
    if (!this.conversationService.canUndo()) {
      return;
    }

    // Disable the button during undo
    this.undoButton.disabled = true;
    this.undoButton.title = 'Undoing...';

    try {
      // Perform the undo operation
      await this.conversationService.undoLastAction();
    } catch (error) {
      console.error('Error during undo:', error);
      this.messageComponent.addErrorMessage(
        `Error during undo: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    } finally {
      // Update the button state after undo completes
      this.updateUndoButtonState();
    }
  }

  /**
   * Cancel the current message processing
   */
  public cancelMessage(): void {
    console.log('Cancelling message...');
    console.log(this.inputManager.getIsProcessingMessage());
    if (!this.inputManager.getIsProcessingMessage()) {
      return;
    }

    console.log('Cancelling message processing...');

    // Cancel the request in the chatService
    this.chatService.cancelRequest();

    // Update state immediately to prevent any further processing
    this.inputManager.setIsProcessingMessage(false);

    // Remove loading indicator
    this.uiHelper.removeLoadingIndicator();

    this.messageComponent.addSystemMessage('Request cancelled by user.');
    this.messageComponent.removeLoadingText();
    this.uiHelper.updateSendButton(this.sendButton, false);
    AppStateService.getPlanStateDisplay().setLoading(false);
    this.uiHelper.updateAgentModeElement(this.modeSelector, false);

    const modeIcon = document.createElement('div');
    MODE_ICON.render(modeIcon);

    // Check if there are pending diffs and show approval dialog if needed
    const diffManager = AppStateService.getState().notebookDiffManager;
    if (
      diffManager &&
      diffManager.hasPendingDiffs() &&
      !diffManager.isDialogOpen()
    ) {
      // Show pending diffs in LLMStateDisplay
      if (this.llmStateDisplay) {
        const currentNotebookPath =
          AppStateService.getState().currentNotebookPath;
        this.llmStateDisplay.showPendingDiffs(currentNotebookPath);
      }

      // Use setTimeout to ensure UI updates before showing the dialog
      setTimeout(async () => {
        const currentNotebookPath =
          AppStateService.getState().currentNotebookPath;
        await diffManager?.showCancellationApprovalDialog(
          this.chatHistory,
          currentNotebookPath // Pass the notebook path
        );
      }, 100);
    } else {
      this.llmStateDisplay.show();
      this.llmStateDisplay.hide();
    }
  }

  /**
   * Send a message to the AI service
   */
  public async sendMessage(cell_context?: string): Promise<void> {
    return this.inputManager.sendMessage(cell_context);
  }

  /**
   * Set the Anthropic prompt and tool blacklist for quick edit mode.
   * This is used by the context cell highlighter for quick cell edits.
   */
  public setAnthropicPromptAndBlacklist(
    prompt: string,
    blacklist: string[]
  ): void {
    if (this.chatService instanceof AnthropicService) {
      (this.chatService as AnthropicService).setSystemPrompt(prompt);
      (this.chatService as AnthropicService).setToolBlacklist(blacklist);
    }
  }

  protected onAfterShow(): void {
    this.inputManager.focus();
  }

  /**
   * Update the loading indicator - exposed for the conversation service to use
   */
  public updateLoadingIndicator(text: string = 'Generating...'): void {
    this.uiHelper.updateLoadingIndicator(text);
  }

  /**
   * Remove the loading indicator - exposed for the conversation service to use
   */
  public removeLoadingIndicator(): void {
    this.uiHelper.removeLoadingIndicator();
  }

  /**
   * Handle a cell being added to context
   * @param notebookPath Path of the notebook containing the cell
   * @param cellId ID of the cell added to context
   */
  public onCellAddedToContext(notebookPath: string): void {
    this.contextHandler.onCellAddedToContext(notebookPath);
  }

  /**
   * Handle a cell being removed from context
   * @param notebookPath Path of the notebook containing the cell
   * @param cellId ID of the cell removed from context
   */
  public onCellRemovedFromContext(notebookPath: string): void {
    this.contextHandler.onCellRemovedFromContext(notebookPath);
  }

  /**
   * Show new chat display or history based on current thread state
   */
  public showNewChatDisplayOrHistory(): void {
    const currentThread = this.chatHistoryManager.getCurrentThread();
    const hasMessages = currentThread && currentThread.messages.length > 0;

    if (hasMessages) {
      this.showHistoryWidget();
    } else {
      this.showNewChatDisplay();
    }
  }

  /**
   * Show the new chat display widget
   */
  public showNewChatDisplay(): void {
    if (this.messageComponent.getMessageHistory().length > 0) return;
    if (this.newChatDisplayWidget) {
      this.newChatDisplayWidget.node.style.display = 'flex';
    }
    if (this.historyWidget) {
      this.historyWidget.node.style.display = 'none';
    }
  }

  /**
   * Show the history widget
   */
  public showHistoryWidget(): void {
    if (this.newChatDisplayWidget) {
      this.newChatDisplayWidget.node.style.display = 'none';
    }
    if (this.historyWidget) {
      this.historyWidget.node.style.display = 'block';
    }
  }

  /**
   * Show the more options popover
   */
  private showMoreOptions(): void {
    const moreOptionsButton = this.node.querySelector(
      '.sage-ai-more-options-button'
    ) as HTMLButtonElement;
    if (moreOptionsButton && this.moreOptionsDisplay) {
      this.moreOptionsDisplay.showPopover(moreOptionsButton);
    }
  }

  /**
   * Handle rename chat action
   */
  private async handleRenameChat(): Promise<void> {
    const currentThread = this.chatHistoryManager.getCurrentThread();
    if (!currentThread) {
      this.messageComponent.addSystemMessage('No active chat to rename.');
      return;
    }

    const newName = prompt('Enter new chat name:', currentThread.name);
    if (newName && newName.trim() !== '' && newName !== currentThread.name) {
      const success = this.chatHistoryManager.renameCurrentThread(
        newName.trim()
      );
      if (success) {
        this.threadNameDisplay.textContent = newName.trim();
        this.messageComponent.addSystemMessage(
          `Chat renamed to: ${newName.trim()}`
        );
      } else {
        this.messageComponent.addSystemMessage('Failed to rename chat.');
      }
    }
  }

  /**
   * Handle delete chat action
   */
  private async handleDeleteChat(): Promise<void> {
    const currentThread = this.chatHistoryManager.getCurrentThread();
    if (!currentThread) {
      this.messageComponent.addSystemMessage('No active chat to delete.');
      return;
    }

    const confirmDelete = confirm(
      `Are you sure you want to delete the chat "${currentThread.name}"? This action cannot be undone.`
    );
    if (confirmDelete) {
      const deletedThreadName = currentThread.name;
      const success = this.chatHistoryManager.deleteThread(currentThread.id);
      if (success) {
        this.messageComponent.addSystemMessage(
          `Chat "${deletedThreadName}" has been deleted.`
        );

        // Update thread name display for the new current thread
        const newCurrentThread = this.chatHistoryManager.getCurrentThread();
        if (newCurrentThread) {
          this.threadNameDisplay.textContent = newCurrentThread.name;
          this.messageComponent.loadFromThread(newCurrentThread);
          if (newCurrentThread.messages.length > 0) {
            this.showHistoryWidget();
          } else {
            this.showNewChatDisplay();
          }
        } else {
          this.showNewChatDisplay();
        }
      } else {
        this.messageComponent.addSystemMessage('Failed to delete chat.');
      }
    }
  }

  /**
   * Subscribe to AppState changes to re-initialize services when Claude settings change
   */
  private subscribeToAppStateChanges(): void {
    // Store initial Claude settings to compare against
    const initialClaudeSettings = AppStateService.getClaudeSettings();
    this.lastClaudeSettings = {
      claudeApiKey: initialClaudeSettings.claudeApiKey,
      claudeModelId: initialClaudeSettings.claudeModelId,
      claudeModelUrl: initialClaudeSettings.claudeModelUrl
    };

    this.appStateSubscription = AppStateService.changes.subscribe(state => {
      // Check if Claude settings have changed
      const currentClaudeSettings = {
        claudeApiKey: state.settings.claudeApiKey,
        claudeModelId: state.settings.claudeModelId,
        claudeModelUrl: state.settings.claudeModelUrl
      };

      const hasChanged =
        !this.lastClaudeSettings ||
        this.lastClaudeSettings.claudeApiKey !==
          currentClaudeSettings.claudeApiKey ||
        this.lastClaudeSettings.claudeModelId !==
          currentClaudeSettings.claudeModelId ||
        this.lastClaudeSettings.claudeModelUrl !==
          currentClaudeSettings.claudeModelUrl;

      if (hasChanged) {
        console.log(
          'Claude settings changed, re-initializing chat service...',
          {
            previous: this.lastClaudeSettings,
            current: currentClaudeSettings
          }
        );

        this.lastClaudeSettings = currentClaudeSettings;
        this.reinitializeChatService();
      }
    });
  }

  /**
   * Re-initialize the chat service with updated settings
   */
  private async reinitializeChatService(): Promise<void> {
    try {
      console.log(
        'Re-initializing chat service with updated Claude settings...'
      );

      // Re-initialize the chat service (it will automatically pick up new settings from AppState)
      const initialized = await this.chatService.initialize();
      console.log('Chat service re-initialized:', initialized);

      if (initialized) {
        const modelName = this.chatService.getModelName();
        // this.messageComponent.addSystemMessage(
        //   `✅ Settings updated successfully. Using model: ${modelName}`
        // );
      } else {
        this.messageComponent.addSystemMessage(
          '⚠️ Failed to re-initialize with updated settings. Please check your API key.'
        );
      }
    } catch (error) {
      console.error('Failed to re-initialize chat service:', error);
      this.messageComponent.addSystemMessage(
        '⚠️ Error updating settings. Please try again.'
      );
    }
  }

  public dispose(): void {
    this.resizeObserver?.disconnect();
    this.mutationObserver?.disconnect();
    this.llmStateConnection?.dispose();
    this.planStateConnection?.dispose();
    this.moreOptionsDisplay?.dispose();
    this.appStateSubscription?.unsubscribe();
    super.dispose();
  }
}
