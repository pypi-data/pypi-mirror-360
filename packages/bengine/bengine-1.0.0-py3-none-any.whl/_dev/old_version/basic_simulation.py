import csv
import datetime
import numpy as np
import matplotlib.pyplot as plt
import argparse
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Polygon
from matplotlib.transforms import Affine2D

# From pedestrian.py file
from old_version.pedestrian import Person

# HIDE WARNINGS
import warnings
warnings.filterwarnings("ignore")

def main(args)->None:
    # Unpack arguments
    num_people = args.num_people
    save_as_mp4 = args.save_mp4

    # --------------------------------------------------------------------------------------------------------

    # Instantiate some people
    people_instances = []
    for i in range(num_people):
        person_instance = Person()
        people_instances.append(person_instance)

    # --------------------------------------------------------------------------------------------------------

    # Initialise CSV with current datetime in file name, for uniqueness
    now = datetime.datetime.now()
    csv_path = "Simulation_CSVs/simulation_"+str(num_people)+str(now.time())+"_"+str(now.date())+".csv"
    csv_path = csv_path.replace(":","-") # makes file more readable

    # Create header columns, 4 for each person id
    csv_header = ["time_step"]
    for person in Person.all:
        id = str(person.person_id)
        csv_header += ["pos_x_"+id,"pos_y_"+id,"vel_x_"+id,"vel_y_"+id]

    # Write to the CSV path and add header
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(csv_header) 

    # Function to write into CSV with a list, in append mode
    def write_row(row: list):
        with open(csv_path, mode='a', newline='') as file:  
            writer = csv.writer(file)
            writer.writerow(row)

    # --------------------------------------------------------------------------------------------------------

    # Loop through timesteps
    time_steps = 100
    for t in range(time_steps):
        # Print calculation progress
        print(f"----- Computation progress: {t} / {time_steps} -----" ,end="\r", flush=True)

        # Before updating, store position and velocity for each person
        new_csv_row = [t]
        for person in Person.all:
            pos_x, pos_y = person.position[0], person.position[1]
            vel_x, vel_y = person.velocity[0], person.velocity[1]
            new_csv_row += [pos_x, pos_y, vel_x, vel_y]
        write_row(new_csv_row)
        
        # Update force term for each person
        for person in Person.all:
            person.update_force_term()
        # Update velocity and position from force term
        for person in Person.all:
            person.update_velocity()
            person.position += person.velocity # Take a step

    # Final state
    new_csv_row = [time_steps]
    for person in Person.all:
        pos_x, pos_y = person.position[0], person.position[1]
        vel_x, vel_y = person.velocity[0], person.velocity[1]
        new_csv_row += [pos_x, pos_y, vel_x, vel_y]
    write_row(new_csv_row)

    # --------------------------------------------------------------------------------------------------------
    # Animate the CSV
    print("-")
    print("\n")

    # Initialise a scatter plot (need all of this)
    fig, ax = plt.subplots(figsize=[7,7])
    fig.canvas.set_window_title(f'Crowd Simulation animation, {num_people} people')
    ax.set_xlim(0, Person.walls_x_lim)  # Set x-axis limits
    ax.set_ylim(0, Person.walls_y_lim)  # Set y-axis limits
    scat = ax.scatter([], [])

    # Triangle creator for directed markers
    def create_irregular_triangle(angle_rad):
        # Define vertices for an irregular triangle (relative to origin)
        triangle = np.array([[-0.5, -1], [0.5, -1], [0.0, 1]])
        # Create a rotation matrix
        rotation_matrix = np.array([[np.cos(angle_rad), -np.sin(angle_rad)],
                                    [np.sin(angle_rad),  np.cos(angle_rad)]])
        # Apply the rotation to the triangle vertices
        return triangle @ rotation_matrix.T

    def update(frame):
        # Progress bar
        print(f"----- Animation progress: {frame} / {time_steps} -----" ,end="\r", flush=True)

        # Clear axis between frames, set axes limits again
        ax.clear()
        ax.set_xlim(0, Person.walls_x_lim)  # Set x-axis limits
        ax.set_ylim(0, Person.walls_y_lim)  # Set y-axis limits
        ax.set_aspect('equal', adjustable='box')

        # Plot attraction and radius
        attract_x, attract_y = Person.attract_point[0], Person.attract_point[1]
        attract_r = np.sqrt(Person.attract_radius)
        ax.scatter([attract_x],[attract_y], c="k",marker='x')
        circle_thetas = np.linspace(0,2*np.pi)
        ax.plot((attract_r*np.cos(circle_thetas)+attract_x), 
                (attract_r*np.sin(circle_thetas)+attract_y), c='k', linestyle=':', alpha=0.3)

        # Open row in CSV
        with open(csv_path, mode='r', newline='') as file:
            reader = csv.reader(file)

            # Loop through the CSV rows until reaching the desired row
            # This must be done since CSV doesn't have indexed data structure
            target_row_index = frame+1 
            for i, row in enumerate(reader):
                if i == target_row_index:
                    current_step_strings = row
                    current_step = [float(x) for x in current_step_strings] # Convert string -> float!
                    break
                    
        # Columns are:
        # time_step, pos_x_0, pos_y_0, vel_x_0, vel_y_0, pos_x_1, pos_x_2, ...
        # Extract x,y positions to scatter
        pos_x_vals = [current_step[i] for i in range(4*num_people+1) if ((i-1)%4 == 0)]
        pos_y_vals = [current_step[i] for i in range(4*num_people+1) if ((i-2)%4 == 0)]
        # Extract velocity to get direction
        vel_x_vals = [current_step[i] for i in range(4*num_people+1) if ((i-3)%4 == 0)]
        vel_y_vals = [current_step[i] for i in range(4*num_people+1) if ((i-4)%4 == 0 and i!=0)]
        thetas = np.arctan2(vel_y_vals, vel_x_vals) - np.pi/2

        # Plot directed points
        for i in range(len(pos_x_vals)):
            # Create a Polygon patch to represent the irregular triangle
            triangle_shape = create_irregular_triangle(thetas[i])
            polygon = Polygon(triangle_shape, closed=True, facecolor='blue', edgecolor='black')
            
            # Create transformation of the polygon to the point
            t = Affine2D().translate(pos_x_vals[i], pos_y_vals[i]) + ax.transData
            polygon.set_transform(t)  # Apply the translation
            ax.add_patch(polygon)

        ax.set_title(f"Time step {round(int(current_step[0]))}")

    # Animate frames by calling update() function
    interval_between_frames = 100 # milliseconds
    ani = FuncAnimation(fig, update, frames=time_steps, interval=100)

    if save_as_mp4:
        mp4_path = "Simulation_mp4s/crowd_"+str(num_people)+"_"+str(now.time())+"_"+str(now.date())+".MP4"
        mp4_path = mp4_path.replace(":","-")
        fps = 1/(interval_between_frames*(10**(-3))) # period -> frequency
        ani.save(mp4_path, writer='ffmpeg', fps=fps)
        print("\n")
        print(f"Saved simulation as mp4 at {mp4_path}.")

    plt.show()

if __name__ == '__main__':
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Process some integers.")
    
    # Add arguments
    parser.add_argument('--num_people', type=int, help='The number of people for the simulation', default=100)
    parser.add_argument('--save_mp4', type=bool, help='Whether to save the simulation as an mp4 video', default=True)
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Call the main function with parsed arguments
    main(args)

