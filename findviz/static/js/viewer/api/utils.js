// utils.js
import { displayInlineError, clearInlineError, modalErrorHandler } from '../error.js';

/**
 * Makes an API request with standardized error handling
 * @param {string} url - API endpoint URL
 * @param {Object} options - Request options (method, headers, body)
 * @param {Object} errorConfig - Error handling configuration
 * @param {string} [errorConfig.errorId] - ID of inline error element
 * @param {boolean} [errorConfig.isInline=false] - Whether to show error inline
 * @param {string} errorConfig.errorPrefix - Prefix for error logging
 * @param {Function} [callback] - Callback function for successful response
 * @param {Function} [errorCallback] - Callback function for error response
 * @returns {Promise<any>} Response data or true for POST requests
 */
export const makeRequest = async (url, options, errorConfig, callback, errorCallback) => {
    try {
        let finalUrl = url;

        // Handle URL parameters for GET requests
        if (options.method === 'GET' && options.body instanceof FormData) {
            const params = new URLSearchParams();
            for (const [key, value] of options.body.entries()) {
                if (value !== null) {
                    params.append(key, value);
                }
            }
            const queryString = params.toString();
            if (queryString) {
                finalUrl = `${url}?${queryString}`;
            }
            delete options.body;  // Remove body from GET request
        }

        // Don't set Content-Type for FormData - browser will set it automatically
        const headers = options.body instanceof FormData 
            ? options.headers 
            : {
                'Content-Type': 'application/json',
                ...options.headers
              };

        const response = await fetch(finalUrl, {
            ...options,
            headers
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.log(`HTTP error! status: ${response.status}, message: ${errorText}`);

            if (errorConfig.isInline && errorConfig.errorId) {
                displayInlineError(errorText, errorConfig.errorId);
            } else {
                modalErrorHandler.displayError(errorText);
            }

            // Call error callback if provided
            if (errorCallback) {
                errorCallback();
            }

            return;

        }

        // Clear inline error if it exists
        if (errorConfig.isInline && errorConfig.errorId) {
            clearInlineError(errorConfig.errorId);
        }

        // get data from response (if any)
        const data = await response.json();

        // For GET requests, parse and return data
        if (options.method === 'GET') {
            if (callback && data) {
                callback(data);
            }
            return data;
        }

        // For POST requests, if callback, execute call back and return true 
        if (callback) {
            callback(data)
            return true;
        } else {
            // if no callback, return data or true
            if (data) {
                return data;
            } else {
                return true;
            }
        }

    } catch (error) {
        console.error(`${errorConfig.errorPrefix}:`, error);
        // Call error callback if provided
        if (errorCallback) {
            errorCallback();
        }
        return;
    }
};

/**
 * Creates FormData from an object
 * @param {Object} data - Object to convert to FormData
 * @returns {FormData} FormData object
 */
export const createFormData = (data) => {
    const formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
        // Convert objects/arrays to JSON strings before appending
        formData.append(key, 
            typeof value === 'object' ? JSON.stringify(value) : value
        );
    });
    return formData;
};