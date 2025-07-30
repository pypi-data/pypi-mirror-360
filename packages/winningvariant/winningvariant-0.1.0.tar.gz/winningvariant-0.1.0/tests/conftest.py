import pytest
from src.winningvariant import WinningVariantClient
from snowflake.snowpark.session import Session
from snowflake.snowpark.functions import udf, col
from snowflake.snowpark.types import StructType, StructField, IntegerType, StringType, TimestampType

def pytest_addoption(parser):
    parser.addoption("--snowflake-session", action="store", default="live")

@pytest.fixture
def client(request) -> WinningVariantClient:
    if request.config.getoption('--snowflake-session') == 'local':
        s = Session.builder.config('local_testing', True).create()

        # Load test data into "stage"
        s.file.put("tests/testdata/assignments.csv", "@mystage", auto_compress=False)
        schema = StructType(
            [
                StructField("id", StringType()),
                StructField("subject_id", StringType()),
                StructField("experiment_id", StringType()),
                StructField("variant_id", StringType()),
                StructField("cohort_index", IntegerType()),
                StructField("created_at", TimestampType()),
            ]
        )

        df = s.read.schema(schema).option("SKIP_HEADER", 1).csv("@mystage/assignments.csv")
        df.write.save_as_table("experimentation.assignments")

        # Register a mock UDF
        @udf(name='experimentation.create_assignment', return_type=StringType(), input_types=[StringType(), StringType()])
        def create_assignment(subject_id, experiment_id):
            # Try to get the assignment from the test dataframe
            assignment = (
                s.table("experimentation.assignments")
                .filter((col("subject_id") == subject_id) & (col("experiment_id") == experiment_id))
                .select("variant_id")
                .limit(1)
                .collect()
            )
            return assignment[0]["VARIANT_ID"].upper() if assignment and len(assignment) == 1 else "NEW_ASSIGNMENT"
    # else:
    #     s = Session.builder.configs(CONNECTION_PARAMETERS).create()

    return WinningVariantClient(session=s, verbose=True, cache=False)