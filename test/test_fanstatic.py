import os

from expecter import expect
from flask_fanstatic import Fanstatic
from flask import Flask, Blueprint, render_template

from js.jquery import jquery


def app_client(**options):
  app = make_app(**options)
  Fanstatic(app)
  return app.test_client()


def make_app(**options):
  test_dir = os.path.dirname(__file__)
  app = Flask('app',
    template_folder=os.path.join(test_dir, 'templates'),
    static_folder=os.path.join(test_dir, 'static'),
  )
  if options:
    app.config['FANSTATIC_OPTIONS'] = options

  @app.route('/no-needs')
  def no_needs():
    return render_template('index.html')

  @app.route('/needs-jquery')
  def needs_jquery():
    jquery.need()
    return render_template('index.html')

  @app.route('/template/<name>')
  def template_needs_jquery(name):
    return render_template('%s.html' % name)

  return app


def test_needing_resource():
  with app_client() as client:
    rv = client.get('/no-needs')
    expect(rv.data).does_not_contain('jquery.js')

    rv = client.get('/needs-jquery')
    expect(rv.data).contains('/fanstatic/jquery/jquery.js')

    rv = client.get('/template/needs_jquery')
    expect(rv.data).contains('/fanstatic/jquery/jquery.js')


def test_file_provider():
  with app_client() as client:
    rv = client.get('/fanstatic/jquery/jquery.js')
    expect(rv.status_code) == 200

    rv = client.get('/fanstatic/jquery/does-not-exist.js')
    expect(rv.status_code) == 404


def test_custom_publisher_signature():
  with app_client(publisher_signature='custom') as client:

    rv = client.get('/needs-jquery')
    expect(rv.data).contains('/custom/jquery/jquery.js')
    expect(rv.data).does_not_contain('fanstatic')

    rv = client.get('/custom/jquery/jquery.js')
    expect(rv.status_code) == 200

    rv = client.get('/fanstatic/jquery/jquery.js')
    expect(rv.status_code) == 404


def test_app_resources():
  app = make_app()
  fanstatic = Fanstatic(app)
  fanstatic.resource('app.js', name='app_js')

  with app.test_client() as client:
    rv = client.get('/template/needs_app_js')
    expect(rv.data).contains('/fanstatic/app/app.js')

    rv = client.get('/fanstatic/app/app.js')
    expect(rv.status_code) == 200


def test_blueprints():
  app = make_app()

  test_dir = os.path.dirname(__file__)
  bluep = Blueprint('bluep', 'blueprint',
    static_folder=os.path.join(test_dir, 'bluep_static'),
  )

  fanstatic = Fanstatic(bluep)
  fanstatic.resource('bluep.js', name='bluep_js')

  @bluep.route('/')
  def bluep_index():
    return render_template('bluep.html')

  app.register_blueprint(bluep, url_prefix='/bluep')

  with app.test_client() as client:
    rv = client.get('/bluep/')
    expect(rv.data).contains('/fanstatic/bluep/bluep.js')

    rv = client.get('/fanstatic/bluep/bluep.js')
    expect(rv.status_code) == 200
