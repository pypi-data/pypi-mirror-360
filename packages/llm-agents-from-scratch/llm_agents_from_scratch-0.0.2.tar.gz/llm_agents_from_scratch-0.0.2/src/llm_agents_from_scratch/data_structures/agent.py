"""Data Structures for LLM Agent."""

from pydantic import BaseModel, Field


class Task(BaseModel):
    """Represents a single task with an instruction.

    Attributes:
        instruction: The instruction for the task.
    """

    instruction: str


class TaskStep(BaseModel):
    """Represents a step within a task and its own instruction.

    Attributes:
        instruction: The instruction for the task.
    """

    instruction: str = Field(
        description="The instruction for this step in the task.",
    )
    last_step: bool = Field(
        description=(
            "Whether or not this task step should be the final one "
            "because there is enough context to complete the overall task."
        ),
    )


class TaskStepResult(BaseModel):
    """The result of a task step execution.

    Attributes:
        task_step: The `TaskStep` that was executed.
        content: The content results of the execution.
        last_step: Whether or not the step was the final step for the parent
            Task.
    """

    task_step: TaskStep
    content: str | None


class TaskResult(BaseModel):
    """The result of the task execution.

    Attributes:
        task: The `Task` that was executed.
        content: The content results of the task execution.
        rollout: The rollout of the task execution.
        error: Whether or not the execution resulted in an error.
    """

    task: Task
    content: str
    rollout: str
    error: bool = False
