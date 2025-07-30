"""Defines the base logic for creation a math exercises."""

import logging
from typing import Any, ClassVar, Type

from pydantic import ValidationError

from wse_exercises.base.components import TextAnswer, TextQuestion

from ..enums import MathExercise
from ..exceptions import OperandGeneratorError
from ..task import SimpleCalcTask
from .components import SimpleCalcConditions, SimpleCalcConfig
from .services import OperandGenerator
from .task_factory import SimpleCalcFactory

logger = logging.getLogger(__name__)


class SimpleCalcExercise:
    """Defines a base logic of simple calculation exercise creation.

    Control exercise task creation with:
    - `task_factory`, create question and answer for exercise type;
    - `operand_generator`, get random or exact calculation operands;
    - `config`, set min and max calculation operand value range for
       random generator or as exact operands.
    """

    exercise_name: ClassVar[MathExercise]
    task_factory: ClassVar[Type[SimpleCalcFactory]]

    def __init__(
        self,
        operand_generator: OperandGenerator,
        config: SimpleCalcConfig | dict[str, Any] | None = None,
    ) -> None:
        """Construct the task creation."""
        # Initialize exercise config
        try:
            # Automatic conversion of dictionaries
            # and other types into a model
            self._config = (
                SimpleCalcConfig.parse_obj(config)
                if config is not None
                else SimpleCalcConfig()
            )
        except ValidationError as e:
            logger.error(f'Invalid exercise config: {e.errors()}')
            logger.info('Using default configuration')
            self._config = SimpleCalcConfig()

        # Set up operand generator
        self._operand_generator = operand_generator

    def create_task(
        self,
        config: SimpleCalcConfig | dict[str, Any] | None = None,
    ) -> SimpleCalcTask:
        """Create simple calculation task."""
        self._set_configuration(config)
        self._generate_operands()
        self._create_components()
        task_dto = self._create_task_dto()
        return task_dto

    # Utility methods

    def _set_configuration(
        self,
        config: SimpleCalcConfig | dict[str, Any] | None,
    ) -> None:
        """Update exercise configuration with validation."""
        if config is not None:
            try:
                self._config = SimpleCalcConfig.parse_obj(config)
            except ValidationError as e:
                logger.error(f'Invalid configuration update: {e.errors()}')
        # If config is None, keep existing configuration.
        self._init_value_range()

    def _init_value_range(self) -> None:
        self._min_value = self._config.min_value
        self._max_value = self._config.max_value

    def _generate_operands(self) -> None:
        """Generate task operands."""
        self._operand_generator.set_values(self._min_value, self._max_value)
        try:
            self._operand_1 = self._operand_generator.generate()
            self._operand_2 = self._operand_generator.generate()
        except OperandGeneratorError as e:
            logger.error(
                'Operand generation failed: %s. '
                'Using fallback values: min_value=%d, max_value=%d',
                str(e),
                self._min_value,
                self._max_value,
            )
            # Fallback to minimal possible values
            # to keep system operational
            self._operand_1 = self._min_value
            self._operand_2 = self._min_value

        except Exception as e:
            logger.critical(
                'Unexpected error during operand generation: %s',
                str(e),
                exc_info=True,
            )
            # Critical fallback to prevent complete failure
            self._operand_1 = 1
            self._operand_2 = 1

    def _create_components(self) -> None:
        """Create simple math task component DTO (question/answer)."""
        self._question = self.task_factory.create_question(
            self._operand_1, self._operand_2
        )
        self._answer = self.task_factory.create_answer(
            self._operand_1, self._operand_2
        )

    def _create_task_dto(self) -> SimpleCalcTask:
        """Create simple math task Data Transfer Object."""
        return SimpleCalcTask(
            config=SimpleCalcConfig(
                min_value=self._min_value,
                max_value=self._max_value,
            ),
            conditions=SimpleCalcConditions(
                operand_1=self._operand_1,
                operand_2=self._operand_2,
            ),
            question=TextQuestion(text=self._question),
            answer=TextAnswer(text=self._answer),
            exercise_name=self.exercise_name,
        )
