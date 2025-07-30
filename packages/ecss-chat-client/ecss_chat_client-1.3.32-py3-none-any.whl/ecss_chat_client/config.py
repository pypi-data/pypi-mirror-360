import configparser


class Settings:
    def __init__(self, server, config_file):
        self.config = configparser.ConfigParser()
        self.config_file = config_file
        self.config.server = server
        self.load_settings()

    def load_settings(self):
        self.config.read(self.config_file)

    def get(self, section, key, fallback=None):
        return self.config.get(section, key, fallback=fallback)

    def write(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def set(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))

    def save(self, section, key, value):
        self.set(section, key, value)
        self.write()

    @property
    def server(self):
        return self.get('API', 'server')

    @property
    def offset(self):
        return self.get('API', 'offset')

    @property
    def count(self):
        return self.get('API', 'count')

    @property
    def logging_level(self):
        return self.get('LOGGING', 'level')

    @property
    def debug_mode(self):
        return self.get('LOGGING', 'debug_mode')
