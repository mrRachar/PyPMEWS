import functools, inspect

def typed(function):
    accepts = dict(function.__annotations__)
    returns = accepts.pop('return') if 'return' in accepts else None

    @functools.wraps(function)
    def wrapper(*args, **kargs):
        for value, argument in zip(args, inspect.getfullargspec(function)[0]):
            if argument in accepts and not isinstance(value, accepts[argument]):
                acceptedtype = accepts[argument].__name__ if not isinstance(accepts[argument], tuple) else ', '\
                    .join(argtype.__name__ for argtype in accepts[argument])
                raise TypeError('Argument {} expected to be of type {} but instead recieved instance of type {}'.format(argument,
                                                                                                                        acceptedtype,
                                                                                                                        type(value).__name__))
        for argument, value in kargs.items():
            if argument in accepts and not isinstance(value, accepts[argument]):
                acceptedtype = accepts[argument].__name__ if not isinstance(accepts[argument], tuple) else ', '\
                    .join(argtype.__name__ for argtype in accepts[argument])
                raise TypeError('Argument {} expected to be of type {} but instead recieved instance of type {}'.format(argument,
                                                                                                                        acceptedtype,
                                                                                                                        type(value).__name__))
        result = function(*args, **kargs)
        if returns is not None and not isinstance(result, returns):
            raise ResultTypeError(returns, type(result))
        return result
    return wrapper

class ResultTypeError(TypeError):
    '''Raised when a function return is of the wrong type'''
    def __init__(self, expected, received):
        expected = expected.__name__ if not isinstance(expected, tuple) else ', '.join(returntype.__name__ for returntype in expected)
        received = received.__name__
        self.value = 'Expected result to be of type {} but instead tried to return instance of type {}'.format(expected, received)

    def __str__(self):
        return self.value