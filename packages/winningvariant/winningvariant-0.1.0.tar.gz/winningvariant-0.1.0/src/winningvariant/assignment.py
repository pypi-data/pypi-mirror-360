class Assignment:
    """An immutable assignment of a subject to a variant in an experiment."""
    
    def __init__(self, subject_id: str, experiment_id: str, variant: str):
        """Initialize an Assignment object.
        
        :param subject_id: The ID of the subject assigned to the variant.
        :param experiment_id: The ID of the experiment the subject is assigned to.
        :param variant: The variant the subject is assigned to.
        """
        self.__subject_id = subject_id
        self.__experiment_id = experiment_id.upper()
        self.__variant = variant.upper()
    
    @property
    def subject_id(self) -> str:
        """Get the subject ID."""
        return self.__subject_id
    
    @property
    def experiment_id(self) -> str:
        """Get the experiment ID."""
        return self.__experiment_id
    
    @property
    def variant(self) -> str:
        """Get the variant."""
        return self.__variant
    
    def is_variant(self, variant: str) -> bool:
        """Check if the assignment's variant matches the provided variant.
        
        :param variant: The variant to check against.
        :return: True if the assignment's variant matches the provided variant, False otherwise.
        """
        return self.__variant == variant.upper()

    def __str__(self) -> str:
        """Get the string representation of the assignment."""
        return f"Assignment(subject_id={self.__subject_id}, experiment_id={self.__experiment_id}, variant={self.__variant})"
      
    def __eq__(self, other: object) -> bool:
        """Check if the assignment is equal to another object or variant string.
        
        :param other: The object to check against, either an Assignment or a string.
        :return: True if the assignment is equal to the other object, False otherwise.
        """
        if isinstance(other, Assignment):
            return (self.__subject_id == other.__subject_id and 
                   self.__experiment_id == other.__experiment_id and 
                   self.__variant == other.__variant)
        elif isinstance(other, str):
            return self.__variant == other.upper()
        return False
