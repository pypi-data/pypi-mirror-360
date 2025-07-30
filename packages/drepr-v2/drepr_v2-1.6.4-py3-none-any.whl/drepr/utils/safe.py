def safe_item_getter(collection, item, msg):
    try:
        return collection[item]
    except Exception as e:
        raise Exception(msg) from e


def safe_range(collection, item, msg):
    try:
        return range(collection, item, item)
    except Exception as e:
        raise Exception(msg) from e


def safe_len(collection, msg):
    try:
        return len(collection)
    except Exception as e:
        raise Exception(msg) from e
