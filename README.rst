Flask-Fanstatic
===============

Flask integration for the Fanstatic resource publishing system.

http://www.fanstatic.org/

.. image:: https://api.travis-ci.org/mgood/flask-fanstatic.png
   :target: https://travis-ci.org/mgood/flask-fanstatic


Overview
--------

Fanstatic is a flexible system for managing the static resources (CSS and
Javascript) used by your web application.  This extension provides simple
integration between Fanstatic and Flask.

Adding static resources to your application becomes as simple as installing them
with pip::

  pip install js.jquery

and ``need``-ing them in your template::

  {{ g.fanstatic.needs('js.jquery:jquery') }}


Usage
-----

To start using Flask-Fanstatic, import and initialize the extension for your
Flask application::

  from flask import Flask
  from flask_fanstatic import Fanstatic

  app = Flask(__name__)
  fanstatic = Fanstatic(app)

Then, in your base template, add the ``top`` and ``bottom`` resources to include
them in your HTML::

  <head>
    {{ g.fanstatic.top }}
  </head>

  <body>
    ...content...

    {{ g.fanstatic.bottom }}
  </body>

You can declare resource to include, by using the ``needs()`` helper to declare
resources needed by your template::

  {{- g.fanstatic.needs('js.jquery:jquery') -}}
  {% extends 'layout.html' %}
  ...

.. note:: The example above uses dashes to tell Jinja to strip the extra whitespace such
   as the newline after the expression.  See the Jinja docs for more details:
   http://jinja.pocoo.org/docs/templates/#whitespace-control

Fanstatic will use the ``top`` and ``bottom`` helpers above to include the CSS
or JavaScript resources ``need``-ed automatically.

You can also ``need`` multiple resources::

  {{ g.fanstatic.needs(
    'js.jquery:jquery',
    'js.handlebars:handlebars'
  ) }}

The ``needs()`` method takes any number of strings, in the form
``<module>:<resource>``.  You can alternatively import the resources from your
code and require them like::

  from js.jquery import jquery

  @app.route('/')
  def index():
    jquery.need()
    return render_template('index.html')


Application resources
---------------------

Flask-Fanstatic also makes it easy to add your application's own static files as
Fanstatic resources.

You can use the ``resource()`` helper to declare a resource in your
application's ``'static'`` folder::

  fanstatic.resource('js/app.js', name='app_js', depends=[jquery])

To include the resource, just use its ``name`` to require it in your template::

  {{ g.fanstatic.needs('app_js') }}

You can also declare named groups of resources::

  from js.jquery import jquery
  fanstatic.resource('css/app.js', name='app_js')

  # there are 3 ways to specify a group resource item:
  fanstatic.group('app_resources', [
    # with an imported resource:
    jquery,

    # with the name of an internal resource:
    'app_js',

    # with an inline resource:
    fanstatic.resource('css/app.css'),
  ])

Groups are included in the same way from the template::

  {{ g.fanstatic.needs('app_resources') }}


Blueprint resources
-------------------

Blueprints can also use Fanstatic in almost the same way as application
resources.  Start by initializing a ``Fanstatic()`` object for your blueprint,
and declare its resources::

  bluep = Blueprint('bluep', __name__, static_folder='static')
  fanstatic = Fanstatic(bluep)
  fanstatic.resource('bluep.css', name='bluep_css')

In the template, reference resources from the current blueprint as ``.<name>``::

  {{ g.fanstatic.needs('.bluep_css') }}

Or explicitly provide the name of a blueprint to include a resource from a
specific blueprint::

  {{ g.fanstatic.needs('bluep.bluep_css') }}
