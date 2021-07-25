Migrating to version 2
######################

This section will detail what changes you need to make to convert a project from using version 1 to version 2. Here are the things to keep in mind:

- analytix now supports Python 3.6.
- The number of dependencies has been reduced from 27 to 7. pandas is now an optional dependency, and so will need to be installed separately if you want it (you can use :code:`pip install "analytix[opt]"` to achieve the same effect).
- The :class:`YouTubeService` class has been merged into the :class:`YouTubeAnalytics` class. Both authentication and retrieval are done through this new superclass.
- The :class:`YouTubeAnalytics` class no longer needs to be manually authorised, though you can still do this if you want. This allows for verification to take place before needing to authorise.
- Code authorisation is now the only authorisation method available.
- The token returned by the YouTube Analytics API is now stored locally for future use. This token only lasts for an hour, but means you no longer need to authorise the client every time you restart the program. If you don't want analytix to store the token, you will need to manually authorise the client, making sure to pass :code:`store_token=False` to the authorisation method.
- You are now required to pass a start date when retrieving reports.
- You can no longer disable report verification.
- Many verification entities (such as report type classes) now exist in different files. If you imported any of these features for whatever reason, you will need to check your import paths.
- Any errors that previously raised :class:`Deprecated` now return :class:`InvalidRequest`.
- Uncaught API errors now raise analytix's :class:`HTTPError` rather than google-api-python-client's :class:`HttpError`.
- The :class:`NoAuthorisedService`, :class:`ServiceAlreadyExists`, and :class:`IncompleteRequest` errors now no longer exist.
- You now need to access the number of rows and colums in a report via the :code:`shape` property rather than the :code:`nrows` and :code:`ncolumns` attributes respectively.
- The :code:`type` attribute in the report class is now the friendly name of the report type rather than the instance itself.
- When converting to a DataFrame, the "day" and "month" columns are now automatically converted to the datetime64[ns] dtype.

This is not an exhaustive list of the changes and additions in version 2, but should provide an idea of what you need to change in your project. With that being said, a number of issues present in version 1 have been fixed in version 2. If you have been having problems with retrieving certain types of reports, it is recommended you migrate to version 2 and try again.
