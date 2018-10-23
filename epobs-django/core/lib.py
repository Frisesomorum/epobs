from django.urls import reverse


class QueryStringArg:
    url_arg = ''
    queryset_arg = ''
    display_name = ''
    default = None
    type = None
    model = None

    def __init__(self, url_arg, queryset_arg, display_name=None, default=None, type=None, model=None):
        self.url_arg = url_arg
        self.queryset_arg = queryset_arg
        if display_name is not None:
            self.display_name = display_name
        else:
            self.display_name = self.url_arg.translate(str.maketrans('_', ' ')).title()
        self.default = default
        self.type = type
        self.model = model


class QueryStringParam:
    argument = None
    value = None
    skip = False

    def __init__(self, argument, value=None):
        self.argument = argument
        if value is None:
            value = argument.default
        if value == 'all':
            self.skip = True
        if argument.type is not None:
            if argument.type == bool:
                value = int(value)
            value = argument.type(value)
        if argument.model is not None:
            value = argument.model.objects.get(pk=value)
        self.value = value

    @property
    def display(self):
        return '{0}: {1}'.format(self.argument.display_name, self.value)


def querystring_url(url_name, params):
    url = reverse(url_name)
    query_list = []
    for arg in params.keys():
        query_list.append('{0}={1}'.format(arg, params[arg]))
    query_str = '&'.join(query_list)
    if len(query_str) > 0:
        url = '{0}?{1}'.format(url, query_str)
    return url
