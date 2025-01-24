// Timecourse plot

class TimeCourse {
    /**
     * Constructor for TimeCourse
     * @param {number} timeLength - The length of the time course
     * @param {string} timeCourseContainerId - The ID of the time course container
     * @param {string} colorDropdownId - The ID of the color dropdown
     * @param {boolean} timeCourseInput - Whether the time course input is provided
     * @param {boolean} taskDesignInput - Whether the task design input is provided
     */
    constructor(
        timeLength,
        timeCourseContainerId,
        colorDropdownId,
        timeCourseInput,
        taskDesignInput
    ) {
        this.timeLength = timeLength;
        this.timeCourseContainer = $(`#${timeCourseContainerId}`);
        this.timeCourseInput = timeCourseInput;
        this.taskDesignInput = taskDesignInput;
        this.colorDropdown = $(`#${colorDropdownId}`);
        if (this.timeCourseInput || this.taskDesignInput) {
            this.timeCourseContainer.css("visibility", "visible");
        }
        
    }


}