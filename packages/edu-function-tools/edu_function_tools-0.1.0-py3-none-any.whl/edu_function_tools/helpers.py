from abc import (
    ABCMeta,
)

from function_tools.helpers import (
    BaseFunctionHelper,
    BaseRunnerHelper,
)

from edu_function_tools.caches import (
    EduFunctionCacheStorage,
    EduRunnerCacheStorage,
)


class EduRunnerHelper(BaseRunnerHelper, metaclass=ABCMeta):
    """Базовый класс помощников для исполнителей функций.
    
    Предоставляет вспомогательную функциональность для исполнителей,
    включая:
    - Кэширование данных исполнителя
    - Общие утилиты для работы с функциями
    - Доступ к разделяемым ресурсам
    
    Attributes:
        cache (EduRunnerCacheStorage): Хранилище кэша для исполнителя
    """

    def _prepare_cache_class(self) -> type[EduRunnerCacheStorage]:
        """Возвращает класс хранилища кэша для исполнителя.
        
        Returns:
            type[EduRunnerCacheStorage]: Класс для кэширования данных
            исполнителя
        """
        return EduRunnerCacheStorage


class EduFunctionHelper(BaseFunctionHelper, metaclass=ABCMeta):
    """Базовый класс помощников для функций обработки данных.
    
    Предоставляет вспомогательную функциональность для функций,
    включая:
    - Кэширование данных функции
    - Общие утилиты для обработки данных
    - Доступ к разделяемым ресурсам
    
    Note:
        Каждая конкретная функция может расширить этот класс,
        добавив специфичные для неё вспомогательные методы.
    
    Attributes:
        cache (EduFunctionCacheStorage): Хранилище кэша для функции
    """

    def _prepare_cache_class(self) -> type[EduFunctionCacheStorage]:
        """Возвращает класс хранилища кэша для функции.
        
        Returns:
            type[EduFunctionCacheStorage]: Класс для кэширования данных
            функции
        """
        return EduFunctionCacheStorage
