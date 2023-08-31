from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Elevator
from .serializers import ElevatorSerializer
from django.db import connection

class ElevatorSystem:
    """Utility class to manage and decide which elevator to assign a request."""

    def assign_elevator(requested_floor):
        elevators = Elevator.objects.filter(status='O')  # Only consider elevators that are operational

        if not elevators.exists():
            return None
        
        # Case 1: Elevator is on the floor and stationary
        elevators_on_floor = [e for e in elevators if e.is_on_floor(requested_floor) and e.direction == 'N']
        if elevators_on_floor:
            return elevators_on_floor[0]

        # Case 2: Elevator moving towards the requested floor
        moving_towards_elevators = [
            e for e in elevators
            if (e.direction == 'U' and e.current_floor < requested_floor) or 
               (e.direction == 'D' and e.current_floor > requested_floor)
        ]
        if moving_towards_elevators:
            return min(moving_towards_elevators, key = lambda e: abs(e.current_floor - requested_floor))

        # Case 3: Choose the closest stationary elevator
        stationary_elevators = [e for e in elevators if e.direction == 'N']
        if stationary_elevators:
            return min(stationary_elevators, key = lambda e: abs(e.current_floor - requested_floor))

        # If none of the above, return any available elevator
        return elevators[0] if elevators else None


class ElevatorViewSet(viewsets.ModelViewSet):
    queryset = Elevator.objects.all()
    serializer_class = ElevatorSerializer

    @action(detail=False, methods=['post'])
    def initialise_system(self, request):
        # Delete all existing elevators
        Elevator.objects.all().delete()

        # Reset the primary key sequence for SQLite
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='elevator_app_elevator';")

        # Create new elevators
        num_elevators = request.data.get('num_elevators', 0)
        for _ in range(num_elevators):
            Elevator.objects.create()

        return Response({'status': f'Elevator system initialised with {num_elevators} elevators.'})

    @action(detail=True, methods=['get'])
    def next_destination(self, request, pk=None):
        elevator = self.get_object()
        next_floor = elevator.get_next_destination()
        return Response({'next_destination': next_floor})

    @action(detail=True, methods=['patch'])
    def change_door_status(self, request, pk=None):
        elevator = self.get_object()

        # Check if the elevator is in a neutral direction
        if elevator.direction != 'N':
            return Response({
                'error': 'Door status can only be changed when the elevator is in a neutral direction.'
            }, status=400)

        door_status = request.data.get('door_status')
        if door_status in ['O', 'C']:
            elevator.change_door_status(door_status)
            return Response({'door_status': elevator.door})
        else:
            return Response({
                'error': 'Invalid door status provided.'
            }, status=400)

    @action(detail=True, methods=['patch'])
    def mark_maintenance(self, request, pk=None):
        elevator = self.get_object()
        is_maintenance = request.data.get('is_maintenance', False)
        elevator.mark_maintenance(is_maintenance)
        return Response({'status': 'Elevator marked as {}'.format(elevator.get_status_display())})
    
    @action(detail=True, methods=['post'])
    def floor_request(self, request, pk=None):
        """Request an elevator from a specific floor."""
        elevator = self.get_object()
        
        # Check if the elevator is operational
        if elevator.status == 'NW':  # Not Working
            return Response({'error': f'Elevator {elevator.id} is not working and cannot accept requests.'}, status=400)

        
        floor = request.data.get('floor')
        if floor not in elevator.requests:
            elevator.requests.append(floor)
            elevator.requests.sort()  # Sort for easier decision-making
            elevator.save()
        
        # Decide the next action and set the elevator's direction
        action = elevator.decide_next_action()
        if action == 'UP':
            elevator.direction = 'U'
        elif action == 'DOWN':
            elevator.direction = 'D'
        else:
            elevator.direction = 'N'
        elevator.save()
        
        return Response({'status': f"Elevator {elevator.id} has received the request for floor {floor}"})
    
    @action(detail=True, methods=['get'])
    def direction(self, request, pk=None):
        elevator = self.get_object()
        return Response({'direction': elevator.direction})
    
    @action(detail=True, methods=['post'])
    def move_elevator(self, request, pk=None):
        elevator = self.get_object()
        elevator.move_to_next_destination()
        return Response({'status': f'Elevator {elevator.id} moved to floor {elevator.current_floor}. Remaining requests: {elevator.requests}'})
    
    @action(detail=False, methods=['post'])
    def assign_elevator(self, request):
        """Assign an elevator based on a floor request."""
        floor = request.data.get('floor')
        if floor is None:
            return Response({"error": "Please provide a floor number in the request."}, status=400)
        
        # Check if all elevators are non-operational
        if not Elevator.objects.filter(status='O').exists():
            return Response({"error": "All elevators are currently non-operational."}, status=503)  # HTTP 503 Service Unavailable

        elevator = ElevatorSystem.assign_elevator(floor)
        
        if not elevator:
            return Response({"error": "No available operational elevators at the moment."}, status=404)
        
        elevator.add_request(floor)
        return Response({"message": f"Elevator {elevator.id} assigned for floor {floor}"})
