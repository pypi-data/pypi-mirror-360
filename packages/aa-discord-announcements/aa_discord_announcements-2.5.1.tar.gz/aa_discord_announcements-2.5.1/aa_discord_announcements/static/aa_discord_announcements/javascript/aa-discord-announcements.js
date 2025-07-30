/* global ClipboardJS, discordAnnouncementsSettings, discordAnnouncementsTranslations */

$(document).ready(() => {
    'use strict';

    /* Variables
    --------------------------------------------------------------------------------- */
    // Selects
    const selectAnnouncementTarget = $('select#id_announcement_target');
    const selectAnnouncementChannel = $('select#id_announcement_channel');

    // Input fields
    const inputCsrfMiddlewareToken = $('input[name="csrfmiddlewaretoken"]');
    const inputAnnouncementText = $('textarea[name="announcement_text"]');

    // Form
    const announcementForm = $('#aa-discord-announcements-form');

    /* Functions
    --------------------------------------------------------------------------------- */
    /**
     * Get data from a given ajax URL
     *
     * @param {string} url The URL to query
     * @returns {Promise<string>}
     */
    const getDataFromAjaxUrl = async (url) => {
        const response = await fetch(url);

        if (!response.ok) {
            const message = `Error ${response.status}: ${response.statusText}`;

            throw new Error(message);
        }

        return await response.text();
    };

    /**
     * Get the additional Discord ping targets for the current user
     */
    const getAnnouncementTargetsForCurrentUser = () => {
        getDataFromAjaxUrl(discordAnnouncementsSettings.url.getAnnouncementTargets).then((announcementTargets) => {
            if (announcementTargets !== '') {
                $(selectAnnouncementTarget).html(announcementTargets);
            }
        }).catch((error) => {
            console.error('Error fetching announcement targets:', error);
        });
    };

    /**
     * Get webhooks for current user
     */
    const getWebhooksForCurrentUser = () => {
        getDataFromAjaxUrl(discordAnnouncementsSettings.url.getAnnouncementWebhooks).then((announcementWebhooks) => {
            if (announcementWebhooks !== '') {
                $(selectAnnouncementChannel).html(announcementWebhooks);
            }
        }).catch((error) => {
            console.error('Error fetching announcement webhooks:', error);
        });
    };

    /**
     * Closing the message
     *
     * @param {string} element
     * @param {int} closeAfter Close Message after given time in seconds (Default: 10)
     */
    const closeMessageElement = (element, closeAfter = 10) => {
        $(element).fadeTo(closeAfter * 1000, 500).slideUp(500, () => {
            $(element).remove();
        });
    };

    /**
     * Show a success message box
     *
     * @param {string} message
     * @param {string} element
     */
    const showSuccess = (message, element) => {
        $(element).html(
            `<div class="alert alert-success alert-dismissible alert-message-success d-flex align-items-center fade show">${message}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>`
        );

        closeMessageElement('.alert-message-success');
    };

    /**
     * Show an error message box
     *
     * @param {string} message
     * @param {string} element
     */
    const showError = (message, element) => {
        $(element).html(
            `<div class="alert alert-danger alert-dismissible alert-message-error d-flex align-items-center fade show">${message}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>`
        );

        closeMessageElement('.alert-message-error', 9999);
    };

    /**
     * Copy the fleet ping to clipboard
     */
    const copyAnnouncementText = () => {
        /**
         * Copy text to clipboard
         *
         * @type Clipboard
         */
        const clipboardFleetPingData = new ClipboardJS('button#copyDiscordAnnouncement');

        /**
         * Copy success
         *
         * @param {type} e
         */
        clipboardFleetPingData.on('success', (e) => {
            showSuccess(
                discordAnnouncementsTranslations.copyToClipboard.success,
                '.aa-discord-announcements-announcement-copyresult'
            );

            e.clearSelection();
            clipboardFleetPingData.destroy();
        });

        /**
         * Copy error
         */
        clipboardFleetPingData.on('error', () => {
            showError(
                discordAnnouncementsTranslations.copyToClipboard.error,
                '.aa-discord-announcements-announcement-copyresult'
            );

            clipboardFleetPingData.destroy();
        });
    };

    /* Events
    --------------------------------------------------------------------------------- */
    /**
     * Generate announcement text
     */
    announcementForm.submit((event) => {
        // Stop the browser from sending the form, we take care of it
        event.preventDefault();

        // Close all possible form messages
        $('.aa-discord-announcements-form-message div').remove();

        // Check for mandatory fields
        const announcementFormMandatoryFields = [
            inputAnnouncementText.val()
        ];

        if (announcementFormMandatoryFields.includes('')) {
            showError(
                discordAnnouncementsTranslations.error.missingFields,
                '.aa-discord-announcements-form-message'
            );

            return false;
        }

        // Get the form data
        const formData = announcementForm.serializeArray().reduce((obj, item) => {
            obj[item.name] = item.value;

            return obj;
        }, {});

        // Fetch API call to create the announcement
        fetch(discordAnnouncementsSettings.url.createAnnouncement, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': inputCsrfMiddlewareToken.val()
            },
            body: JSON.stringify(formData)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success === true) {
                    $('.aa-discord-announcements-no-announcement').hide('fast');
                    $('.aa-discord-announcements-announcement').show('fast');

                    $('.aa-discord-announcements-announcement-text')
                        .html(data.announcement_context);

                    if (data.message) {
                        showSuccess(
                            data.message,
                            '.aa-discord-announcements-form-message'
                        );
                    }
                } else {
                    if (data.message) {
                        showError(
                            data.message,
                            '.aa-discord-announcements-form-message'
                        );
                    } else {
                        showError(
                            'Something went wrong, no details given.',
                            '.aa-discord-announcements-form-message'
                        );
                    }
                }
            })
            .catch(() => {
                showError(
                    'Something went wrong, no details given.',
                    '.aa-discord-announcements-form-message'
                );
            });
    });

    /**
     * Copy ping text
     */
    $('button#copyDiscordAnnouncement').on('click', () => {
        copyAnnouncementText();
    });

    /**
     * Initialize functions that need to start on load
     */
    (() => {
        getAnnouncementTargetsForCurrentUser();
        getWebhooksForCurrentUser();
    })();
});
