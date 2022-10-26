# Creating a Google Developers application

!!! warning
    This page is outdated and is due for a rewrite.

This guide will run you through the process of configuring a project for analytix to use.

By the end of this guide, you will know:

1. How to set up an application on the [Google Developers Console](https://console.cloud.google.com/home)
2. How to enable the YouTube Analytics API in your application
3. How to make analytix aware of your application

## Creating a project

To create a project:

1. Sign into your Google account. This does not need to be the same account as the one you are retrieving data from.
2. On the navbar, click on the dropdown that says "Select a project".
3. Click on "NEW PROJECT".
4. Enter your project name, then click "CREATE". You do not need to set an organisation.

After this, you'll be redirected back to the dashboard. It may take some time to create the project.

## Setting up the YouTube Analytics API

### Enabling the YouTube Analytics API

1. Click on "ENABLE APIS AND SERVICES".
2. Search for "youtube", then click "YouTube Analytics API".
3. Click "ENABLE".

### Configuring the consent screen

1. Click "Credentials" on the side bar.
2. Click "CONFIGURE CONSENT SCREEN".
3. Select "External" from the options, then click "CREATE".
4. Enter the following information:
    * App name: The name of your application. This does not need to be the same as your project's name.
    * User support email: This is required even though your project will remain private to you.
    * Developer contact information: Same as User support email.
5. Click "SAVE AND CONTINUE" — no other information is necessary.
6. Click "ADD OR REMOVE SCOPES".
7. Select the final two, then click "UPDATE":
    * .../auth/yt-analytics.readonly
    * .../auth/yt-analytics-monetary.readonly
8. Click "SAVE AND CONTINUE".
9. Click "ADD USERS".
10. Enter the email address associated with your YouTube channel, then click "ADD". If there are multiple, you only need to enter one.
11. Click "SAVE AND CONTINUE".
12. Click "BACK TO DASHBOARD".

## Creating an OAuth client ID

1. Click "Credentials" on the side bar.
2. Click "CREATE CREDENTIALS".
3. Click "OAuth client ID".
4. In the dropdown, select "Desktop app", and give this a name. Your project's name will be fine.
5. Click "OK".
6. Click the download button to download your secrets file.
7. Save this file with an easy to remember name ("secrets.json" is good) where your project can access it.

!!! warning
    You should **never** share this secrets file with anyone.

!!! success
    You're all done! You can now start working with analytix.
