# rail-away (placeholder name)

This is a project created as part of the Hack4Rail Hackathon 2025: https://hack4rail.event.sbb.ch/

Consists of a frontend, backend, and matcher tool.

**Matcher** Is basically a preprocessors that takes a geojson of locations of activities from OSM and a GTFS export. It
then computes the reachability from a set of stops to all other stops and combines the mapping with possible activities
that can be done at the destinations.
**Frontend** Is a web-based frontend that allows users to provide their spending time and the type of activity they wish
to do. It then provides suggestions on journeys with possible activities of the requested category at their ends.
**Backend** Takes the output of the matcher and based on the given spending time and location provided from the frontend
returns a set of possible origin, destinations, and activities.