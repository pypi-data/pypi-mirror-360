import pytest
from src.winningvariant import Assignment, SnowflakeExecutionError

def test_get_assignment_returns_none(client):
    variant = client.get_assignment("user_123", "exp_2")
    assert variant is None

def test_get_assignment_returns_variant(client):
    variant = client.get_assignment("user_123", "exp_1")
    assert variant == "TREATMENT-A"
    assert variant.subject_id == "user_123"
    assert variant.experiment_id == "EXP_1"
    assert variant.variant == "TREATMENT-A"

def test_get_assignment_exception(client, monkeypatch):
    monkeypatch.setattr(client, "get_assignment_sql", lambda s, e: (_ for _ in ()).throw(Exception("Snowflake error")))
    with pytest.raises(SnowflakeExecutionError, match="Failed to fetch assignment"):
        client.get_assignment("user_123", "exp_2")

def test_get_assignment_sql_cached_results(client):
    client.enable_cache()
    
    # First call should hit the database
    assert client.get_assignment_sql("user_123", "exp_1") == "TREATMENT-A"

    # Second call should hit the cache
    assert client.get_assignment_sql("user_123", "exp_1") == "TREATMENT-A"

    client.disable_cache()

    # Third call should hit the database again
    assert client.get_assignment_sql("user_123", "exp_1") == "TREATMENT-A"

def test_create_assignment_on_existing_returns_variant(client):
    variant = client.create_assignment("user_456", "exp_1")
    assert variant == "CONTROL"
    assert variant.subject_id == "user_456"
    assert variant.experiment_id == "EXP_1"
    assert variant.variant == "CONTROL"

def test_create_assignment_on_new_returns_variant(client):
    variant = client.create_assignment("user_789", "exp_1")
    assert variant == "NEW_ASSIGNMENT"
    assert variant.subject_id == "user_789"
    assert variant.experiment_id == "EXP_1"
    assert variant.variant == "NEW_ASSIGNMENT"

def test_create_assignment_exception(client, monkeypatch):
    monkeypatch.setattr(client, "create_assignment_sql", lambda s, e: (_ for _ in ()).throw(Exception("Snowflake error")))
    with pytest.raises(SnowflakeExecutionError, match="Failed to create assignment"):
        client.create_assignment("user_123", "exp_2")

def test_check_variant_no_create_true(client, monkeypatch):
    monkeypatch.setattr(client, "get_assignment", lambda s, e: Assignment("user_123", "exp_1", "variant_a"))
    assert client.check_variant("user_123", "exp_1", "variant_a", create_assignment=False) is True

def test_check_variant_no_create_true_case_insensitive(client, monkeypatch):
    monkeypatch.setattr(client, "get_assignment", lambda s, e: Assignment("user_123", "exp_1", "variant_a"))
    assert client.check_variant("user_123", "exp_1", "variant_A", create_assignment=False) is True

def test_check_variant_no_create_false(client, monkeypatch):
    monkeypatch.setattr(client, "get_assignment", lambda s, e: Assignment("user_123", "exp_1", "variant_b"))
    assert client.check_variant("user_123", "exp_1", "variant_a", create_assignment=False) is False

def test_check_variant_create_true(client, monkeypatch):
    monkeypatch.setattr(client, "create_assignment", lambda s, e: Assignment("user_456", "exp_1", "variant_a"))
    assert client.check_variant("user_456", "exp_1", "variant_a", create_assignment=True) is True

def test_check_variant_create_true_case_insensitive(client, monkeypatch):
    monkeypatch.setattr(client, "create_assignment", lambda s, e: Assignment("user_456", "exp_1", "variant_a"))
    assert client.check_variant("user_456", "exp_1", "variant_A", create_assignment=True) is True

def test_create_assignment_sql_cached_results(client):
    client.enable_cache()
    
    # First call should hit the database
    assert client.create_assignment_sql("user_123", "exp_1") == "TREATMENT-A"

    # Second call should hit the cache
    assert client.create_assignment_sql("user_123", "exp_1") == "TREATMENT-A"

    client.disable_cache()

    # Third call should hit the database again
    assert client.create_assignment_sql("user_123", "exp_1") == "TREATMENT-A"

@pytest.mark.asyncio
async def test_async_assignment_decorator(client, monkeypatch):
    monkeypatch.setattr(client, "create_assignment", lambda s, e: Assignment("async_user", "exp_async", "variant_async"))

    @client.assignment(subject_arg="user_id", experiment_id="exp_async")
    async def my_async_func(user_id, assignment=None):
        return f"User {user_id} assigned to {assignment.variant}"

    result = await my_async_func(user_id="async_user")
    assert result == "User async_user assigned to VARIANT_ASYNC"

