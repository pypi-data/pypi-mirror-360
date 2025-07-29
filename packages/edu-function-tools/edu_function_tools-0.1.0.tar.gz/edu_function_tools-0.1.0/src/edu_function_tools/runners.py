"""Исполнители (runners) для функций интеграции с продуктами Образования.

Этот модуль содержит классы исполнителей, которые отвечают за запуск и управление
выполнением функций обработки данных. Исполнители обеспечивают:
- Подготовку и валидацию входных данных
- Управление жизненным циклом функций
- Логирование процесса выполнения
- Обработку результатов и ошибок
"""

from abc import (
    ABCMeta,
)

from educommon import (
    logger,
)
from function_tools.runners import (
    BaseRunner,
    GlobalHelperRunner,
)

from edu_function_tools.helpers import (
    EduRunnerHelper,
)
from edu_function_tools.results import (
    EduRunnerResult,
)
from edu_function_tools.validators import (
    EduRunnerValidator,
)
from edu_rdm_integration.core.consts import (
    LOGS_DELIMITER,
)


class EduRunner(BaseRunner, metaclass=ABCMeta):
    """Базовый класс исполнителей функций продуктов Образования.
    
    Предоставляет основную функциональность для запуска и управления
    выполнением функций обработки данных. Включает:
    - Подготовку и валидацию входных параметров
    - Логирование процесса выполнения
    - Обработку результатов и ошибок
    - Управление очередью выполнения
    
    Attributes:
        helper (EduRunnerHelper): Помощник для вспомогательных операций
        validator (EduRunnerValidator): Валидатор входных данных
        result (EduRunnerResult): Объект для хранения результатов
    """

    def _prepare_helper_class(self) -> type[EduRunnerHelper]:
        """Возвращает класс помощника исполнителя.
        
        Returns:
            type[EduRunnerHelper]: Класс помощника для вспомогательных операций
            при выполнении функций
        """
        return EduRunnerHelper

    def _prepare_validator_class(self) -> type[EduRunnerValidator]:
        """Возвращает класс валидатора исполнителя.
        
        Returns:
            type[EduRunnerValidator]: Класс для валидации входных параметров
            и проверки состояния исполнителя
        """
        return EduRunnerValidator

    def _prepare_result_class(self) -> type[EduRunnerResult]:
        """Возвращает класс результата исполнителя.
        
        Returns:
            type[EduRunnerResult]: Класс для хранения результатов выполнения
            функций и возможных ошибок
        """
        return EduRunnerResult

    def _prepare_runnable_before_enqueue(self, runnable, *args, **kwargs):
        """Подготовка запускаемого объекта перед добавлением в очередь.
        
        Выполняет базовую подготовку объекта и добавляет логирование
        для отслеживания процесса выполнения.
        
        Args:
            runnable: Объект для выполнения
            *args: Дополнительные позиционные аргументы
            **kwargs: Дополнительные именованные аргументы
        """
        super()._prepare_runnable_before_enqueue(runnable, *args, **kwargs)

        logger.info(f'{LOGS_DELIMITER * 2}enqueue {runnable.__class__.__name__}..')


class EduGlobalHelperRunner(GlobalHelperRunner, metaclass=ABCMeta):
    """Базовый класс исполнителей с глобальным помощником.
    
    Расширяет функциональность EduRunner, добавляя поддержку
    глобального помощника. Это позволяет:
    - Использовать общие вспомогательные методы между разными исполнителями
    - Кэшировать часто используемые данные
    - Оптимизировать использование ресурсов
    
    Note:
        Глобальный помощник должен быть потокобезопасным, так как может
        использоваться одновременно несколькими исполнителями.
    
    Attributes:
        helper (EduRunnerHelper): Глобальный помощник для всех исполнителей
        validator (EduRunnerValidator): Валидатор входных данных
        result (EduRunnerResult): Объект для хранения результатов
    """

    def _prepare_helper_class(self) -> type[EduRunnerHelper]:
        """Возвращает класс глобального помощника.
        
        Returns:
            type[EduRunnerHelper]: Класс помощника, который будет использоваться
            всеми исполнителями
        """
        return EduRunnerHelper

    def _prepare_validator_class(self) -> type[EduRunnerValidator]:
        """Возвращает класс валидатора исполнителя.
        
        Returns:
            type[EduRunnerValidator]: Класс для валидации входных параметров
            и проверки состояния исполнителя
        """
        return EduRunnerValidator

    def _prepare_result_class(self) -> type[EduRunnerResult]:
        """Возвращает класс результата исполнителя.
        
        Returns:
            type[EduRunnerResult]: Класс для хранения результатов выполнения
            функций и возможных ошибок
        """
        return EduRunnerResult
