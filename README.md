# AIRPORT SERVICE API

The RESTful API for an airport service platform. 


## User Registration and Authentication:

- Users can register with their email and password to create an account.
- Users can login with their credentials and receive a JWT token for authentication.
- Users can logout and invalidate their JWT token.

## User Profile:
- Users can create and update their profile, including profile picture and other details.
- Users can retrieve their own profile.

## Airport
- User with admin permission can create/update/retrieve/delete airport.
- User who is authenticated can retrieve the airport.

## Route
- User with admin permission can create/update/retrieve/delete routes.
- User who is authenticated can retrieve the route.

## Crew
- User with admin permission can create/update/retrieve/delete crew.
- User who is authenticated can retrieve crew.

## Airplane
- User with admin permission can create/update/retrieve/delete airplanes.
- User who is authenticated can retrieve the airplane.
- User who is authenticated can add a star (1-5) to the airplane.

## Airplane type
- User with admin permission can create/update/retrieve/delete airplane type.
- The user who is authenticated can retrieve airplane type.

## Flight
- User with admin permission can create/update/retrieve/delete flight.
- A user who is authenticated can retrieve a flight.

## Order and tickets
- User who is authenticated can create/update/retrieve/delete 
order including a few tickets.

## Payment system:
- Users can pay for orders (functionality with Stripe).

## Filtering system
- The user who is authenticated can filter the next endpoint: 
    - Airport (by name, country, city);
    - Route (by source, destination, distance);
    - Crew (by crew position);
    - Airplane (by name, rows, seats in row, airplane type);
    - Flight (by route, airplane, departure time, arrival time);
    - Order (by created at).

## API Permissions:
- Only authenticated users can perform actions such as creating orders/tickets and adding stars to the airplane.
- User with admin permission can create/update/retrieve/delete user profile, airport, route, crew, flight, 
airplane, airplane type, tickets, order, ratings.
- Users can update their own profile.

## API Documentation:
- The API is well-documented with clear instructions on how to use each endpoint.
- The documentation includes sample API requests and responses for different endpoints.

## Tests
- You can test the next endpoint:
  - Airport;
  - Route;
  - Crew;
  - Airplane;
  - Flight;

## How to install using GitHub

- Clone this repository
- Create venv: python -m venv venv
- Activate venv: source venv/bin/activate
- Install requirements: pip install -r requirements.txt
- Run: python manage.py runserver
- Create user via: user/register
- Get access token via: user/token

## Diagram of all models:

![airport_airplane](https://github.com/kostya-kononenko/AIRPORT_SERVICE_API/assets/107486491/0a706f16-5373-456c-8f8c-e8d25c63a6f7)
