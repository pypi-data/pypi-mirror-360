class StepNameConflictError(Exception):
    """
    Exception raised when a step with the same name already exist
    """

    def __init__(self, message="Step with the same name already exist"):
        self.message = message
        super().__init__(self.message)


class CoreStepAlreadySetError(Exception):
    """
    Exception raised when the core step is already set
    """

    def __init__(self, message="Core step is already set"):
        self.message = message
        super().__init__(self.message)


class CoreStepNotSetError(Exception):
    """
    Exception raised when the core step is not set
    """

    def __init__(self, message="Core step is not set"):
        self.message = message
        super().__init__(self.message)


class StepNotDefinedError(Exception):
    """
    Exception raised when a step is not defined
    """

    def __init__(self, message="Step is not defined"):
        self.message = message
        super().__init__(self.message)


class CircularStepDefinitionError(Exception):
    """
    Exception raised when a step is defined circularly
    """

    def __init__(self, message="Circular step definition"):
        self.message = message
        super().__init__(self.message)


class StepBranchingCannotBeUsedWithoutNextStepError(Exception):
    """
    Exception raised when a step is defined as branching but without next step
    """

    def __init__(self, message="Step cannot be defined as branching without next step"):
        self.message = message
        super().__init__(self.message)
    #     self.message = message
    
class InvalidAppError(Exception):
    """Custom exception for invalid app configurations."""
    def __init__(self, message: str = "Invalid app configuration"):
        super().__init__(message)
        self.message = message
        