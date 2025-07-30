import functools
from time import sleep

def ziaretry(fn):

    @functools.wraps(fn)
    def __retry(*args, **kwargs):

        retries = kwargs.get("zia_retries", 3)
        if not isinstance(retries, int):
            retries = 3

        # remove the zia_retries param from the kwargs
        kwargs.pop("zia_retries", None)

        tries = 0
        while tries < retries+1:
            try:
                return fn(*args, **kwargs)
            except ApiException as ex:

                tries += 1
                retry_after = ex.headers.get("Retry-After")

                # have done max number of retries
                if tries == retries:
                    raise

                # try after delay
                elif retry_after is not None:

                    if not isinstance(retry_after, float):
                        try:
                            retry_after = float(retry_after)
                        except ValueError:
                            raise ValueError(f"invalid Retry-After header value: {retry_after}")

                    sleep(retry_after)

                # no retry header
                else:
                    raise

    return __retry