Creating a Google application
#############################

This guide will run you through the process of configuring a project for analytix to use.

By the end of this guide, you will know:

#. How to set up an application on the Google Developers Console
#. How to enable the YouTube Analytics API in your application
#. How to make analytix aware of your application

Creating a project
==================

To create a project:

#. Sign into your Google account. This does not need to be the same account as the one you are retrieving data from.
#. On the navbar, click on the dropdown that says "Select a project".
#. Click on "NEW PROJECT".
#. Enter your project name, then click "CREATE". You do not need to set an organisation.

After this, you'll be redirected back to the dashboard. It may take some time to create the project.

Setting up the YouTube Analytics API
====================================

Enabling the YouTube Analytics API
----------------------------------

#. Click on "ENABLE APIS AND SERVICES".
#. Search for "youtube", then click "YouTube Analytics API".
#. Click "ENABLE".

Configuring the consent screen
------------------------------

#. Click "Credentials" on the side bar.
#. Click "CONFIGURE CONSENT SCREEN".
#. Select "External" from the options, then click "CREATE".
#. Enter the following information:
    #. App name: The name of your application. This does not need to be the same as your project's name.
    #. User support email: This is required even though your project will remain private to you.
    #. Developer contact information: Same as User support email.
#. Click "SAVE AND CONTINUE" -- no other information is necessary.
#. Click "ADD OR REMOVE SCOPES".
#. Select the final two, then click "UPDATE":
    #. .../auth/yt-analytics.readonly
    #. .../auth/yt-analytics-monetary.readonly
#. Click "SAVE AND CONTINUE".
#. Click "ADD USERS".
#. Enter the email address associated with your YouTube channel, then click "ADD". If there are multiple, you only need to enter one.
#. Click "SAVE AND CONTINUE".
#. Click "BACK TO DASHBOARD".

Creating an OAuth Client ID
---------------------------

#. Click "Credentials" on the side bar.
#. Click "CREATE CREDENTIALS".
#. Click "OAuth client ID".
#. In the dropdown, select "Desktop app", and give this a name. Your project's name will be fine.
#. Click "OK".
#. Click the download button to download your secrets file.
#. Save this file with an easy to remember name ("secrets.json" is good) where your project can access it.

.. warning::

    You should **never** share this secrets file with anyone.

Conclusion
==========

You're all done! You can now start working with analytix.
