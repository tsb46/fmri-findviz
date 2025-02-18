// moviePopover.js - movie play options popover

import eventBus from '../../../events/ViewerEvents.js';
import { EVENT_TYPES } from '../../../../constants/EventTypes.js';
import { initializeSingleSlider } from '../../sliders.js';
import { getFmriPlotOptions, updateFmriPlotOptions } from '../../../api/plot.js';

class MoviePopover {
    constructor(playMoviePopoverId, playMovieSpeedSliderId) {
        this.playMoviePopoverId = playMoviePopoverId;
        this.playMoviePopover = $(`#${playMoviePopoverId}`);
        this.playMovieSpeedSliderId = playMovieSpeedSliderId;

        // initialize popover
        this.initializePlayMoviePopover();
    }

    initializePlayMoviePopover() {
        this.playMoviePopover.on('shown.bs.popover', async () => {
            const plotOptions = await getFmriPlotOptions();
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

    updatePlayMovieSpeed(playMovieSpeedSlider) {
        const speed = playMovieSpeedSlider.val();
        updateFmriPlotOptions({ play_movie_speed: speed }, () => {
            eventBus.publish(EVENT_TYPES.VISUALIZATION.FMRI.PLAY_MOVIE_SPEED_CHANGE, speed);
        });
    }
}

export default MoviePopover;