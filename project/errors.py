class WitError(Exception):
    pass


class FilesDoesntMatchError(WitError):
    pass


class BranchDoesntExistError(WitError):
    pass


class BranchExistsError(WitError):
    pass


class WitExistsError(WitError):
    pass


class MergeError(WitError):
    pass


class NoCommonCommitError(WitError):
    pass
