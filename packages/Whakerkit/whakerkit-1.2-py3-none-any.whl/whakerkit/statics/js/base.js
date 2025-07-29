/**
_This file is part of WhakerKit: https://whakerkit.sourceforge.io
_This file was originally part of WhintPy - by Brigitte Bigi, CNRS.
Integrated into WhakerKit as of 2025-05-23.

-------------------------------------------------------------------------


  ██╗    ██╗██╗  ██╗ █████╗ ██╗  ██╗███████╗██████╗ ██╗  ██╗██╗████████╗
  ██║    ██║██║  ██║██╔══██╗██║ ██╔╝██╔════╝██╔══██╗██║ ██╔╝██║╚══██╔══╝
  ██║ █╗ ██║███████║███████║█████╔╝ █████╗  ██████╔╝█████╔╝ ██║   ██║
  ██║███╗██║██╔══██║██╔══██║██╔═██╗ ██╔══╝  ██╔══██╗██╔═██╗ ██║   ██║
  ╚███╔███╔╝██║  ██║██║  ██║██║  ██╗███████╗██║  ██║██║  ██╗██║   ██║
   ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝   ╚═╝

  a seamless toolkit for managing dynamic websites and shared documents.

-------------------------------------------------------------------------

Copyright (C) 2024-2025 Brigitte Bigi, CNRS
Laboratoire Parole et Langage, Aix-en-Provence, France

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

This banner notice must not be removed.

**/

// --------------------------------------------------------------------------

/**
 * BaseManager class serves as a foundation for managing HTTP requests
 * and handling responses. It encapsulates common functionality for derived
 * classes, including managing a request manager instance and URI extraction
 * from the current window location.
 *
 * This class provides methods to display action results and error messages
 * in a user-friendly way, either through a <dialog> element or a browser
 * alert, facilitating consistent error handling across different components
 * that extend this base class.
 *
 * Private Members:
 *  - _requestManager: An instance of the RequestManager class responsible
 *    for managing HTTP requests.
 *  - _uri: A string representing the current URL path, extracted from the
 *    window location.
 *
 * Methods:
 *  - _showActionResult: Handles the result of an action by checking the
 *    HTTP request status and displaying appropriate messages.
 *  - #showDialog: Displays a message in a <dialog> element or falls back
 *    to a browser alert if the dialog is not available.
 *
 * Usage example:
 *  class DerivedManager extends BaseManager {
 *      ...
 *  }
 *  const manager = new DerivedManager();
 *
 */
export default class BaseManager {

    // Private members shared by all classes
    _requestManager;
    _uri;

    constructor() {
        this._requestManager = new RequestManager();
        let url = new URL(window.location.href);
        this._uri = url.pathname.substring(1);
    }

    /**
     * Displays an error or info message, and/or reloads the page.
     *
     * Handles the result of an action by checking the status of the request. If the
     * request was unsuccessful (status code not 200), an error message is displayed.
     * Otherwise, an optional info message is shown. If `reload` is set to true, the page
     * is reloaded after displaying the message.
     * The messages are displayed in a <dialog> element if available, or in an alert box otherwise.
     *
     * HTML Requirement:
     *  - A <dialog> element with id="error_dialog" to display error messages.
     *  - A <dialog> element with id="info_dialog" to display info messages.
     *
     * @param {string} [error="No details"] - The error message to display if a request fails.
     * @param {string} [info=""] - An optional info message to display upon success.
     * @param {boolean} [reload=true] - Whether to reload the page if no error occurred.
     *
     * @returns {void}
     *
     */
    _showActionResult(error = "No details", info = "", reload = true) {
        if (this._requestManager.status !== 200) {
            console.error(`HTTP error ${this._requestManager.status}: ${error}`);
            this.#showDialog('error_dialog', `Erreur ${this._requestManager.status} : ${error}`);
        } else {
            if (info) {
                console.info(info);
                this.#showDialog('info_dialog', info);
            }
            if (reload) {
                window.location.reload();
            }
        }
    }

    // ----------------------------------------------------------------------

    /**
     * Displays a message in a <dialog> element if it exists, or falls back to an alert.
     *
     * This function searches for a <dialog> element by its ID. If found, it inserts the
     * provided message inside the dialog and opens it. If the dialog is not found, it
     * displays the message using a browser alert.
     *
     * @param {string} dialogId - The ID of the <dialog> element to display the message in.
     * @param {string} message - The message to display in the dialog or alert.
     *
     * @returns {void}
     *
     */
    #showDialog = (dialogId, message) => {
        let dlg = document.getElementById(dialogId);
        if (dlg != null) {
            dlg.innerHTML = `<p>${message}</p>`;
            open_dialog(dialogId);
        } else {
            alert(message);
        }
    }

}
