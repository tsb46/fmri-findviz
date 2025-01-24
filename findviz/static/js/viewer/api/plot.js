// plot.js
// API calls for modifying plot display

/**
 * Fetches colormap data from the server
 * @param {Function} callback - Callback function to handle successful response 
 * @returns {Promise} Promise object representing the API call
 */
export const getColormapData = async (callback) => {
    try {
        const response = await fetch(API_ENDPOINTS.GET_COLORMAPS, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.log(`HTTP error! status: ${response.status}, message: ${errorText}`);
            displayModalError(errorText);
            return;
        }

        const data = await response.json();
        
        // Execute callback if provided and response contains data
        if (callback && data) {
            callback(data);
        }

        return data;

    } catch (error) {
        console.error('Error fetching colormap data:', error);
        displayModalError(error.message);
        return;
    }
};

/**
 * Fetches plot options from the server
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getPlotOptions = async (callback) => {
    try {
        const response = await fetch(API_ENDPOINTS.GET_PLOT_OPTIONS, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.log(`HTTP error! status: ${response.status}, message: ${errorText}`);
            displayModalError(errorText);
            return;
        }

        const data = await response.json();
        
        // Execute callback if provided and response contains data
        if (callback && data) {
            callback(data);
        }

        return data;

    } catch (error) {
        console.error('Error fetching plot options:', error);
        displayModalError(error.message);
        return;
    }
};



/**
 * Resets color options to default values
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const resetColorOptions = async (callback) => {
    try {
        const response = await fetch(API_ENDPOINTS.RESET_COLOR_OPTIONS, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.log(`HTTP error! status: ${response.status}, message: ${errorText}`);
            displayModalError(errorText);
            return;
        }

        // Execute callback if provided
        if (callback) {
            callback();
        }

        return true;

    } catch (error) {
        console.error('Error resetting color options:', error);
        displayModalError(error.message);
        return;
    }
};


/**
 * Updates location data on the server
 * @param {Object} locationData - Location data to update
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const updateLocation = async (locationData, callback) => {
    try {
        const formData = new FormData();
        // Add location data fields to form data
        Object.keys(locationData).forEach(key => {
            formData.append(key, locationData[key]);
        });

        const response = await fetch(API_ENDPOINTS.UPDATE_LOCATION, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.log(`HTTP error! status: ${response.status}, message: ${errorText}`);
            displayModalError(errorText);
            return;
        }

        // Execute callback if provided
        if (callback) {
            callback();
        }

        return true;

    } catch (error) {
        console.error('Error updating location:', error);
        displayModalError(error.message);
        return;
    }
};

/**
 * Updates plot options on the server
 * @param {Object} plotOptions - Plot options to update
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const updatePlotOptions = async (plotOptions, callback) => {
    try {
        const formData = new FormData();
        formData.append('plot_options', plotOptions);

        const response = await fetch(API_ENDPOINTS.UPDATE_PLOT_OPTIONS, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.log(`HTTP error! status: ${response.status}, message: ${errorText}`);
            displayModalError(errorText);
            return;
        }

        // Execute callback if provided
        if (callback) {
            callback();
        }

        return true;

    } catch (error) {
        console.error('Error updating plot options:', error);
        displayModalError(error.message);
        return;
    }
};

/**
 * Updates timepoint on the server
 * @param {number} timePoint - Time point to update
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const updateTimepoint = async (timePoint, callback) => {
    try {
        const formData = new FormData();
        formData.append('time_point', timePoint);

        const response = await fetch(API_ENDPOINTS.UPDATE_TIMEPOINT, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.log(`HTTP error! status: ${response.status}, message: ${errorText}`);
            displayModalError(errorText);
            return;
        }

        // Execute callback if provided
        if (callback) {
            callback();
        }

        return true;

    } catch (error) {
        console.error('Error updating timepoint:', error);
        displayModalError(error.message);
        return;
    }
};

