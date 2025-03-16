// TaskDesignFileManager.js
// Manages the task design file DOM elements

class TaskDesignFileManager {
    /**
     * @param {string} taskDesignFileId - The ID of the task design file input
     * @param {string} taskDesignTRId - The ID of the task design TR input
     * @param {string} taskDesignSliceTimeId - The ID of the task design slice time input
     */
    constructor(
        taskDesignFileId,
        taskDesignTRId,
        taskDesignSliceTimeId
    ) {
        this.taskDesignFileId = taskDesignFileId;
        this.taskDesignTRId = taskDesignTRId;
        this.taskDesignSliceTimeId = taskDesignSliceTimeId;
    }

    /**
     * Get task design files
     * @returns {object} - The task design files
     */
    getFiles() {
        return {
            task_file: document.getElementById(this.taskDesignFileId).files[0],
            tr: document.getElementById(this.taskDesignTRId).value,
            slicetime_ref: document.getElementById(this.taskDesignSliceTimeId).value,
        };
    }
}

export default TaskDesignFileManager;

