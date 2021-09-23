
class FileCache:
    def __init__(self, dnac, logging):
        self.logging = logging
        self._cache = {}
        logging.debug("Initializing file cache")
        LIMIT=500
        offset = 1
        while True:
            files = dnac.file.get_list_of_files(name_space="config",offset=offset, limit=LIMIT)
            logging.debug("offset {}, limit {}, got {}".format(offset, LIMIT, len(files.response)))
            if files.response == []:
                break
            for file in files.response:
                logging.debug("Caching {}".format(file.name))
                self._cache[file.name] =  file
            offset += LIMIT
    def lookup(self,name):
        if name in self._cache:
            self.logging.debug("Found file:{}".format(name))
            return self._cache[name]
        else:
            return None
