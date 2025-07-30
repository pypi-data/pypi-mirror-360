from snowflake.snowpark import Session
from src.winningvariant import WinningVariantClient
from uuid import uuid4

# session = Session.builder.config("connection_name", "myconnection").create()

connection_parameters = {
    "user": "PYTHON_SDK_DEV",
    "password": "eyJraWQiOiIxMTUzMTYwMDY0OTAxMTI2IiwiYWxnIjoiRVMyNTYifQ.eyJwIjoiMTc1OTU4MjcwNjE6MTc1OTU4MjY1NjUiLCJpc3MiOiJTRjoxMDQ5IiwiZXhwIjoxNzUyMTY4MzI5fQ.Sq_wp_QhvqLOQI9rYxNivL3pXvOcMK5LRgiyzZ7sglxPJoIrfB50AxMvswHNrjvLD-mlM8MyEwrxDOSUbAzRzA",
    "account": "VAXTAKL-DEMO",
    "warehouse": "DEMO",
    "database": "WINNING_VARIANT_EXPERIMENTATION"
    # schema="PUBLIC"
}

session = Session.builder.configs(connection_parameters).create()

wv = WinningVariantClient(session, cache=True)

experiment_id = "search-v2"

subject_id = str(uuid4())
print(f"Subject ID: {subject_id}")

# Create a decorated function that uses the subject_id and experiment_id arguments
# and is given the assignment value
@wv.assignment(subject_arg="subject_id", experiment_arg="experiment_id")
def decorated_func_assignment(subject_id, experiment_id, assignment = None):
    return f"Subject {subject_id} assigned to {assignment.variant}"

# Create a decorated function that only runs if the subject is assigned a specific variant
@wv.if_assignment(subject_arg="subject_id", experiment_arg="experiment_id", variant_id = "v2")
def decorated_func_if_var(subject_id, experiment_id):
    return f"Subject {subject_id} is assigned to V2"

# Create a decorated function that only runs if the subject is NOT assigned a specific variant
@wv.unless_assignment(subject_arg="subject_id", experiment_arg="experiment_id", variant_id = "v2")
def decorated_func_unless_var(subject_id, experiment_id):
    return f"Subject {subject_id} is not assigned to V2"

assignment = wv.get_assignment(subject_id=subject_id, experiment_id=experiment_id)
print('Existing assignment:', assignment)

assignment = wv.create_assignment(subject_id=subject_id, experiment_id=experiment_id)
print('New assignment:', assignment)

assignment = wv.get_assignment(subject_id=subject_id, experiment_id=experiment_id)
print('Try retrieving again:', assignment)

print(decorated_func_assignment(subject_id=subject_id, experiment_id=experiment_id))
print('decorated_func_if_var:', decorated_func_if_var(subject_id=subject_id, experiment_id=experiment_id))
print('decorated_func_unless_var:', decorated_func_unless_var(subject_id=subject_id, experiment_id=experiment_id))