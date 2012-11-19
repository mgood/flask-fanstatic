from fanstatic import (init_needed, Publisher, get_library_registry,
                       DEFAULT_SIGNATURE, Resource, Library, Group)
from flask import Blueprint, g, Markup, current_app, request
from werkzeug import cached_property
from werkzeug.utils import import_string
from werkzeug.wsgi import DispatcherMiddleware


class Fanstatic(object):
  def __init__(self, app=None):
    self.app = app

    if app is not None:
      self.init_app(app)

    if app is not None and app.has_static_folder:
      self.library = Library(app.name, app.static_folder)
      get_library_registry().add(self.library)
    else:
      self.library = None

    self.resources = {}

  def init_app(self, app):
    if isinstance(app, Blueprint):
      app.record_once(lambda s: self._configure_app(s.app, blueprint=app))
    else:
      self._configure_app(app)

  def _configure_app(self, app, blueprint=None):
    if not hasattr(app, 'extensions'):
      app.extensions = {}

    if 'fanstatic' not in app.extensions:
      app.extensions['fanstatic'] = _FanstaticManager(app)

    app.extensions['fanstatic'].register(self, blueprint=blueprint)

  def resource(self, *args, **kwargs):
    if self.app is None:
      raise AssertionError('Cannot provide resources: '
                           'not initialized with an app')
    if self.library is None:
      raise AssertionError('Cannot provide resources: '
                           'app does not have a static folder')

    name = kwargs.pop('name', None)
    resource = Resource(self.library, *args, **kwargs)
    if name:
      self.resources[name] = resource
    return resource

  def group(self, name, items):
    items = [
      self.resources[i] if isinstance(i, basestring) else i
      for i in items
    ]
    group = self.resources[name] = Group(items)
    return group


class _FanstaticManager(object):
  def __init__(self, app):
    self.publisher = Publisher(get_library_registry())

    app.before_request(self.before_request)

    options = app.config.get('FANSTATIC_OPTIONS', {})
    publisher_signature = options.get('publisher_signature', DEFAULT_SIGNATURE)

    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
      '/%s' % publisher_signature: self.publisher,
    })

    self.resource_sets = {}

  def register(self, fanstatic, blueprint=None):
    if blueprint:
      prefix = blueprint.name
    else:
      prefix = None
    self.resource_sets[prefix] = fanstatic
  
  def find_resource(self, name):
    if ':' in name:
      return import_string(name)

    blueprint, sep, resource = name.rpartition('.')
    if not sep:
      blueprint = None
    elif not blueprint:
      blueprint = request.blueprint

    return self.resource_sets[blueprint].resources[resource]

  def before_request(self):
    g.fanstatic = _FanstaticContext(init_needed(
      # TODO set base_url for this app if needed
      **current_app.config.get('FANSTATIC_OPTIONS', {})
    ), self)


class _FanstaticContext(object):
  def __init__(self, needed, manager):
    self._needed = needed
    self._manager = manager
    self._rendered = False

  def needs(self, *resources):
    if self._rendered:
      raise AssertionError('Invalid state: already rendered Fanstatic resources')

    for name in resources:
      self._manager.find_resource(name).need()

    return ''

  @property
  def top(self):
    return Markup(self._topbottom[0])

  @property
  def bottom(self):
    return Markup(self._topbottom[1])

  @cached_property
  def _topbottom(self):
    self._rendered = True
    if self._needed.has_resources():
      return self._needed.render_topbottom()
    else:
      return '', ''
