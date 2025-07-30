export class WaitingUserReplyBoxManager {
  private container: HTMLElement | null = null;
  private waitingReplyBox: HTMLElement | null = null;

  public initialize(container: HTMLElement): void {
    if (this.waitingReplyBox) {
      return;
    }

    this.container = container;

    // Create the waiting reply box
    this.waitingReplyBox = document.createElement('div');
    this.waitingReplyBox.className = 'sage-ai-waiting-reply-container';

    const text = document.createElement('div');
    text.className = 'sage-ai-waiting-reply-text';
    text.textContent = 'Sage will continue working after you reply';

    this.waitingReplyBox.appendChild(text);

    this.hide();

    // Add to the container
    this.container.appendChild(this.waitingReplyBox);
  }

  public hide(): void {
    if (this.waitingReplyBox) {
      this.waitingReplyBox.style.display = 'none';
    }
  }

  public show(): void {
    if (this.waitingReplyBox) {
      this.waitingReplyBox.style.display = 'block';
    }
  }
}
