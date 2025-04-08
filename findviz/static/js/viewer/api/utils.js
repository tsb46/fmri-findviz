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
 * @returns {Promise<any>} Response data or null on error
 */
export const makeRequest = async (url, options, errorConfig) => {
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
            delete options.body;
        }

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
            // Try to parse the error as JSON first
            let errorData;
            let errorText;
            
            try {
                errorData = await response.json();
                // Check if the response is a structured error
                if (typeof errorData === 'object' && errorData !== null) {
                    errorText = errorData.error || JSON.stringify(errorData);
                } else {
                    errorText = errorData;
                }
            } catch (e) {
                // If not JSON, get as text
                errorText = await response.text();
            }
            
            console.error(`${errorConfig.errorPrefix}:`, errorData || errorText);

            if (errorConfig.isInline && errorConfig.errorId) {
                displayInlineError(errorText, errorConfig.errorId);
            } else {
                // Pass structured error data to the error handler if available
                if (errorData && typeof errorData === 'object') {
                    const errorMessage = errorData.error || errorText;
                    modalErrorHandler.displayError(errorMessage);
                } else {
                    modalErrorHandler.displayError(errorText);
                }
            }
            throw new Error(errorText);
        }

        // Clear inline error if it exists
        if (errorConfig.isInline && errorConfig.errorId) {
            clearInlineError(errorConfig.errorId);
        }

        const data = await response.json();

        return data || null;
    } catch (error) {
        console.error(`${errorConfig.errorPrefix}:`, error);
        throw error; // Re-throw to be caught by the calling function
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