def test_assignment_decorator_sync(client, monkeypatch):
    monkeypatch.setattr(client, "create_assignment", lambda s, e: Assignment("sync_user", "exp_sync", "variant_sync"))

    @client.assignment(subject_arg="user_id", experiment_id="exp_sync")
    def my_sync_func(user_id, assignment=None):
        return f"User {user_id} assigned to {assignment.variant}"

    result = my_sync_func(user_id="sync_user")
    assert result == "User sync_user assigned to VARIANT_SYNC"

def test_assignment_decorator_sync_missing_subject_at_runtime(client, monkeypatch):
    monkeypatch.setattr(client, "create_assignment", lambda s, e: Assignment("sync_user", "exp_sync", "variant_sync"))

    @client.assignment(subject_arg="user_id", experiment_id="exp_sync")
    def missing_subject_func(user_id, assignment=None):
        return f"User {user_id} assigned to {assignment.variant}"
    
    with pytest.raises(ValueError, match="Missing subject argument 'user_id'"):
        missing_subject_func()

def test_assignment_decorator_missing_subject_at_definition(client):
    with pytest.raises(ValueError, match="Either subject_id or subject_arg must be provided"):
        @client.assignment(experiment_id="e1")
        def missing_subject_func():
            return "should not run"

def test_assignment_decorator_missing_experiment_at_definition(client):
    with pytest.raises(ValueError, match="Either experiment_id or experiment_arg must be provided"):
        @client.assignment(subject_id="s1")
        def missing_experiment_func():
            return "should not run"

def test_assignment_decorator_sync_missing_experiment_at_runtime(client, monkeypatch):
    monkeypatch.setattr(client, "create_assignment", lambda s, e: Assignment("sync_user", "exp_sync", "variant_sync"))

    @client.assignment(subject_id="user_id", experiment_arg="exp_sync")
    def missing_experiment_func(user_id, assignment=None):
        return f"User {user_id} assigned to {assignment.variant}"
    
    with pytest.raises(ValueError, match="Missing experiment argument 'exp_sync'"):
        missing_experiment_func()

def test_if_assignment_decorator_true(client, monkeypatch):
    monkeypatch.setattr(client, "get_assignment", lambda s, e: Assignment("s1", "e1", "v1"))

    @client.if_assignment("v1", subject_id="s1", experiment_id="e1", create_assignment=False)
    def visible_func():
        return "visible"

    assert visible_func() == "visible"

def test_if_assignment_decorator_false(client, monkeypatch):
    monkeypatch.setattr(client, "get_assignment", lambda s, e: Assignment("s1", "e1", "v1"))

    @client.if_assignment("v2", subject_id="s1", experiment_id="e1", create_assignment=False)
    def hidden_func():
        return "should not run"

    assert hidden_func() is None

def test_if_assignment_decorator_missing_subject_at_definition(client):
    with pytest.raises(ValueError, match="Either subject_id or subject_arg must be provided"):
        @client.if_assignment("v1", experiment_id="e1", create_assignment=False)
        def missing_subject_func():
            return "should not run"

def test_if_assignment_decorator_missing_experiment_at_definition(client):
    with pytest.raises(ValueError, match="Either experiment_id or experiment_arg must be provided"):
        @client.if_assignment("v1", subject_id="s1", create_assignment=False)
        def missing_experiment_func():
            return "should not run"

def test_unless_assignment_decorator_true(client, monkeypatch):
    monkeypatch.setattr(client, "get_assignment", lambda s, e: Assignment("s1", "e1", "v2"))

    @client.unless_assignment("v1", subject_id="s1", experiment_id="e1", create_assignment=False)
    def visible_func():
        return "visible"

    assert visible_func() == "visible"

def test_unless_assignment_decorator_false(client, monkeypatch):
    monkeypatch.setattr(client, "get_assignment", lambda s, e: Assignment("s1", "e1", "v1"))

    @client.unless_assignment("v1", subject_id="s1", experiment_id="e1", create_assignment=False)
    def hidden_func():
        return "should not run"

    assert hidden_func() is None

def test_unless_assignment_decorator_missing_subject_at_definition(client):
    with pytest.raises(ValueError, match="Either subject_id or subject_arg must be provided"):
        @client.unless_assignment("v1", experiment_id="e1", create_assignment=False)
        def missing_subject_func():
            return "should not run"

def test_unless_assignment_decorator_missing_experiment_at_definition(client):
    with pytest.raises(ValueError, match="Either experiment_id or experiment_arg must be provided"):
        @client.unless_assignment("v1", subject_id="s1", create_assignment=False)
        def missing_experiment_func():
            return "should not run"