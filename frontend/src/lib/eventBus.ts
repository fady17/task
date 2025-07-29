/**
 * A type definition for the callback functions that will handle events.
 * It can optionally receive a `data` payload of any type.
 */
type EventHandler = (data?: any) => void;

/**
 * A simple, lightweight, client-side event bus (also known as a Pub/Sub system).
 * This allows different, decoupled parts of the application to communicate with each other.
 * For example, the Chatbot feature can `emit` an event, and the Todos feature can `on` (listen for) that event
 * to know when it needs to update its state, without either feature needing to know about the other's internal logic.
 */
class EventBus {
  // A dictionary to store arrays of event handlers for each event name.
  // The key is the event name (e.g., 'state_change'), and the value is an array of functions.
  private events: Record<string, EventHandler[]> = {};

  /**
   * Subscribes to an event.
   * @param event The name of the event to listen for.
   * @param callback The function to execute when the event is emitted.
   */
  public on(event: string, callback: EventHandler): void {
    // If no one is listening to this event yet, create an empty array for it.
    if (!this.events[event]) {
      this.events[event] = [];
    }
    // Add the new callback function to the list of listeners for this event.
    this.events[event].push(callback);
  }

  /**
   * Unsubscribes from an event. This is crucial for preventing memory leaks in React components.
   * @param event The name of the event to stop listening to.
   * @param callback The specific callback function to remove.
   */
  public off(event: string, callback: EventHandler): void {
    // If the event doesn't exist in our record, there's nothing to do.
    if (!this.events[event]) return;

    // Filter the array of listeners, keeping only those that are NOT the one we want to remove.
    this.events[event] = this.events[event].filter(
      (eventCallback) => callback !== eventCallback
    );
  }

  /**
   * Emits (or publishes) an event, triggering all subscribed callbacks.
   * @param event The name of the event to emit.
   * @param data Optional data to pass to the event handlers.
   */
  public emit(event: string, data?: any): void {
    // If no one is listening for this event, there's nothing to do.
    if (!this.events[event]) return;

    // Call every registered callback for this event, passing along the data.
    this.events[event].forEach((callback) => callback(data));
  }
}

/**
 * A singleton instance of the EventBus.
 * By exporting a single instance, we ensure that the entire application
 * shares the same event bus, allowing any component to talk to any other component.
 */
export const appEventBus = new EventBus();