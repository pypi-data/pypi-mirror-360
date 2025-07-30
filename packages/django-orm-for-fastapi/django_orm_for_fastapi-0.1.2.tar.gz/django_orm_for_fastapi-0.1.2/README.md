# Django ORM for FastAPI

This project aim is provide easy integration of Django's ORM into FastAPI applications.

## Currently implemented

- Ability to configure single database connection
- Ability to define Django models and use them in FastAPI endpoints
- Simple endpoint decorator for closing unused connections
- Utilities 
  - Function that will create model's tables
  - Function that will delete model's tables
- Test utils
  - Function that will create test database 
  - Function that will tear-down test database
  - Function that will flush test database tables

## Todo

- Migrations
- Support for multiple databases
- Transactional test utilities (so `flush`ing won't be needed)
- Tests
