// moviePopover.js - movie play options popover

import { EVENT_TYPES } from '../../../../constants/EventTypes.js';
import { initializeSingleSlider } from '../../sliders.js';
import ContextManager from '../../../api/ContextManager.js';


class MoviePopover {
    /**
     * @param {string} playMoviePopoverId - The id of the play movie popover
     * @param {string} playMovieSpeedSliderId - The id of the play movie speed slider
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(playMoviePopoverId, playMovieSpeedSliderId, eventBus, contextManager) {
        this.playMoviePopoverId = playMoviePopoverId;
        this.playMoviePopover = $(`#${playMoviePopoverId}`);
        this.playMovieSpeedSliderId = playMovieSpeedSliderId;
        this.eventBus = eventBus;
        this.contextManager = contextManager;

        // initialize popover
        this.initializePlayMoviePopover();
    }

    initializePlayMoviePopover() {
        this.playMoviePopover.on('shown.bs.popover', async () => {
            const plotOptions = await this.contextManager.plot.getFmriPlotOptions();
            const playMovieSpeed = plotOptions.play_movie_speed;

            // initialize play movie speed slider
            initializeSingleSlider(
                this.playMovieSpeedSliderId, 
                playMovieSpeed, 
                [50, 1000], 
                50
            );
            // Hide popover when clicking outside
            // Store reference to this
            const self = this;
            $(document).on('click', function (e) {
                // Check if the click is outside the popover and the button
                if (!$(e.target).closest(`.popover, #${self.playMoviePopoverId}`).length) {
                    $(`#${self.playMoviePopoverId}`).popover('hide');
                }
            });

            // attach play movie speed slider listener
            const playMovieSpeedSlider = $(`#${this.playMovieSpeedSliderId}`);

            playMovieSpeedSlider.on('change', () => this.updatePlayMovieSpeed(playMovieSpeedSlider));
        });
    }

    async updatePlayMovieSpeed(playMovieSpeedSlider) {
        const speed = playMovieSpeedSlider.val();
        await this.contextManager.plot.updateFmriPlotOptions({ play_movie_speed: speed });
        this.eventBus.publish(EVENT_TYPES.VISUALIZATION.FMRI.PLAY_MOVIE_SPEED_CHANGE, speed);
    }
}

export default MoviePopover;