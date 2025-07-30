import pytest
from src.winningvariant import Assignment


class TestAssignment:
    def test_assignment_initialization(self):
        """Test that Assignment objects are initialized correctly."""
        assignment = Assignment("user_123", "exp_1", "TREATMENT-A")
        assert assignment.subject_id == "user_123"
        assert assignment.experiment_id == "EXP_1"
        assert assignment.variant == "TREATMENT-A"

    def test_is_variant_true(self):
        """Test that is_variant returns True for matching variant."""
        assignment = Assignment("user_123", "exp_1", "TREATMENT-A")
        assert assignment.is_variant("TREATMENT-A") is True
        assert assignment.is_variant("treatment-a") is True  # Case insensitive

    def test_is_variant_false(self):
        """Test that is_variant returns False for non-matching variant."""
        assignment = Assignment("user_123", "exp_1", "TREATMENT-A")
        assert assignment.is_variant("CONTROL") is False
        assert assignment.is_variant("TREATMENT-B") is False

    def test_str_representation(self):
        """Test the string representation of Assignment."""
        assignment = Assignment("user_123", "exp_1", "TREATMENT-A")
        expected = "Assignment(subject_id=user_123, experiment_id=EXP_1, variant=TREATMENT-A)"
        assert str(assignment) == expected

    def test_equality_same_assignment(self):
        """Test that two identical assignments are equal."""
        assignment1 = Assignment("user_123", "exp_1", "TREATMENT-A")
        assignment2 = Assignment("user_123", "exp_1", "TREATMENT-A")
        assert assignment1 == assignment2

    def test_equality_with_string(self):
        """Test that assignment is equal to a string."""
        assignment = Assignment("user_123", "exp_1", "TREATMENT-A")
        assert assignment == "TREATMENT-A"
        assert assignment != "TREATMENT-B"

    def test_equality_different_subject(self):
        """Test that assignments with different subjects are not equal."""
        assignment1 = Assignment("user_123", "exp_1", "TREATMENT-A")
        assignment2 = Assignment("user_456", "exp_1", "TREATMENT-A")
        assert assignment1 != assignment2

    def test_equality_different_experiment(self):
        """Test that assignments with different experiments are not equal."""
        assignment1 = Assignment("user_123", "exp_1", "TREATMENT-A")
        assignment2 = Assignment("user_123", "exp_2", "TREATMENT-A")
        assert assignment1 != assignment2

    def test_equality_different_variant(self):
        """Test that assignments with different variants are not equal."""
        assignment1 = Assignment("user_123", "exp_1", "TREATMENT-A")
        assignment2 = Assignment("user_123", "exp_1", "CONTROL")
        assert assignment1 != assignment2

    def test_equality_with_non_assignment(self):
        """Test that assignment is not equal to non-Assignment objects."""
        assignment = Assignment("user_123", "exp_1", "TREATMENT-A")
        assert assignment != 123
        assert assignment != None

    def test_case_insensitive_initialization(self):
        """Test that assignment IDs are converted to uppercase."""
        assignment = Assignment("User_123", "Exp_1", "Treatment-A")
        assert assignment.subject_id == "User_123"
        assert assignment.experiment_id == "EXP_1"
        assert assignment.variant == "TREATMENT-A"

    def test_immutability(self):
        """Test that Assignment objects are immutable."""
        assignment = Assignment("user_123", "exp_1", "TREATMENT-A")
        
        # Attempting to modify properties should raise AttributeError
        with pytest.raises(AttributeError):
            assignment.subject_id = "new_user"
        
        with pytest.raises(AttributeError):
            assignment.experiment_id = "new_exp"
        
        with pytest.raises(AttributeError):
            assignment.variant = "new_variant"
