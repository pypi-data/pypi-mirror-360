# person.py

import numpy as np

# Define global counter variable
counter = 0

class Person:
    # Class attribute set of all people
    all = []
    
    # Person
    person_dist_thresh = 10**2
    person_force = 5
    max_speed = 1
    person_inertia = 1

    # Walls 
    walls_dist_thresh = 1**2
    walls_force = 3
    walls_x_lim = 100
    walls_y_lim = 100

    # Attraction point
    attract_point = np.array([60,60])
    attract_pull = 30
    attract_radius = 60**2

    # Random
    random_force = 0.5

    # Class to describe each person in simulation
    def __init__(self, 
                position: np.ndarray = None,
                velocity: np.ndarray = None) -> None:
        
        #TODO Check for correct formats

        # Assign random position and stationary velocity if not given
        if position is None:
            self.position = np.random.rand(2)*100
        if velocity is None:
            self.velocity = np.zeros(2)

        # Start with zero acceleration
        self.force_term = np.zeros(2)

        # Add to set of all people
        global counter
        self.person_id = counter
        counter += 1
        Person.all += [self]

    # Print statement for person
    def __str__(self) -> str:
        return f"Person at position {self.position} with velocity {self.velocity}"

    # Debug statement for person
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.position},{self.velocity})"


    # Calculate squared euclidean distance between people
    def dist(self,other) -> float:
        return np.sum((self.position-other.position)**2)
    
    # Calculate distance direction between people
    def dirn(self,other) -> float:
        return (self.position-other.position)/np.sqrt(self.dist(other))
    

    # Update force term and store as attribute
    def update_force_term(self) -> None:
        force_term = np.zeros(2)

        # Personal force - currently 1/d
        for person in Person.all:
            if person == self:
                continue
            elif self.dist(person) < Person.person_dist_thresh:
                force_term += self.dirn(person)*(Person.person_force/(np.sqrt(self.dist(person))))
            else:
                continue

        # Force from walls - ideally would find shortest dist etc
        pos_x, pos_y = self.position[0], self.position[1]
        if pos_x < Person.walls_dist_thresh:
            force_term += Person.walls_force * np.array([1,0])
        elif pos_x > (Person.walls_x_lim - Person.walls_dist_thresh):
            force_term += Person.walls_force * np.array([-1,0])
        if pos_y < Person.walls_dist_thresh:
            force_term += Person.walls_force * np.array([0,1])
        elif pos_y > (Person.walls_y_lim - Person.walls_dist_thresh):
            force_term += Person.walls_force * np.array([0,-1])

        # Force from attraction point
        attract_dist = np.sum((self.position-self.attract_point)**2)
        if attract_dist < self.attract_radius:
            force_term += self.attract_pull*(self.attract_point-self.position)/(attract_dist)

        # Random force - stochastic noise
        # Generate between [0,1], map to [0,2] then shift to [-1,1]
        force_term += ((np.random.rand(2)*2)-1)*Person.random_force

        self.force_term = force_term

    def update_velocity(self):
        # Update velocity via force term
        self.velocity += self.force_term / self.person_inertia
        speed = np.sqrt(np.sum(self.velocity)**2)
        # Normalise speed to max in whichever direction it points
        if speed > Person.max_speed:
            self.velocity *= Person.max_speed/speed



            


    


    


    
    