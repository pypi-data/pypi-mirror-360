from hyrrokkin_engine.persistence_interface import PersistenceInterface

class Persistence(PersistenceInterface):

    def __init__(self):
        self.target_id = None
        self.target_type = None

    def configure(self, target_id, target_type):
        self.target_id = target_id
        self.target_type = target_type

    @staticmethod
    def check_valid_data_key(key):
        for c in key:
            if not c.isalnum() and c != '_':
                raise ValueError("data key can only contain alphanumeric characters and underscores")

    @staticmethod
    def check_valid_data_value(data):
        if data is None:
            return True
        return isinstance(data, bytes)