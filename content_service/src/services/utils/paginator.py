from typing import TypeVar

T = TypeVar("T")


class Paginator:
    @staticmethod
    def paginate(items: list[T], page: int, size: int, cls: type[T]) -> list[T]:
        """
        Пагинация списка объектов.

        :param items: полный список элементов
        :param page: номер страницы, начиная с 1
        :param size: размер страницы
        :param cls: класс, в который нужно привести элементы
        :return: список экземпляров cls
        """
        start = (page - 1) * size
        end = start + size
        page_items = items[start:end]

        # если элементы уже экземпляры cls, возвращаем как есть
        if page_items and isinstance(page_items[0], cls):
            return page_items

        # иначе создаём объекты cls из словарей
        return [cls(**item) if isinstance(item, dict) else item for item in page_items]
