// set montage box popup options
import { EVENT_TYPES } from '../../constants/EventTypes.js';
import { initializeSingleSlider } from '../sliders.js';
import eventBus from '../../events/ViewerEvents.js';
import { 
    getMontageData, 
    getViewerMetadata, 
    updateMontageSliceDir, 
    updateMontageSliceIdx 
} from '../../api/data.js';

/**
 * Montage class
 */
class Montage {
    /**
     * Constructor
     * @param {string} fmriFileType - The type of FMRI file
     * @param {string} montagePopoverId - The ID of the montage popover
     * @param {string} montageSliceDirSelectId - The ID of the montage slice direction select
     * @param {string} slice1SliderId - The ID of the first slice slider
     * @param {string} slice2SliderId - The ID of the second slice slider
     * @param {string} slice3SliderId - The ID of the third slice slider
     */
    constructor(
        fmriFileType,
        montagePopoverId,
        montageSliceDirSelectId,
        slice1SliderId,
        slice2SliderId,
        slice3SliderId,
    ) {
        // get fmri slice length from viewer metadata
        getViewerMetadata(
            (metadata) => {
                this.fmriSliceLen = metadata.slice_len;
            }
        );
        this.fmriFileType = fmriFileType;
        this.montagePopoverId = montagePopoverId;
        this.montageSliceDirSelectId = montageSliceDirSelectId;
        // define montage slice ids
        this.sliceSliderIds = [slice1SliderId, slice2SliderId, slice3SliderId];
        // define id to montage slice names converter 
        this.sliceSliderId2Names = {
            [slice1SliderId]: 'slice_1',
            [slice2SliderId]: 'slice_2',
            [slice3SliderId]: 'slice_3',
        };

        if (this.fmriFileType === 'gifti') {
            // remove popover for gifti
            $(`#${this.montagePopoverId}`).popover('disable');
            // disable button
            $(`#${this.montagePopoverId}`).prop('disabled', true);
        } else {
            // initialize montage options
            this.initializeMontageOptions()
        }
    }

    /**
     * Initialize montage options
     */
    initializeMontageOptions() {
        // Event listener for when the popover is shown
        $(`#${this.montagePopoverId}`).on('shown.bs.popover', () => {
            // get plot options
            getMontageData((montageData) => {
                const montageSliceDir = montageData.montage_slice_dir;
                const montageSliceIndices = montageData.montage_slice_idx;
                // set selection in drop down menu
                $(`#${this.montageSliceDirSelectId}`).val(montageSliceDir);
                // loop through slider divs and initialize sliders 
                this.sliceSliderIds.forEach((sliceSliderId, index) => {
                    initializeSingleSlider(
                        sliceSliderId,
                        montageSliceIndices[montageSliceDir][this.sliceSliderId2Names[sliceSliderId]][montageSliceDir],
                        [0, this.fmriSliceLen[montageSliceDir] - 1],
                        1
                    )
                    // refresh slider
                    $(`#${sliceSliderId}`).slider('refresh');
                });
                // Hide popover when clicking outside
                // Store reference to this
                const self = this;
                $(document).on('click', function (e) {
                    // Check if the click is outside the popover and the button
                    if (!$(e.target).closest(`.popover, #${self.montagePopoverId}`).length) {
                        $(`#${self.montagePopoverId}`).popover('hide');
                    }
                });
                // attach montage listeners
                this.sliceSelectionListener();
                this.sliderChangeListener();
            });
        });
    }

    /**
     * Handle montage slice direction change
     * @param {Event} event - event object
     */
    sliceSelectionListener() {
        // attach dropdown slice selection listener
        $(`#${this.montageSliceDirSelectId}`).change((event) => {
            this.handleMontageSliceDirectionChange(event);
        });
    }

    /**
     * Handle montage slice direction change
     * @param {Event} event - event object
     */
    async handleMontageSliceDirectionChange(event) {
        // update plot options
        await updateMontageSliceDir(event.target.value);
        // get plot options
        getMontageData((montageData) => {
            this.initializeMontageOptions(
                montageData.montage_slice_dir,
                montageData.montage_slice_idx,
            );
            // trigger a montage slice direction change event
            eventBus.publish(
                EVENT_TYPES.VISUALIZATION.FMRI.MONTAGE_SLICE_DIRECTION_CHANGE, 
                {
                    sliceDirection: event.target.value,
                }
            );
        });
    }

    /**
     * Handle slider change
     */
    sliderChangeListener() {
        // Listen for slider changes and update slice index
        this.sliceSliderIds.forEach((sliceSliderId, index) => {
            $(`#${sliceSliderId}`).on('change', (event) => {
                const sliceName = this.sliceSliderId2Names[sliceSliderId];
                const sliceIdx = event.value.newValue;
                this.handleMontageSliceChange(sliceName, sliceIdx);
            });
        });
    }

    /**
     * Handle montage slice change
     * @param {string} sliceName - The name of the slice
     * @param {number} sliceIdx - The index of the slice
     */
    async handleMontageSliceChange(sliceName, sliceIdx) {
        const montageSliceParams = {
            slice_name: sliceName,
            slice_idx: sliceIdx,
        }
        // update plot options
        updateMontageSliceIdx(montageSliceParams, () => {
            // trigger a montage slice change event
            eventBus.publish(
                EVENT_TYPES.VISUALIZATION.FMRI.MONTAGE_SLICE_CHANGE, 
                {
                    slice_name: sliceName,
                    slice_idx: sliceIdx
                }
            );
        });
    }
}

export default Montage;
