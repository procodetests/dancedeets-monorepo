# DanceDeets

The code for www.dancedeets.com and the DanceDeets mobile app.

## Code layout

- [`server/`](server): AppEngine server codebase (contains FE JS code, Python GAE app, and other miscellaneous).
- [`mobile/`](mobile): React Native app (including JS code).
- [`common/`](common)`: Common functions and data models used by both `server/` and `mobile/`. As well as data shared by both (ie all the tutorial data)
- [`bybase/`](bybase): Some half-finished scripts, just poking around at the data bybase was using
- [`scripts/`](scripts): Some scripts that might apply to things outside of just a server or mobile context
- [`dataflow/`](dataflow): The Google Cloud Dataflow (aka Apache Beam) code. Basically where the new MapReduce type jobs are being written, as we try to migrate off Google AppEngine mapreduce and pipeline libraries.
