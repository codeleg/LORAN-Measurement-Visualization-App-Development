import numpy as np
import matplotlib.pyplot as plt
import asyncio
import websockets
import json

# Constants
SPEED_OF_LIGHT = 3e8  # speed of light in m/s

# TDoA error function
def tdoa_error(params, x1, y1, x2, y2, x3, y3, delta_t12, delta_t13, c):
    x, y = params
    d1 = np.sqrt((x - x1)**2 + (y - y1)**2)
    d2 = np.sqrt((x - x2)**2 + (y - y2)**2)
    d3 = np.sqrt((x - x3)**2 + (y - y3)**2)

    delta_t12_calc = (d1 - d2) / c
    delta_t13_calc = (d1 - d3) / c

    return [delta_t12_calc - delta_t12, delta_t13_calc - delta_t13]

def loss_function(params, tdoa_error_func, args):
    errors = tdoa_error_func(params, *args)
    loss = sum(e**2 for e in errors)
    return loss

def custom_least_squares(tdoa_error_func, initial_guess, args, learning_rate=0.01, max_iterations=1000, tolerance=1e-6):
    x, y = initial_guess
    prev_loss = float('inf')

    for iteration in range(max_iterations):
        loss = loss_function([x, y], tdoa_error_func, args)
        if abs(prev_loss - loss) < tolerance:  #burada bir sorun var 
            print(f"Converged after {iteration} iterations")
            break
        prev_loss = loss

        # Gradient calculation
        delta = 1e-8
        grad_x = (loss_function([x + delta, y], tdoa_error_func, args) - loss) / delta
        grad_y = (loss_function([x, y + delta], tdoa_error_func, args) - loss) / delta

        # Update coordinates
        x -= learning_rate * grad_x
        y -= learning_rate * grad_y

        if iteration % 100 == 0:
            print(f"Iteration {iteration}: x={x}, y={y}, loss={loss}")

    return x, y
#delte'yı doğru hesapla
#  # Initial data
# x1, y1 = 0, 0
# x2, y2 = 100000, 0
# x3, y3 = 0, 100000 
# Measured time differences of arrival (in seconds)

# delta_t12 = 0.0001806640625*10e8
# delta_t13 =  -0.00014453125*10e8
# c = 3e8/10e8

async def get_loran_data():
    uri = "ws://localhost:4002"  # WebSocket endpoint
    base_stations = [(0, 0), (100000, 0), (0, 100000)]
    
    plt.ion()  # Turn on interactive mode for live plotting
    fig, ax = plt.subplots()
    ax.set_xlim(-50000, 150000)
    ax.set_ylim(-50000, 150000)
    ax.set_xlabel('X Coordinate (m)')
    ax.set_ylabel('Y Coordinate (m)')

    # Initial plot of base stations
    for (x, y) in base_stations:
        ax.plot(x, y, 'ro')  # Base stations in red
    plt.pause(0.1)

    try:
        async with websockets.connect(uri) as websocket:
            async for message in websocket:
                data = json.loads(message)
                print(f"Received data: {data}")
 #asıl proplem burda 
                delta_t12 = data.get("delta_t12", 0)  # Default to 0 if not present //ilk versionu  burada
                delta_t13 = data.get("delta_t13", 0)  # Default to 0 if not present //gelinin değerinin doğru olup olamdıgını control et.

                # Ensure delta_t values are numbers
                if not isinstance(delta_t12, (int, float)):
                    delta_t12 = 0
                if not isinstance(delta_t13, (int, float)):
                    delta_t13 = 0

                c = SPEED_OF_LIGHT
                initial_guess = [50000, 50000]

                x_opt, y_opt = custom_least_squares(
                    tdoa_error, 
                    initial_guess,
                    (base_stations[0][0], base_stations[0][1], 
                     base_stations[1][0], base_stations[1][1], 
                     base_stations[2][0], base_stations[2][1], 
                     delta_t12, delta_t13, c)
                )

                # Clear the previous estimated position
                ax.cla()  # Clear axes
                ax.set_xlim(-50000, 150000)
                ax.set_ylim(-50000, 150000)
                ax.set_xlabel('X Coordinate (m)')
                ax.set_ylabel('Y Coordinate (m)')

                # Redraw base stations
                for (x, y) in base_stations:
                    ax.plot(x, y, 'ro')

                # Plot the estimated position of the receiver
                ax.plot(x_opt, y_opt, 'bo')  # Estimated position in blue
                plt.pause(0.1)  # Pause to update the plot

    except asyncio.CancelledError:
        print("WebSocket bağlantısı iptal edildi.")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")

def process_received_data(received_data):
    required_keys = ['delta_t12', 'delta_t13']
    for key in required_keys:
        if key not in received_data:
            print(f"{key} is missing from the data! Setting default value to 0.")
            received_data[key] = 0  # Set default value if key is missing

    print("Processed data:", received_data)

def receive_data():
    received_data = {
        'id': '00be15e4-8840-4630-83fe-aaa7371b13bf',
        'sourceId': 'source1',
        'receivedAt': 1730238677070.202,
    }
    process_received_data(received_data)

if __name__ == "__main__":
    try:
        asyncio.run(get_loran_data())
    except KeyboardInterrupt:
        print("Program Stoped.")
