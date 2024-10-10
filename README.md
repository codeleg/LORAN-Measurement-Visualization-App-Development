LORAN-Measurement-Visualization-App-Development

Project Purpose

The purpose of this project is to visualize measurements made with the LORAN (Long Range Navigation) system and to allow the user to interactively change system parameters. By using WebSockets and Chart.js, the project aims to display and analyze specific measurement data in real-time on a graph. The user can instantly update the visualized data by changing the object's speed and the coordinates of the LORAN stations.

Task Description

This project operates through three main components:

Real-Time Visualization: Data received from the server via WebSocket is processed instantly and displayed on the graph using Chart.js. This visualization graphically shows the positions of the LORAN stations and the moving object over time.

Parameter Updates with User Inputs: The user can change the object’s speed, station coordinates, and LORAN parameters through input forms located on the right side. These inputs are sent to the server, allowing for real-time data updates.

Calculating Object Position Using the Least Squares Method: The estimated position of the object is calculated based on signal times received from three LORAN stations and added to the visualization.

1-Prerequisites

Downloading and running the LORAN measurement emulator:

The LORAN measurement emulator is provided as a Docker image named iperekrestov/university/loran-emulation-service. To run the emulator, follow these steps:

Download the Docker image from Docker Hub:

docker pull iperekrestov/university:loran-emulation-service

Run the Docker container using the following command:

docker run --name loran-emulator -p 4002:4000 iperekrestov/university:loran-emulation-service

This command starts the container named loran-emulator and opens port 4002 on the host machine, which maps to port 4000 inside the container, to connect to the LORAN measurement emulator.

Modifying and retrieving parameters via API:

The service supports an API for modifying and retrieving the following parameters of the LORAN measurement system:

Retrieving the configuration via GET request: The current configuration with emulation zone parameters and object speed can be obtained using a GET request:

curl http://localhost:4002/config

Modifying the object speed via POST request:

curl -X POST http://localhost:4002/config -H "Content-Type: application/json" -d '{
  "objectSpeed": 120
}'

The configuration includes the following parameters:

emulationZoneSize: Size of the emulation zone (in kilometers, default is 100x100 km).
objectSpeed: Object speed (in km/h, default is 100 km/h).
Message format sent through WebSocket:

The data sent through WebSocket from the LORAN emulator includes information about the base stations and the object. Messages are sent in JSON format and have the following structure:

{
  "id": "uuid",
  "sourceId": "source_x",
  "receivedAt": 1692170400100
}

Explanation of fields:

id: Unique message identifier (UUID).
sourceId: Identifier of the base station that sent the signal.
receivedAt: Time the signal was received by the base station (milliseconds since Unix epoch).

-LORAN Measurement Visualization-
# Script Block Explanations #

1- For WebSocket Connection

javascript :

const ws = new WebSocket('ws://localhost:4002');
Purpose: Initiates a WebSocket connection to receive real-time data from the server.
Explanation: When a message is received via WebSocket, the relevant message is processed and displayed on the graph.

2- Object Speed Change Function

javascript :

function changeObjectSpeed() {
    const speed = document.getElementById('objectSpeed').value;
    const data = { objectSpeed: parseInt(speed) };

    fetch('http://localhost:4002/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => console.log('Object speed changed:', data))
    .catch(error => console.error('Error:', error));
}
Purpose: Sends the user's inputted object speed to the server.
Explanation: It retrieves the object speed from the input field, sends it to the server, and displays the success status in the browser console.

3- Chart.js for Graph Visualization

javascript:

const ctx = document.getElementById('loranCanvas').getContext('2d');
const loranChart = new Chart(ctx, {
    type: 'scatter',
    data: {
        datasets: [{
            label: 'Base Stations',
            data: [],
            backgroundColor: 'blue',
            showLine: true,  // Show line connecting points
        }, {
            label: 'Object',
            data: [],
            backgroundColor: 'red',
            pointStyle: 'triangle'
        }]
    },
    options: {
        responsive: true,
        scales: {
            x: { type: 'linear', position: 'bottom', title: { display: true, text: 'X Coordinate' } },
            y: { type: 'linear', position: 'left', title: { display: true, text: 'Y Coordinate' } }
        }
    }
});
Purpose: Creates a graph to visualize LORAN stations and the object's position for the user.
Explanation: A scatter plot is created using Chart.js. The coordinates of the stations and the object are visualized in different colors.

4-Receiving Data via WebSocket and Reflecting it on the Graph

javascript:

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    console.log('Received message:', message);

    const receivedAt = message.receivedAt;
    const sourceY = sourceIdMap[message.sourceId] || 0;

    if (message.sourceId.startsWith('source')) {
        const baseStationIndex = parseInt(message.sourceId.slice(-1)) - 1;
        loranChart.data.datasets[0].data.push({
            x: receivedAt,
            y: sourceY
        });
        loranChart.data.datasets[0].pointBackgroundColor = loranChart.data.datasets[0].data.map((_, index) => colors[index % colors.length]);
    } else if (message.sourceId === 'object') {
        loranChart.data.datasets[1].data = [{ x: receivedAt, y: sourceY }];
    }

    loranChart.update();
};
Purpose: To receive messages from the server and reflect them on the graph.
Explanation: Data from the stations and the object is processed and added to the graph. Each station is displayed in a different color, and the object’s movements are updated in real-time.

5-Updating Coordinates and Calculating Object Position

javascript

function updateStationCoordinates() {
    const station1 = parseCoordinates('station1Coords');
    const station2 = parseCoordinates('station2Coords');
    const station3 = parseCoordinates('station3Coords');

    const baseStations = [station1, station2, station3];
    const signalTimes = [10, 15, 20]; // Placeholder times

    const objectPosition = calculateObjectPosition(station1, station2, station3, signalTimes);

    loranChart.data.datasets[0].data = [
        { x: station1.x, y: station1.y, backgroundColor: 'blue' },
        { x: station2.x, y: station2.y, backgroundColor: 'green' },
        { x: station3.x, y: station3.y, backgroundColor: 'yellow' }
    ];

    loranChart.data.datasets[1].data = [{ x: objectPosition.x, y: objectPosition.y, backgroundColor: 'red' }];

    loranChart.update();
}

Purpose: To recalculate the object's position based on the newly entered station coordinates and update the graph.
Explanation: The object's position is calculated based on the coordinates obtained from the user, and drawn on the graph.

Updating LORAN Parameters

javascript:

function updateLORANParams() {
    const param1 = document.getElementById('loranParam1').value;
    const param2 = document.getElementById('loranParam2').value;

    const params = { param1: parseFloat(param1), param2: parseFloat(param2) };

    fetch('http://localhost:4002/loranParams', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
    })
    .then(response => response.json())
    .then(data => console.log('LORAN params updated:', data))
    .catch(error => console.error('Error:', error));
}
Purpose: To allow the user to change certain parameters of the LORAN system.
Explanation: The parameters entered by the user are sent to the server, and the parameters are updated.

Conclusion
This project provides users with an application that allows for interactive visualization of LORAN measurements and the modification of parameters. Real-time data processing and visualization are achieved using WebSockets and Chart.js.
