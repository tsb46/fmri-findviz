// TR Form Listener
// Synchronizes TR inputs across different inputs

class TRFormListener {
    /**
     * @param {string} taskDesignTRInputId - The ID of the task design TR input
     * @param {string} fmriPreprocessingTRInputId - The ID of the fmri preprocessing TR input
     * @param {string} timeSeriesTRInputId - The ID of the time series TR input
     * @param {string} trConvertInputId - The ID of the tr convert input
     */
    constructor(
        taskDesignTRInputId,
        fmriPreprocessingTRInputId,
        timeSeriesTRInputId,
        trConvertInputId
    ) {
        this.taskDesignTRInput = document.getElementById(taskDesignTRInputId);
        this.fmriPreprocessingTRInput = document.getElementById(fmriPreprocessingTRInputId);
        this.timeSeriesTRInput = document.getElementById(timeSeriesTRInputId);
        this.trConvertInput = document.getElementById(trConvertInputId);
    }

    /**
     * Synchronizes TR inputs across different inputs
     */
    synchronize() {
        // synchronize TR inputs
        this.synchronizeTRInputs(
            this.taskDesignTRInput,
            [
                this.fmriPreprocessingTRInput, 
                this.timeSeriesTRInput,
                this.trConvertInput
            ]
        );
        this.synchronizeTRInputs(
            this.fmriPreprocessingTRInput,
            [
                this.taskDesignTRInput,
                this.timeSeriesTRInput,
                this.trConvertInput
            ]
        );
        this.synchronizeTRInputs(
            this.timeSeriesTRInput,
            [
                this.taskDesignTRInput,
                this.fmriPreprocessingTRInput,
                this.trConvertInput
            ]
        );
        this.synchronizeTRInputs(
            this.trConvertInput,
            [
                this.taskDesignTRInput, 
                this.fmriPreprocessingTRInput, 
                this.timeSeriesTRInput
            ]
        );
    }
    /**
     * Synchronizes the value of the source input with the target inputs
     * @param {HTMLInputElement} sourceInput - The source input to synchronize
     * @param {HTMLInputElement[]} targetInputs - The target inputs to synchronize
     */
    synchronizeTRInputs(sourceInput, targetInputs) {
        sourceInput.addEventListener('input', function() {
            targetInputs.forEach(input => {
                input.value = sourceInput.value;
            });
        });
    }
}

export default TRFormListener;