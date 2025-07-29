from .config_chapter import ConfigChapter


class Publisher(ConfigChapter):
    def __init__(self, author, company):
        self._author = author
        self._company = company

    @classmethod
    def from_yaml(cls, input_dict):
        if input_dict is None:
            return Publisher(None, None)

        publisher = Publisher(input_dict.get('author'), input_dict.get('company'))
        ConfigChapter.validate(input_dict, validation_file='publisher_schema.json')
        return publisher

    @property
    def author(self):
        return self._author

    @property
    def company(self):
        return self._company
