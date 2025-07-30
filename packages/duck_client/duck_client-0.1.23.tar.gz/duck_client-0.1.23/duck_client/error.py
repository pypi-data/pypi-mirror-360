class DBError(Exception):
    pass

class DBReadOnlyError(DBError):
    pass
