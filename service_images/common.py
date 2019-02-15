import logging
class ApiError(Exception):
    """ Adds to error optional _details_ and may be _http_code_"""

    def __init__(self, original_message, details=None, http_code=None):
        Exception.__init__(self)
        self.message = f'{original_message}: "{details}"' if details else original_message
        if http_code:
            self.http_code_str = f'http_code: {http_code}, '
        else:
            self.http_code_str = ''

    def __str__(self):
        return '{}{}'.format(self.http_code_str, self.message)