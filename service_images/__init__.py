from flask import Flask, got_request_exception, render_template, json
from flask.logging import default_handler
import logging
from .config import Config
# from .models import WorkDAO
from flask_restplus import Api as BaseApi


# configure all loggers same as default flask logger
root = logging.getLogger()
root.addHandler(default_handler)


def create_app(config_class=None):
    """
    App factory
    :param config_class: class, with additional config parameters if need
    :return: Flask instance
    """
    app = Flask(__name__,
                static_url_path = ''  # removes any preceding path from the URL (i.e. the default /static)
                ) # template_folder = 'my/templates'

    app.url_map.strict_slashes = False
    app.config.from_object(Config)          # default
    app.config.from_object(config_class)    # overwrite & additional

    app.static_folder = str(app.config['PROCESSED_DIR_PATH'].resolve())

    # Add file logger for the app
    file_handler = logging.FileHandler(filename=app.config['LOG_PATH'])
    file_handler.setFormatter(logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(app.config['LOGGING_LEVEL'])

    # Attach custom error handlers to an exception
    def log_exception(sender, exception, **extra):
        """ Log an exception to our logging framework """
        sender.logger.debug('Got exception during processing: %s', exception)

    got_request_exception.connect(log_exception, app)


    # Hack to use current configuration
    with app.app_context():
        from .apis import api as ns1

    # Workaround of "I can't seem to set a path of '/'": https://github.com/noirbizarre/flask-restplus/issues/247
    # - solution 1
    class Api(BaseApi):
        def _register_doc(self, app_or_blueprint):
            # HINT: This is just a copy of the original implementation but with the last line commented out.
            if self._add_specs and self._doc:
                # Register documentation before root if enabled
                app_or_blueprint.add_url_rule(self._doc, 'doc', self.render_doc)
            # app_or_blueprint.add_url_rule(self._doc, 'root', self.render_root)

        @property
        def base_path(self):
            return ''

    api = Api(
        title='Image processing service',
        version='1.0',
        description='Test task of implementing The REST API',
        doc = '/doc/'
    )
    app.config.SWAGGER_UI_DOC_EXPANSION = 'list'

    from flask import make_response, render_template_string

    def convert_dict_of_lists_to_html(data):
        """
        Render lists from each key, also render images if have corresponded key
        :param data: dict with field(s) which contain list
        :return:
        """
        return render_template_string(""" 
                        {% for key, list in data.items() %}
                           <h2> {{key}} </h2>
                           <ul>
                           {% if key != 'files' %}
                                {% for item in list %}
                                  <li><a href = "{{ item }}">{{ item }}</a> </li>
                                {% endfor %}
                           {% else %}
                                {% for file in list %}
                                  <li>
                                    <a href = "{{ file }}">{{ file }}</a>
                                    <a download="{{ file }}" href="{{ file }}" title="{{ file }}">
                                      <img src="{{ file }}" width="120" height="90" />
                                    </a>
                                  </li>
                                {% endfor %}
                           {% endif %}                                    
                           </ul>
                        {% endfor %}
                        """, data=data)

    @api.representation('text/html')
    def output_html(data, code, headers=None):
        resp = make_response(convert_dict_of_lists_to_html(data), code)
        if headers:
            resp.headers.extend(headers)
        return resp

    @api.representation('application/json')
    def output_json(data, code, headers=None):
        resp = make_response(json.dumps(data), code)
        if headers:
            resp.headers.extend(headers)
        return resp

    @api.errorhandler
    def default_error_handler(error):
        """
        Default error handler
        :param error:
        :return:
        """
        app.logger.exception(error)
        return {'message': str(error)}, getattr(error, 'code', 500)

    # - solution 2
    # @app.route('/')
    # def index():
    #     return render_template('index.html')


    api.add_namespace(ns1)
    api.init_app(app)  # app.register_blueprint(api, url_prefix='/api/1')
    return app

