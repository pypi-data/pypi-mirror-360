import pytest
from src.winningvariant._internal import has_valid_args, get_subject_id, get_experiment_id


class TestHasValidArgs:
    def test_both_subject_id_and_subject_arg_raises_error(self):
        """Test that providing both subject_id and subject_arg raises ValueError."""
        result = has_valid_args(subject_id="user123", subject_arg="user_id")
        assert isinstance(result, ValueError)
        assert str(result) == "Either subject_id or subject_arg must be provided, not both"

    def test_both_experiment_id_and_experiment_arg_raises_error(self):
        """Test that providing both experiment_id and experiment_arg raises ValueError."""
        result = has_valid_args(experiment_id="exp1", experiment_arg="exp_id")
        assert isinstance(result, ValueError)
        assert str(result) == "Either experiment_id or experiment_arg must be provided, not both"

    def test_no_subject_raises_error(self):
        """Test that providing no subject raises ValueError."""
        result = has_valid_args(experiment_id="exp1")
        assert isinstance(result, ValueError)
        assert str(result) == "Either subject_id or subject_arg must be provided"

    def test_no_experiment_raises_error(self):
        """Test that providing no experiment raises ValueError."""
        result = has_valid_args(subject_id="user123")
        assert isinstance(result, ValueError)
        assert str(result) == "Either experiment_id or experiment_arg must be provided"

    def test_subject_id_and_experiment_id_valid(self):
        """Test that providing subject_id and experiment_id returns True."""
        result = has_valid_args(subject_id="user123", experiment_id="exp1")
        assert result is True

    def test_subject_arg_and_experiment_arg_valid(self):
        """Test that providing subject_arg and experiment_arg returns True."""
        result = has_valid_args(subject_arg="user_id", experiment_arg="exp_id")
        assert result is True

    def test_mixed_args_valid(self):
        """Test that providing subject_id and experiment_arg returns True."""
        result = has_valid_args(subject_id="user123", experiment_arg="exp_id")
        assert result is True

    def test_mixed_args_valid_swapped(self):
        """Test that providing subject_arg and experiment_id returns True."""
        result = has_valid_args(subject_arg="user_id", experiment_id="exp1")
        assert result is True


class TestGetSubjectId:
    def test_get_subject_id_from_subject_id(self):
        """Test getting subject_id when subject_id is provided."""
        result = get_subject_id({}, subject_id="user123")
        assert result == "user123"

    def test_get_subject_id_from_subject_arg(self):
        """Test getting subject_id from kwargs when subject_arg is provided."""
        kwargs = {"user_id": "user456"}
        result = get_subject_id(kwargs, subject_arg="user_id")
        assert result == "user456"

    def test_get_subject_id_missing_subject_arg_raises_error(self):
        """Test that missing subject_arg in kwargs raises ValueError."""
        kwargs = {}
        with pytest.raises(ValueError, match="Missing subject argument 'user_id'"):
            get_subject_id(kwargs, subject_arg="user_id")

    def test_get_subject_id_no_args_raises_error(self):
        """Test that providing no subject_id or subject_arg raises ValueError."""
        with pytest.raises(ValueError, match="Either subject_id or subject_arg must be provided"):
            get_subject_id({})


class TestGetExperimentId:
    def test_get_experiment_id_from_experiment_id(self):
        """Test getting experiment_id when experiment_id is provided."""
        result = get_experiment_id({}, experiment_id="exp1")
        assert result == "exp1"

    def test_get_experiment_id_from_experiment_arg(self):
        """Test getting experiment_id from kwargs when experiment_arg is provided."""
        kwargs = {"exp_id": "exp2"}
        result = get_experiment_id(kwargs, experiment_arg="exp_id")
        assert result == "exp2"

    def test_get_experiment_id_missing_experiment_arg_raises_error(self):
        """Test that missing experiment_arg in kwargs raises ValueError."""
        kwargs = {}
        with pytest.raises(ValueError, match="Missing experiment argument 'exp_id'"):
            get_experiment_id(kwargs, experiment_arg="exp_id")

    def test_get_experiment_id_no_args_raises_error(self):
        """Test that providing no experiment_id or experiment_arg raises ValueError."""
        with pytest.raises(ValueError, match="Either experiment_id or experiment_arg must be provided"):
            get_experiment_id({})
