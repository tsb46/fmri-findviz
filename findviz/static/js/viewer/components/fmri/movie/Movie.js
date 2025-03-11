// Movie component
import { EVENT_TYPES } from '../../../../constants/EventTypes.js';
import ContextManager from '../../../api/ContextManager.js';

/**
 * Movie class for handling fMRI time point animation
 */
class Movie {
    /**
     * Create a Movie instance
     * @param {string} timeSliderId - Time slider element
     * @param {string} playMovieButtonId - Play movie button
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(timeSliderId, playMovieButtonId, eventBus, contextManager) {
        this.timeSlider = $(`#${timeSliderId}`);
        this.playMovieButton = $(`#${playMovieButtonId}`);
        this.playMovieButtonIcon = this.playMovieButton.find('i');
        this.isPlaying = false;
        this.intervalId = null;
        this.eventBus = eventBus;
        this.contextManager = contextManager;

        // get interval time from state
        this.getIntervalTime();

        // Bind event handlers
        this.playMovieButton.on('click', () => this.togglePlay());

        // Subscribe to play speed change events
        this.eventBus.subscribe(EVENT_TYPES.VISUALIZATION.FMRI.PLAY_MOVIE_SPEED_CHANGE, (newSpeed) => {
            this.setIntervalTime(newSpeed);
        });
    }

    async getIntervalTime() {
        const plotOptions = await this.contextManager.plot.getFmriPlotOptions();
        this.intervalTime = plotOptions.play_movie_speed;
    }

    /**
     * Toggle between play and pause states
     */
    togglePlay() {
        if (this.isPlaying) {
            console.log('stopping movie');
            this.stop();
        } else {
            console.log('starting movie');
            this.start();
        }
    }

    /**
     * Start playing the movie
     */
    start() {
        this.isPlaying = true;
        this.playMovieButtonIcon.removeClass('fa-play').addClass('fa-stop');

        this.intervalId = setInterval(() => {
            let currentValue = this.timeSlider.slider('getValue');
            let maxValue = this.timeSlider.slider('getAttribute', 'max');

            if (currentValue < maxValue) {
                this.timeSlider.slider('setValue', currentValue + 1);
                this.timeSlider.trigger('change');
            } else {
                this.stop();
            }
        }, this.intervalTime);
    }

    /**
     * Stop playing the movie
     */
    stop() {
        clearInterval(this.intervalId);
        this.isPlaying = false;
        this.playMovieButtonIcon.removeClass('fa-stop').addClass('fa-play');
    }

    /**
     * Get current playing state
     * @returns {boolean} Whether the movie is currently playing
     */
    getIsPlaying() {
        return this.isPlaying;
    }

    /**
     * Set new interval time
     * @param {number} newIntervalTime - New interval time in milliseconds
     */
    setIntervalTime(newIntervalTime) {
        this.intervalTime = newIntervalTime;
        if (this.isPlaying) {
            clearInterval(this.intervalId);  // Clear the existing interval
            this.start();  // Restart with new interval time
        }
    }

    /**
     * Clean up resources
     */
    destroy() {
        this.stop();
        this.playMovieButton.off('click');
    }
}

export default Movie;