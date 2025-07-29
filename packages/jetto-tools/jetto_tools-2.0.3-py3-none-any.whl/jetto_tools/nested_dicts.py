import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _gen_dict_extract(var, key, verbosity=0):
    """ Find keys in deeply nested structures
    From https://stackoverflow.com/a/60261620/3613853
    Best performance from tested implementations
    Adjusted for Python3 duck-typing style

    Args:
      - var: The variable to search in. Recurses deeper inward.
      - key: The key to search for

    Kwargs:
      - verbosity: Verbosity of this function [0-inf]

    Yields:
      - result: The found fields matching the key
    """
    if verbosity >= 3:
        logger.setLevel(logging.TRACE)
    elif verbosity >= 2:
        logger.setLevel(logging.DEBUG)
    elif verbosity >= 1:
        logger.setLevel(logging.INFO)
    elif verbosity >= 0:
        logger.setLevel(logging.WARNING)

    if hasattr(var, 'items'):
        for kk, vv in var.items():
            logger.trace('Checking key={!r} of {!s}'.format(kk, type(vv)))
            if kk == key:
                logger.debug('Yielding key {!r} of {!s}'.format(kk, type(vv)))
                yield vv
            else:
                logger.trace('Key not found, recurse into key={!r}'.format(kk))

            # This is not the key, recurse
            if hasattr(vv, 'items'):
                # We have items, probably a dict or something
                for result in _gen_dict_extract(vv, key, verbosity=verbosity):
                    yield result
            elif isinstance(vv, list):
                # We do not have items, try to loop normally
                for el in vv:
                    for result in _gen_dict_extract(key, el, verbosity=verbosity):
                        yield result
