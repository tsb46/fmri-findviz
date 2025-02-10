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
            slice1SliderId: 'slice1',
            slice2SliderId: 'slice2',
            slice3SliderId: 'slice3',
        };

        this.popoverShown = false;
        if (this.fmriFileType === 'gifti') {
            // remove popover for gifti
            $(`#${this.montagePopoverId}`).popover('disable');
            // disable button
            $(`#${this.montagePopoverId}`).prop('disabled', true);
        } else {
            // initialize montage options
            // get plot options
            getMontageData((montageData) => {
                this.fmriSliceLen = montageData.fmri_slice_len;
                this.initializeMontageOptions(
                    montageData.montage_slice_dir,
                    montageData.montage_slice_idx,
                );
            });
        }
    }

    /**
     * Initialize montage options
     * @param {string} montageSliceDir - The selected montage slice direction ['x', 'y', 'z']
     * @param {Object} montageSliceIndices - The montage slice indices
     */
    initializeMontageOptions(
        montageSliceDir,
        montageSliceIndices,
    ) {
        // if montage is not shown, attach listener for popover show
        if (!this.popoverShown) {
            // Event listener for when the popover is shown
            $(`#${this.montagePopoverId}`).on('shown.bs.popover', () => {
                this.popoverShown = true;
                // set selection in drop down menu
                $(`#${this.montageSliceDirSelectId}`).val(montageSliceDir);
                // loop through slider divs and set sliders with index
                this.sliceSliderIds.forEach((sliceSliderId, index) => {
                    initializeSingleSlider(
                        sliceSliderId,
                        montageSliceIndices[montageSliceDir][this.sliceSliderId2Names[sliceSliderId]],
                        [0, this.fmriSliceLen[montageSliceDir] - 1],
                        1
                    )
                    // refresh slider
                    $(`#${sliceSliderId}`).slider('refresh');
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
            this.sliceSliderIds.forEach((sliceSliderId, index) => {
                // re-initialize slider
                initializeSingleSlider(
                    sliceSliderId,
                    montageSliceIndices[montageSliceDir][this.sliceSliderId2Names[sliceSliderId]],
                    [0, this.fmriSliceLen[montageSliceDir] - 1],
                    1
                )
                // refresh slider
                $(`#${sliceSliderId}`).slider('refresh');
            });
        }
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
                sliceName = this.sliceSliderId2Names[sliceSliderId];
                sliceIdx = event.value.newValue;
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
