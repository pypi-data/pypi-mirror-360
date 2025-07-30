import { LabIcon } from '@jupyterlab/ui-components';
import modeIcon from '../../style/icons/chat_input/mode.svg';
import handsOnModeIcon from '../../style/icons/chat_input/hands-on-mode.svg';
import askIcon from '../../style/icons/chat_input/ask-mode.svg';
import openModeSelectorIcon from '../../style/icons/chat_input/open.svg';
import sendIcon from '../../style/icons/chat_input/send.svg';
import stopIcon from '../../style/icons/chat_input/stop.svg';
export const MODE_ICON = new LabIcon({
  name: 'sage-agent:my-icon', // unique name for your icon
  svgstr: modeIcon // the imported SVG content as string
});

export const HANDS_ON_MODE_ICON = new LabIcon({
  name: 'sage-agent:hands-on-icon',
  svgstr: handsOnModeIcon
});

export const ASK_ICON = new LabIcon({
  name: 'sage-agent:ask-icon',
  svgstr: askIcon
});

export const OPEN_MODE_SELECTOR_ICON = new LabIcon({
  name: 'sage-agent:open-mode-selector-icon',
  svgstr: openModeSelectorIcon
});

export const SEND_ICON = new LabIcon({
  name: 'sage-agent:send-icon',
  svgstr: sendIcon
});

export const STOP_ICON = new LabIcon({
  name: 'sage-agent:stop-icon',
  svgstr: stopIcon
});
