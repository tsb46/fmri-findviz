// utils.js
import { displayInlineError, displayModalError, clearInlineError } from '../error.js';

/**
 * Makes an API request with standardized error handling
 * @param {string} url - API endpoint URL
 * @param {Object} options - Request options (method, headers, body)
 * @param {Object} errorConfig - Error handling configuration
 * @param {string} [errorConfig.errorId] - ID of inline error element
 * @param {boolean} [errorConfig.isInline=false] - Whether to show error inline
 * @param {string} errorConfig.errorPrefix - Prefix for error logging
 * @param {Function} [callback] - Callback function for successful response
 * @returns {Promise<any>} Response data or true for POST requests
 */
export const makeRequest = async (url, options, errorConfig, callback) => {
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
                displayModalError(errorText);
            }
            return;
        }

        // Clear inline error if it exists
        if (errorConfig.isInline && errorConfig.errorId) {
            clearInlineError(errorConfig.errorId);
        }

        // For GET requests, parse and return data
        if (options.method === 'GET') {
            const data = await response.json();
            if (callback && data) {
                callback(data);
            }
            return data;
        }

        // For POST requests, execute callback and return true
        if (callback) {
            callback();
        }
        return true;

    } catch (error) {
        console.error(`${errorConfig.errorPrefix}:`, error);
        // always display modal for catch-all error
        displayModalError(error.message);
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