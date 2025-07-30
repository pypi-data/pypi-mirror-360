
class HuiBiaoException(Exception):
    pass


def FolderResourceAlreadyExistException(path: str) -> HuiBiaoException:
    return HuiBiaoException(f"Folder resource already exist: {path}!")


