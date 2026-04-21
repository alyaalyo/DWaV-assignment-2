## About the project

A real-time 3D network traffic visualization system built with Python, Flask, and Three.js. A Python sender script reads IP traffic data from a CSV file and streams it to a Flask backend via HTTP GET requests, respecting the original packet timestamps to preserve temporal distribution. The backend fans the incoming data out to all connected browser clients using Server-Sent Events (SSE) and retains full history so late-joining clients receive a complete replay. The frontend renders an interactive 3D Earth globe where each packet appears as a geo-located dot (red for suspicious, cyan for normal). Two real-time interactive panels update as data arrives: a ranked top-15 source IP list with proportional bar charts, and an activity timeline showing packet volume per 10-second interval. Users can rotate and zoom the globe, and hovering over any point shows the IP address, coordinates, and timestamp.

## Run instructions

```docker-compose up --build```
