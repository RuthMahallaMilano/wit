class WitError(Exception):
    pass


class FilesDoesntMatchError(WitError):
    pass


class BranchDoesntExistError(WitError):
    pass


class WitExistsError(WitError):
    pass
