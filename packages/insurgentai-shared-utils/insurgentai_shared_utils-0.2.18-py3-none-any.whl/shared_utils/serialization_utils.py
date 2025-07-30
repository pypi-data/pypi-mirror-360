from functools import wraps

def deserialize_event(contract_class):
    """
    Decorator to deserialize event data into an event contract class instance.
    """
    def decorator(callback_fn):
        @wraps(callback_fn)
        def wrapper(event_data):
            try:
                obj = contract_class(**event_data)
            except Exception as e:
                print(f"Deserialization failed for {contract_class.__name__}: {e}")
                return
            return callback_fn(obj)
        return wrapper
    return decorator