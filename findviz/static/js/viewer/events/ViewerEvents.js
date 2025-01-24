// ViewerEvents.js - central event management class for viewer interactions

// Create a single instance
const eventBus = new ViewerEvents();

/**
 * Central event management class for viewer interactions
 */
class ViewerEvents {
    constructor() {
        this.eventSubscriptions = new Map();
    }

    /**
     * Subscribe to specific event types
     * @param {string} eventType - Type of event to subscribe to
     * @param {Function} callback - Callback function to execute
     * @returns {Symbol} Subscription ID
     */
    subscribe(eventType, callback) {
        const id = Symbol();
        if (!this.eventSubscriptions.has(eventType)) {
            this.eventSubscriptions.set(eventType, new Map());
        }
        this.eventSubscriptions.get(eventType).set(id, callback);
        return id;
    }

    /**
     * Emit event to all subscribers
     * @param {string} eventType - Type of event to emit
     * @param {any} data - Event data
     */
    publish(eventType, data) {
        const subscribers = this.eventSubscriptions.get(eventType);
        if (subscribers) {
            subscribers.forEach(callback => callback(data));
        }
    }
    /**
     * Unsubscribe from a specific subscription
     * @param {string} eventType - Type of event to unsubscribe from
     * @param {Symbol} subscriptionId - ID of subscription to remove
     * @returns {boolean} Whether unsubscribe was successful
     */
    unsubscribe(eventType, subscriptionId) {
        const subscribers = this.eventSubscriptions.get(eventType);
        if (subscribers) {
            return subscribers.delete(subscriptionId);
        }
        return false;
    }
    /**
     * Clean up event listeners
     */
    destroy() {
        this.eventSubscriptions.clear();
    }
}

export default eventBus;