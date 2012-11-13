""":mod:`flask.ext.configlint` --- Flask configuration utilities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import collections

__version__ = '0.9.0'
__all__ = ('ConfigError', 'ConfigKeyError', 'ConfigSchema', 'ConfigTypeError',
           'ConfigVar', 'get_typename')


class ConfigSchema(dict):

    def validate(self, config, manipulate=True):
        """Validates the configuration.

        :param config: the config mapping
        :type config: :class:`collections.Mapping`
        :param manipulate: manipulate the config in place if it's ``True``.
                           default is ``False``
        :type manipulate: :class:`bool`

        """
        if not isinstance(config, collections.Mapping):
            raise TypeError('config must be a mapping object, not ' +
                            repr(config))
        elif manipulate and not isinstance(config, collections.MutableMapping):
            raise TypeError('config must be mutable to manipulate it')
        keys = self.keys()
        keys.sort()
        for key in keys:
            spec = self[key]
            try:
                value = config[key]
            except KeyError:
                if spec.required and all(k not in config for k in spec.alt):
                    raise ConfigKeyError(key, spec)
                continue
            new_value = spec.validate(key, value)
            self[key] = new_value

    def docstring(self, sphinx=False):
        """Generates a docstring for the configuration schema.

        :param sphinx: format for Sphinx if it's ``True``.
                       ``False`` by default
        :type sphinx: :class:`bool`
        :returns: generated docstring
        :rtype: :class:`basestring`

        """
        keys = self.keys()
        keys.sort()
        return '\n' + ''.join(
            self[key].docstring(key, sphinx=sphinx)
            for key in keys
        ) + '\n'


class ConfigVar(object):

    def __init__(self, description=None, cls=None, required=False, alt=[],
                 preprocess=None, element_cls=None, element_preprocess=None):
        if not (description is None or isinstance(description, basestring)):
            raise TypeError('description must be a string, not ' +
                            repr(description))
        elif not (cls is None or isinstance(cls, type) or
                  isinstance(cls, collections.Sequence) and
                  all(isinstance(c, type) for c in cls)):
            raise TypeError('cls must be a type object, not ' + repr(cls))
        elif not (preprocess is None or callable(preprocess)):
            raise TypeError('preprocess must be callable, not ' +
                            repr(preprocess))
        elif not (element_cls is None or isinstance(element_cls, type) or
                  isinstance(element_cls, collections.Sequence) and
                  all(isinstance(c, type) for c in element_cls)):
            raise TypeError('element_cls must be a type object, not ' +
                            repr(element_cls))
        elif not (element_preprocess is None or callable(element_preprocess)):
            raise TypeError('element_preprocess must be callable, not ' +
                            repr(element_preprocess))
        if isinstance(cls, collections.Sequence):
            cls = tuple(cls)
        if isinstance(element_cls, collections.Sequence):
            element_cls = tuple(element_cls)
        self.description = description
        self.cls = cls
        self.required = bool(required)
        self.alt = list(alt)
        self.preprocess = preprocess
        self.element_cls = element_cls
        self.element_preprocess = element_preprocess

    def validate(self, key, value):
        def get_typenames(cls):
            if isinstance(cls, type):
                return get_typename(cls)
            elif len(cls) < 2:
                return get_typename(cls[0])
            names = map(get_typename, cls)
            return ', '.join(names[:-1]) + ', or ' + names[-1]
        if self.preprocess is not None:
            value = self.preprocess(value)
        if self.cls and not isinstance(value, self.cls):
            raise ConfigTypeError('%s must be an instance of %s, not %r'
                                  % (key, get_typenames(self.cls), value))
        if self.element_preprocess:
            value = map(self.element_preprocess, value)
        if self.element_cls:
            for el in value:
                if not isinstance(el, self.element_cls):
                    raise ConfigTypeError(
                        '%s must consist of %s objects, but it includes %r'
                        % (key, get_typenames(self.element_cls), el)
                    )
        return value

    def docstring(self, key, sphinx=False):
        if sphinx:
            stylize_typename = lambda cls: ':class:`%s`' % get_typename(cls)
        else:
            stylize_typename = lambda cls: '``%s``' % get_typename(cls)
        description = self.description or ''
        if self.required:
            description = '*Required.* ' + description
        if self.cls:
            typename = stylize_typename(self.cls)
            if self.element_cls:
                typename += ' of ' + stylize_typename(self.element_cls)
            description = '(%s) %s' % (typename, description)
        return '\n``%s``\n   %s\n' % (key, description)


class ConfigError(Exception):
    """:exc:`Exception` related to configuration."""


class ConfigKeyError(ConfigError, KeyError):
    """Configuration is missing something required."""

    def __init__(self, message, spec):
        super(ConfigKeyError, self).__init__(message)
        self.spec = spec

    def __str__(self):
        return '%r -- %s' % (self.message, self.spec.description)


class ConfigTypeError(ConfigError, TypeError):
    """:exc:`TypeError` specific for configuration."""


def get_typename(cls):
    """Resolves the full name of the given class."""
    if cls.__module__ == '__builtin__':
        return cls.__name__
    return cls.__module__ + '.' + cls.__name__
