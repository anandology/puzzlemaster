
def listget(list_, index, default=None):
    if index < len(list_):
        return list_[index]
    else:
        return default