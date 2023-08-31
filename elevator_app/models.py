from django.db import models

class Elevator(models.Model):
    DIRECTIONS = (
        ('U', 'Up'),
        ('D', 'Down'),
        ('N', 'None'),
    )

    STATUS = (
        ('O', 'Operational'),
        ('NW', 'Not Working'),
    )

    DOOR_STATUS = (
        ('O', 'Open'),
        ('C', 'Closed'),
    )

    current_floor = models.IntegerField(default=0)
    status = models.CharField(max_length=2, choices=STATUS, default='O')
    direction = models.CharField(max_length=1, choices=DIRECTIONS, default='N')
    door = models.CharField(max_length=1, choices=DOOR_STATUS, default='')
    requests = models.JSONField(default=list)  # List of requested floors

    def move(self, direction):
        """Move the elevator one floor in the given direction."""
        if direction == 'U':
            self.current_floor += 1
        elif direction == 'D':
            self.current_floor -= 1
        self.direction = direction
        self.save()

    def add_request(self, floor):
        """Add a floor request to the elevator."""
        if floor not in self.requests:
            self.requests.append(floor)
            self.requests.sort()
            self.save()

    def get_next_destination(self):
        """Fetch the next destination for the elevator based on the Elevator Algorithm."""
        if not self.requests:
            return None  # No requests to service
        
        # If elevator is moving up
        if self.direction == 'U':
            above_requests = [floor for floor in self.requests if floor > self.current_floor]
            if above_requests:
                return min(above_requests)
            return max(self.requests)  # No requests above; change direction on next move
        
        # If elevator is moving down
        if self.direction == 'D':
            below_requests = [floor for floor in self.requests if floor < self.current_floor]
            if below_requests:
                return max(below_requests)
            return min(self.requests)  # No requests below; change direction on next move
    
        # If elevator is neutral, move to the closest request
        return min(self.requests, key=lambda x: abs(x - self.current_floor))

    def change_door_status(self, status):
        """Open or close the elevator door."""
        self.door = status
        self.save()

    def mark_maintenance(self, is_maintenance):
        """Mark the elevator as operational or not working."""
        self.status = 'NW' if is_maintenance else 'O'
        self.save()

    def __str__(self):
        return f"Elevator {self.id} on floor {self.current_floor}"
        
    def is_on_floor(self, floor):
        """Check if the elevator is currently on a given floor."""
        return self.current_floor == floor
    
    def decide_next_action(self):
        """Decide the next action for the elevator based on its current direction and requests."""
        if not self.requests:
            self.direction = 'N'
            self.change_door_status(self.DOOR_STATUS[0][0])  
            return 'STOP'
        
        if self.direction == 'N':
            # If elevator's direction is neutral, move towards the closest request
            closest_request = min(self.requests, key=lambda x: abs(x - self.current_floor))
            direction = 'U' if closest_request > self.current_floor else 'D'
            self.direction = direction
            self.change_door_status(self.DOOR_STATUS[1][0])  
            return direction
        
        if self.direction == 'U':
            # If moving up, continue moving up if there are requests above the current floor
            above_requests = [floor for floor in self.requests if floor > self.current_floor]
            direction = 'UP' if above_requests else 'DOWN'
            if direction == 'DOWN':
                self.change_door_status(self.DOOR_STATUS[1][0])  
            return direction
        
        if self.direction == 'D':
            # If moving down, continue moving down if there are requests below the current floor
            below_requests = [floor for floor in self.requests if floor < self.current_floor]
            direction = 'DOWN' if below_requests else 'UP'
            if direction == 'UP':
                self.change_door_status(self.DOOR_STATUS[1][0])  
            return direction

                
    def move_to_next_destination(self):
        """Simulate moving the elevator to its next designated floor and update its state."""
        next_dest = self.get_next_destination()
        if next_dest is not None:
            
            # Determine direction
            if next_dest > self.current_floor:
                self.direction = 'U'  # Moving Up
            elif next_dest < self.current_floor:
                self.direction = 'D'  # Moving Down
            else:
                self.direction = 'N'  # Not moving, already at the floor
                
            # Ensure the door is closed before moving
            self.change_door_status(self.DOOR_STATUS[1][0])

            self.current_floor = next_dest  # Set the current floor to the next destination
            self.requests.remove(next_dest)  # Remove the next destination from the requests

            # Check if requests list is empty, if so, set direction to Neutral and open the door
            if not self.requests:
                self.direction = 'N'
                self.change_door_status(self.DOOR_STATUS[0][0])

            self.save()
