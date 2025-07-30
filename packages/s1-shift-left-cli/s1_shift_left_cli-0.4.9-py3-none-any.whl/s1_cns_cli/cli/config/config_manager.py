class ConfigManager:
    def __init__(self, config):
        self.__global = config["global"]
        self.__secret = config["secret"]
        self.__iac = config["iac"]
        self.__vuln = config["vuln"]

    def get_global(self):
        return self.__global

    def get_secret(self):
        return self.__secret

    def get_iac(self):
        return self.__iac

    def get_vuln(self):
        return self.__vuln

    def set_global(self, key, value):
        self.__global[key] = value

    def set_secret(self, key, value):
        self.__secret[key] = value

    def set_iac(self, key, value):
        self.__iac[key] = value

    def set_vuln(self, key, value):
        self.__vuln[key] = value
