// colormap.js - Colormap dropdown creation
import { getColormapData } from '../api/plot.js';
import ContextManager from '../api/ContextManager.js';

class ColorMap {
    /**
     * Constructor for ColorMap class
     * 
     * @param {string} colormapContainerId - ID of the colormap container
     * @param {string} colormapDropdownMenuId - ID of the colormap dropdown menu
     * @param {string} colormapDropdownToggleId - ID of the colormap dropdown toggle
     * @param {Function} getPlotOptions - Function to get plot options
     * @param {Function} updatePlotOptions - Function to update plot options
     * @param {ViewerEvents} eventBus - The event bus
     * @param {ContextManager} contextManager - The context manager
     */
    constructor(
        colormapContainerId,
        colormapDropdownMenuId,
        colormapDropdownToggleId,
        getPlotOptions,
        updatePlotOptions,
        changeColorMapEvent,
        eventBus,
        contextManager
    ) {
        this.colormapContainerId = colormapContainerId;
        this.colormapDropdownMenuId = colormapDropdownMenuId;
        this.colormapDropdownToggleId = colormapDropdownToggleId;
        this.getPlotOptions = getPlotOptions;
        this.updatePlotOptions = updatePlotOptions;
        this.changeColorMapEvent = changeColorMapEvent;
        this.eventBus = eventBus;
        this.contextManager = contextManager;

        // initialize color map menu
        this.initializeColorMapMenu();
    }

    /**
     * Initialize color map menu
     */
    async initializeColorMapMenu() {
        // get plot options
        const plotOptions = await this.getPlotOptions();
        const colormapData = await getColormapData();
        // create colormap dropdown
        this.createColormapDropdown(colormapData, plotOptions.color_map);
        // toggle colormap dropdown
        this.colorMapDropdownToggle();
        // close colormap dropdown
        this.colorMapDropdownClose();
        // attach colormap change listener
        this.colorMapChangeListener();
    }

    /**
     * Create colormap dropdown
     * 
     * @param {Object} colormapData - Colormap data
     * @param {string} colorMapSelect - Select element for the colormap dropdown
     * @returns {HTMLElement} - Container for the colormap dropdown
     */
    createColormapDropdown(
        colormapData,
        colorMapSelect
    ) {
        console.log('creating colormap dropdown');
        // get colormap container
        const colormapContainer = document.getElementById(this.colormapContainerId);
        // Dynamically generate the colormap options
        let colormapOptions = Object.keys(colormapData).map(cmap => `
            <li data-value="${cmap}" style="display: flex; justify-content: space-between; align-items: center;">
                <span style="flex: 1; min-width: 70px;">${colormapData[cmap].label}</span>
                <span class="colormap-swatch" style="background: ${colormapData[cmap].gradient};"></span>
            </li>`
        ).join('');

        // Clear any existing content
        colormapContainer.innerHTML = '';

        // Generate dropdown
        colormapContainer.innerHTML = `
            <div id="${this.colormapDropdownToggleId}" class="dropdown-toggle" style="color:black;">${colorMapSelect}</div>
            <ul id="${this.colormapDropdownMenuId}" class="dropdown-menu">
                ${colormapOptions}
            </ul>
        `;

        // return the container
        return colormapContainer;
    }

    /**
    * Toggle colormap dropdown
    */
    colorMapDropdownToggle() {
        const dropdownToggle = document.getElementById(this.colormapDropdownToggleId);
        const dropdownMenu = document.getElementById(this.colormapDropdownMenuId);
        dropdownToggle.addEventListener('click', (event) => {
            dropdownMenu.classList.toggle('show');
            event.stopPropagation();
        });
    }

    /**
    * Close colormap dropdown
    */
    colorMapDropdownClose() {
        const dropdownToggle = document.getElementById(this.colormapDropdownToggleId);
        const dropdownMenu = document.getElementById(this.colormapDropdownMenuId);

        // Close dropdown on outside click
        document.addEventListener('click', (event) => {
            if (!dropdownMenu.contains(event.target) && !dropdownToggle.contains(event.target)) {
                dropdownMenu.classList.remove('show');
            }
        });
    }

    /**
     * Attach colormap dropdown event listeners
     */
    colorMapChangeListener() {
        const dropdownToggle = document.getElementById(this.colormapDropdownToggleId);
        const dropdownMenu = document.getElementById(this.colormapDropdownMenuId);

        // Handle item selection
        dropdownMenu.addEventListener('click', (event) => {
            console.log('colormap dropdown item clicked');
            if (event.target.tagName === 'LI' || event.target.parentElement.tagName === 'LI') {
                const selectedValue = event.target.closest('li').getAttribute('data-value');
                dropdownToggle.textContent = event.target.closest('li').querySelector('span:first-child').textContent;
                dropdownMenu.classList.remove('show');
                this.handleColorMapChange(selectedValue);
            }
        });
    }

    async handleColorMapChange(colormap) {
        console.log('handling color map change');
        // update the plot options
        await this.updatePlotOptions({ color_map: colormap });
        // trigger color map change event
        this.eventBus.publish(
            this.changeColorMapEvent,
            {
                colormap: colormap
            }
        );
    }

}

export default ColorMap;



