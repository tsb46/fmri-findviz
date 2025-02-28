/**
 * Manages Plotly trace indices for time courses in a plot
 */
class TraceManager {
    /**
     * @param {Object} options - Configuration options
     * @param {number} [options.startIndex=0] - Starting index for traces (e.g., 1 if dummy data at index 0)
     */
    constructor(options = {}) {
        // Map of time course label to trace index
        this.traceIndices = new Map();
        // Set starting index (default to 0 if not specified)
        this.startIndex = options.startIndex || 0;
        // Initialize nextIndex to startIndex
        this.nextIndex = this.startIndex;
    }

    /**
     * Add a new time course trace and return its index
     * @param {string} label - Label of the time course
     * @returns {number} Index assigned to the trace
     * @throws {Error} If label already exists
     */
    addTrace(label) {
        // check if trace already exists
        if (this.traceIndices.has(label)) {
            console.warn(`Time course ${label} already exists - replacing existing trace`);
        }
        // get index for new trace
        const index = this.nextIndex;
        // add trace to map
        this.traceIndices.set(label, index);
        // increment next index
        this.nextIndex++;
        // return index for new trace
        return index;
    }

   /**
     * Remove a time course trace and update indices
     * @param {string} label - Label of the time course to remove
     * @returns {Object} Object containing removed index and map of traces that need updating
     * @throws {Error} If label doesn't exist
     */
    removeTrace(label) {
        if (!this.traceIndices.has(label)) {
            throw new Error(`Time course ${label} does not exist`);
        }

        // get index of trace to remove
        const removedIndex = this.traceIndices.get(label);
        // delete trace from map
        this.traceIndices.delete(label);

        // Create map of traces that need their indices updated
        const tracesToUpdate = new Map();
        for (const [traceLabel, index] of this.traceIndices) {
            if (index > removedIndex) {
                // Shift indices down by 1 for all traces after the removed one
                this.traceIndices.set(traceLabel, index - 1);
                tracesToUpdate.set(traceLabel, index - 1);
            }
        }

        this.nextIndex--;
        return {
            removedIndex,
            tracesToUpdate
        };
    }

    /**
     * Get the index of a time course trace
     * @param {string} label - Label of the time course
     * @returns {number} Index of the trace
     * @throws {Error} If label doesn't exist
     */
    getTraceIndex(label) {
        if (!this.traceIndices.has(label)) {
            throw new Error(`Time course ${label} does not exist`);
        }
        return this.traceIndices.get(label);
    }

    /**
     * Check if a time course trace exists
     * @param {string} label - Label of the time course
     * @returns {boolean} True if trace exists, false otherwise
     */
    hasTrace(label) {
        return this.traceIndices.has(label);
    }

    /**
     * Get all trace labels and their indices
     * @returns {Map} Map of labels to indices
     */
    getAllTraces() {
        return new Map(this.traceIndices);
    }

    /**
     * Clear all traces
     */
    clear() {
        this.traceIndices.clear();
        this.nextIndex = this.startIndex;
    }

    /**
     * Get number of traces
     * @returns {number} Number of traces
     */
    size() {
        return this.traceIndices.size;
    }
}

export default TraceManager;