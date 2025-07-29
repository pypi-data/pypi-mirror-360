"""Базовые классы функций для интеграции с продуктами Образования.

Этот модуль содержит базовые классы функций, которые используются для создания
конкретных реализаций функций обработки данных в системе. Модуль предоставляет
различные варианты базовых классов с разными стратегиями сохранения данных
и управления очередями объектов.
"""

from abc import (
    ABCMeta,
)

from function_tools.functions import (
    BaseFunction,
    LazySavingPredefinedQueueFunction,
    LazySavingPredefinedQueueGlobalHelperFunction,
)

from edu_function_tools.helpers import (
    EduFunctionHelper,
)
from edu_function_tools.results import (
    EduFunctionResult,
)
from edu_function_tools.validators import (
    EduFunctionValidator,
)


class EduFunction(BaseFunction, metaclass=ABCMeta):
    """Базовый класс для создания функций продуктов Образования.
    
    Предоставляет основной интерфейс для создания функций обработки данных.
    Наследуется от BaseFunction и добавляет специфичную для продуктов
    Образования функциональность.
    
    Note:
        Этот класс является абстрактным и должен быть расширен конкретными
        реализациями функций.
    """


class EduLazySavingPredefinedQueueFunction(LazySavingPredefinedQueueFunction, metaclass=ABCMeta):
    """Базовый класс для создания функций с отложенным сохранением.
    
    Реализует паттерн отложенного сохранения (lazy saving) с предустановленной
    очередью объектов. Это позволяет:
    - Накапливать объекты для сохранения в течение выполнения функции
    - Сохранять все объекты атомарно после успешного выполнения всех операций
    - Откатывать все изменения в случае ошибки
    - Оптимизировать производительность за счет пакетного сохранения
    
    Attributes:
        helper (EduFunctionHelper): Помощник функции для вспомогательных операций
        validator (EduFunctionValidator): Валидатор для проверки данных
        result (EduFunctionResult): Объект для хранения результатов работы
    """

    def _prepare_helper_class(self) -> type[EduFunctionHelper]:
        """Возвращает класс помощника функции.
        
        Returns:
            type[EduFunctionHelper]: Класс помощника для работы с данными
        """
        return EduFunctionHelper

    def _prepare_validator_class(self) -> type[EduFunctionValidator]:
        """Возвращает класс валидатора функции.
        
        Returns:
            type[EduFunctionValidator]: Класс для валидации входных данных
        """
        return EduFunctionValidator

    def _prepare_result_class(self) -> type[EduFunctionResult]:
        """Возвращает класс результата функции.
        
        Returns:
            type[EduFunctionResult]: Класс для хранения результатов выполнения
        """
        return EduFunctionResult


class EduLazySavingPredefinedQueueGlobalHelperFunction(
    LazySavingPredefinedQueueGlobalHelperFunction,
    metaclass=ABCMeta,
):
    """Базовый класс для создания функций с глобальным помощником.
    
    Расширяет функциональность EduLazySavingPredefinedQueueFunction,
    добавляя поддержку глобального помощника. Это позволяет:
    - Использовать общие вспомогательные методы между разными функциями
    - Кэшировать часто используемые данные на уровне всего приложения
    - Оптимизировать использование ресурсов при массовой обработке данных
    
    Note:
        Глобальный помощник должен быть потокобезопасным, так как может
        использоваться одновременно несколькими функциями.
    """
