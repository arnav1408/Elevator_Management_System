# Elevator_System

**Introduction**

The Elevator Management System (EMS) is developed to effectively handle and automate the operations of multiple elevators within a building. Through our EMS, users can dispatch floor requests to elevators, and the system strategically assigns an elevator that optimally caters to the request.

**Thought Process**

Scalability: Recognizing that large buildings can house several elevators, the system was architected with scalability at its core. This ensures that even as the number of requests or elevators burgeon, the system remains efficient.

Efficiency: Ensuring rapid responses, the system leverages an algorithm that contemplates both the direction of the elevator and its proximity to the requested floor.

Reliability: Real-world scenarios often include elevator maintenance or unforeseen breakdowns. Our EMS acknowledges this, providing functionalities to mark elevators as non-operational.

**Design Decisions**

Database Choice: SQLite was chosen for its lightweight nature, minimal setup, and reliability for development projects.

Django Framework: With its "batteries-included" philosophy, Django furnishes all essential tools for web development straight out of the box.

**API Contracts**

1. Initialise Elevator System\
Endpoint: POST /api/elevators/initialise_system/\
Description: This endpoint initializes the elevator system by deleting all existing elevators and creating a fresh set of elevators as per the provided count.

Payload:

json format

{

    "num_elevators": <number_of_elevators>

}

Example: To initialize the system with 3 elevators:

{

    "num_elevators": 3

}

2. Get Next Destination for an Elevator
   
Endpoint: GET /api/elevators/<lift_id>/next_destination/

Description: Returns the next destination floor for the specified elevator.

Example: To check the next destination for elevator with ID 2: GET /api/elevators/2/next_destination/

3. Change Door Status of an Elevator
   
Endpoint: PATCH /api/elevators/<lift_id>/change_door_status/

Description: Allows changing the door status (open/close) of the specified elevator. The elevator should be in a neutral direction to perform this action.

Payload:

json format

{

    "door_status": "O" or "C"
    
}

Example: To change the door status of elevator with ID 2 to open:

json

{

    "door_status": "O"
    
}

4. Mark Elevator for Maintenance
   
Endpoint: PATCH /api/elevators/<lift_id>/mark_maintenance/

Description: Marks the elevator as either operational or under maintenance.

Payload:

json

{

    "is_maintenance": true or false
    
}

Example: To mark elevator with ID 2 for maintenance:

json

{

    "is_maintenance": true
    
}

5. Send Floor Request for an Elevator

Endpoint: POST /api/elevators/<lift_id>/floor_request/

Description: Registers a request for the elevator to move to a specified floor.

Payload:

json

{

    "floor": <desired_floor_number>
    
}

Example: To send a request to elevator with ID 2 to move to the 5th floor:

json

{

    "floor": 5
    
}

6. Get Current Direction of an Elevator
   
Endpoint: GET /api/elevators/<lift_id>/direction/

Description: Returns the current movement direction of the specified elevator.

Example: To get the current direction of elevator with ID 2: GET /api/elevators/2/direction/

7. Move Elevator to Next Destination
   
Endpoint: POST /api/elevators/<lift_id>/move_elevator/

Description: Commands the specified elevator to move to its next destination based on its request queue.

Example: To move the elevator with ID 2 to its next destination: POST /api/elevators/2/move_elevator/

8. Assign an Elevator based on Floor Request
   
Endpoint: POST /api/elevators/assign_elevator/

Description: Assigns an operational elevator to cater to a request from a specific floor using the algorithm to determine the most optimal lift for the operation.

Payload:

json

{

    "floor": <requested_floor_number>
    
}

Example: To request an elevator for the 3rd floor:

json

{

    "floor": 3
    
}

**Setup and Deployment**

Prerequisites:

Python 3.8+

Setup:

1. Clone the GitHub repository:

git clone [repository_url]
cd [repository_name]

2. Set up a virtual environment and activate it:

python -m venv env
source env/bin/activate  # On Windows use: .\env\Scripts\activate

3. Install the required packages:

pip install -r requirements.txt

Running:

Begin the Django development server:

4. python manage.py runserver

**Architecture and Modelling**

Architecture: Adhered to Django's conventional MTV (Model, Template, View) architecture. Within this setup, the model denotes the database structure, views oversee business logic, and templates are responsible for the presentation layer.

Database Modelling: The primary model is Elevator, equipped with attributes such as current_floor, status, direction, and so forth.

Repository Structure:

models.py: Contains the database models.

views.py: Manages the business logic and API endpoints.

serializers.py: Responsible for data serialization.

...

**Plugins and Libraries Employed**

Django Rest Framework (DRF): Facilitates the creation of API endpoints and manages request/response data.

SQLite: As an embedded SQL database engine, SQLite offers a lightweight, serverless, and self-contained system.
