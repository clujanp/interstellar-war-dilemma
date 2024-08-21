from abc import ABC, abstractmethod


class AbstractRepository(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def create_table(self, table_name, columns):
        pass

    @abstractmethod
    def insert(self, table_name, data):
        pass

    @abstractmethod
    def update(self, table_name, data, condition):
        pass

    @abstractmethod
    def delete(self, table_name, condition):
        pass

    @abstractmethod
    def select(self, table_name, condition=None):
        pass
