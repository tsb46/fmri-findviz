// set montage box popup options
import { EVENT_TYPES } from '../constants/EventTypes.js';
import { initializeSingleSlider } from './sliders.js';
import eventBus from '../events/ViewerEvents.js';
import { getPlotOptions, updatePlotOptions } from '../api/plot.js';

/**
 * Montage class
 */
class Montage {
    /**
     * Constructor
     * @param {string} fmriFileType - The type of FMRI file
     * @param {Object} fmriSliceLen - The length of the FMRI slices
     * @param {string} montagePopoverId - The ID of the montage popover
     * @param {string} montageSliceSelectId - The ID of the montage slice select
     */
    constructor(
        fmriFileType,
        fmriSliceLen,
        montagePopoverId,
        montageSliceSelectId,
    ) {
        this.fmriFileType = fmriFileType;
        this.fmriSliceLen = fmriSliceLen;
        this.montagePopoverId = montagePopoverId;
        this.montageSliceSelectId = montageSliceSelectId;
        // define montage slice div ids
        this.sliceDivIds = ['slice1Slider', 'slice2Slider', 'slice3Slider'];

        this.popoverShown = false;
        if (this.fmriFileType === 'gifti') {
            // remove popover for gifti
            $(`#${this.montagePopoverId}`).popover('disable');
            // disable button
            $(`#${this.montagePopoverId}`).prop('disabled', true);
        } else {
            // initialize montage options
            // get plot options
            getPlotOptions((plotOptions) => {
                this.initializeMontageOptions(
                    plotOptions.montage_slice_dir,
                    plotOptions.montage_slice_idx,
                    this.fmriSliceLen
                );
            });
        }
    }

    /**
     * Initialize montage options
     * @param {string} montageSliceSelection - The selected montage slice ['x', 'y', 'z']
     * @param {Object} montageSliceIndices - The montage slice indices
     */
    initializeMontageOptions(
        montageSliceSelection,
        montageSliceIndices,
    ) {
        // if montage is not shown, attach listener for popover show
        if (!this.popoverShown) {
            // Event listener for when the popover is shown
            $(`#${this.montagePopoverId}`).on('shown.bs.popover', () => {
                this.popoverShown = true;
                // set selection in drop down menu
                $(`#${this.montageSliceSelectId}`).val(montageSliceSelection);
                // loop through slider divs and set sliders with index
                this.sliceDivIds.forEach((sliceDiv, index) => {
                    initializeSingleSlider(
                        sliceDiv,
                        montageSliceIndices[montageSliceSelection][index],
                        [0, this.fmriSliceLen[montageSliceSelection] - 1],
                        1
                    )
                });
                // Hide popover when clicking outside
                $(document).on('click', function (e) {
                    this.popoverShown = false;
                    // Check if the click is outside the popover and the button
                    if (!$(e.target).closest(`.popover, #${this.montagePopoverId}`).length) {
                      $(`#${this.montagePopoverId}`).popover('hide');
                    }
                });
                // attach montage listeners
                this.sliceSelectionListener();
                this.sliderChangeListener();
            });
        // if already shown, revise sliders
        } else {
            for (const sliceDiv in montageSliceIndices[montageSliceSelection]) {
                // re-initialize slider
                initializeSingleSlider(
                    $(`#${sliceDiv}`),
                    montageSliceIndices[montageSliceSelection][sliceDiv],
                    [0, this.fmriSliceLen[montageSliceSelection] - 1, 1],
                    1
                )
                // refresh slider
                $(`#${sliceDiv}`).slider('refresh');
            };
        }
    }

    /**
     * Handle montage slice direction change
     * @param {Event} event - event object
     */
    sliceSelectionListener() {
        // attach dropdown slice selection listener
        $(`#${this.montageSliceSelectId}`).change((event) => {
            this.handleMontageSliceDirectionChange(event);
        });
    }

    /**
     * Handle montage slice direction change
     * @param {Event} event - event object
     */
    async handleMontageSliceDirectionChange(event) {
        const plotOptions = {
            montageSliceSelection: event.target.value,
        }
        // update plot options
        await updatePlotOptions(plotOptions);
        // get plot options
        getPlotOptions((plotOptions) => {
            this.initializeMontageOptions(
                plotOptions.montage_slice_dir,
                plotOptions.montage_slice_idx,
            );
            // trigger a montage slice selection change event
            eventBus.publish(EVENT_TYPES.VISUALIZATION.MONTAGE_SLICE_DIRECTION_CHANGE, {
                sliceDirection: plotOptions.montage_slice_dir,
                sliceIndices: plotOptions.montage_slice_idx[plotOptions.montage_slice_dir]
            });
        });
    }

    /**
     * Handle slider change
     * @param {Object} montageSliceIndices - The montage slice indices
     * @param {string} montageSliceSelection - The montage slice selection
     */
    sliderChangeListener(montageSliceIndices, montageSliceSelection) {
        // Listen for slider changes and update slice index
        this.sliceDivIds.forEach((sliceDiv, index) => {
            $(`#${sliceDiv}`).on('change', (event) => {
                montageSliceIndices[montageSliceSelection][sliceDiv] = event.value.newValue;
                this.handleMontageSliceChange(montageSliceIndices, montageSliceSelection);
            });
        });
    }

    /**
     * Handle montage slice change
     * @param {Object} montageSliceIndices - The montage slice indices
     * @param {string} montageSliceSelection - The montage slice selection
     */
    async handleMontageSliceChange(montageSliceIndices, montageSliceSelection) {
        const plotOptions = {
            montage_slice_idx: montageSliceIndices,
        }
        // update plot options
        await updatePlotOptions(plotOptions);
        // trigger a montage slice change event
        eventBus.publish(EVENT_TYPES.VISUALIZATION.MONTAGE_SLICE_CHANGE, {
            sliceDirection: montageSliceSelection,
            sliceIndices: montageSliceIndices[montageSliceSelection]
        });
    }
}

export default Montage;
