// data.js 
// API calls for pulling fmri and time course data

import { displayModalError } from '../error';
/**
 * Fetches FMRI data from the server
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getFMRIData = async (callback) => {
    try {
        const response = await fetch(API_ENDPOINTS.GET_FMRI_DATA, {
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
        console.error('Error fetching FMRI data:', error);
        displayModalError(error.message);
        return;
    }
};

/**
 * Fetches functional timecourse data from the server
 * @param {Function} callback - Callback function to handle successful response
 * @returns {Promise} Promise object representing the API call
 */
export const getFunctionalTimecourse = async (callback) => {
    try {
        const response = await fetch(API_ENDPOINTS.GET_FUNCTIONAL_TIMECOURSE, {
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
        console.error('Error fetching functional timecourse:', error);
        displayModalError(error.message);
        return;
    }
};

