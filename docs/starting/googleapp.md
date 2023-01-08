# Creating a Google Developers application

This guide will run you through the process of configuring a project for analytix to use.

By the end of this guide, you will know:

1. how to set up an application on the [Google Developers Console](https://console.cloud.google.com/home)
2. how to enable the YouTube Analytics API in your application
3. how to make analytix aware of your application

## Creating a project

To create a project:

1. sign into your Google account. This does not need to be the same account as the one you are retrieving data from.
2. on the navbar, click on the dropdown that says "Select a project".
3. click "NEW PROJECT".
4. enter your project name, then click "CREATE". You do not need to set an organisation.

After this, you'll be redirected back to the dashboard. It may take some time to create the project.

## Setting up the YouTube Analytics API

### Enabling the YouTube Analytics API

1. Click on "ENABLE APIS AND SERVICES".
2. Search for "youtube", then click "YouTube Analytics API".
3. Click "ENABLE".

### Configuring the consent screen

Click "CREATE CREDENTIALS" in the top-right corner, then proceed with the following steps.

1. **Credential type**
    * Under "What data will you be accessing?", select "User data"
    * Click "NEXT".
2. **OAuth consent screen**
    * Enter the following information:
        * App name: the name of your application; this does not need to be the same as your project's name
        * User support email: this is required even though your project will remain private to you
        * App logo: an optional logo for your application
        * Developer contact information: same as User support email
    * Click "SAVE AND CONTINUE".
3. **Scopes**
    * Click "ADD OR REMOVE SCOPES".
    * Select the `.../auth/yt-analytics.readonly` and `.../auth/yt-analytics-monetary.readonly` scopes; these should be the last two in the list.
    * Click "UPDATE".
    * Click "SAVE AND CONTINUE".
4. **OAuth Client ID**
    * Select your application type. If you're not sure which option to select, choose "Desktop app".
    * Enter a name for your OAuth 2 client. This does not need to be the same as your project name.
5. **Your credentials**
    * Click "DOWNLOAD".
    * Save your secrets file in the root directory (or subdirectory thereof) of your project. It is recommended you give it an easy name to remember, such as "secrets.json".
    * Click "DONE".

!!! warning
    You should **never** share your secrets file with anyone.

### Setting yourself as a test user

In order to use your application, you need to add yourself as a test user. To do so:

1. click "OAuth consent screen"
2. under the "Test users" heading, click "+ ADD USERS"
3. type your email address into the box
4. click "SAVE"

!!! success
    You're all done! You can now start working with analytix.
