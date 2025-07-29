# learning_classes.py

# Define global counter variable
counter = 0

# Define a Car class, (capitalised)
class Car:
    # We define an intialisation method function of the class, containing starting attributes
    def __init__(self, colour: str, position: float) -> None:
        # This has 2 arguments we need to specify when we create a Car instance
        self.colour = colour
        self.position = position

        # Update global counter each time a Car is initialised
        global counter
        self.car_id = counter
        counter += 1

    # We define a 'drive' method
    def drive(self, distance) -> None:
        self.position += distance
        print(f"{self.colour} car now at position {self.position}")

    # Define one of the 'dunder' methods (with underscores)
    def __str__(self) -> str:
        # This tells us what string to return to a print function when instance printed
        return f"Car with ID {self.car_id} is {self.colour}, and at position {self.position}."
    
    # Define the distance between cars
    def distance(self, other) -> str:
        return f"The distance between Car {self.car_id} and Car {other.car_id} is {round(abs(self.position - other.position), 2)}"

# Package script into 'main'
def main_function():
    
    # Create a couple of instances of the Car class
    bmw = Car("white", 5)
    volvo = Car("red",2)

    # Print the colour of the bmw Car
    print(f"The BMW has a {bmw.colour} colour")

    # Drive the bmw a few metres down the road
    volvo.drive(5.4)

    # Print the bmw and volvo __str__:
    print(bmw)
    print(volvo)

    print(bmw.distance(volvo))

# Call main_function 
if __name__ == '__main__':
    main_function()