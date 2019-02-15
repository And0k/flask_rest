from flask import current_app as app, request, jsonify, make_response, send_file, send_from_directory, render_template_string, url_for
from flask_restplus import Namespace, Resource, fields, marshal_with, reqparse, marshal
from pathlib import Path
from .models import WorkDAO, ApiError
# from werkzeug.​contrib.​fixers import ProxyFix

#blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Namespace('Tasks', path='/', title='Images processing API', version='1.0', contact='ao.korzh@gmail.ru',
          description='A simple API of converting images to black and white', validate=True)
Work = WorkDAO()  #processed_dir_path=app.config['PROCESSED_DIR_PATH']

# api.namespaces.clear()
# ns = api.namespace('tasks', description='operations')

# def on_json_loading_failed(err):
#     if not request.is_json:
#         raise ApiError('Expected "application/json" encoded data', 'Wrong media type', 415)
#     raise ApiError(str(err), 'Bad request', 400)
#
#
# request.on_json_loading_failed = on_json_loading_failed
# task = request.get_json(
#     force=True)  # force=True will make sure this works even if a client does not specify application/json

# input models
len_hex_uuid4 = 32
guid_model_field = fields.String(description='The task unique identifier (hex uuid4 number without dashes)',
                          min_length=len_hex_uuid4, max_length=len_hex_uuid4)
task_model_dict = {
    'url_list': fields.List(fields.Url, description='The task processing parameter: list of urls of images to process'),
    'threshold': fields.Float(required=True, min=0, max=255, description='The task processing parameter')
}
task_model = api.model('task', task_model_dict)
#put_task_fields = api.model('put task', dict(post_task_model_dict, guid=guid_model_field))

# output model
processed_fields = api.model('Processed', {
    'guid': guid_model_field,
    'processed_cnt': fields.Integer})
# class Processed(fields.Raw):
#     def format(self, value):
#         return {'id': value.id, 'processed_cnt': value.processed_cnt}


# Resources #
@api.route('/', '/index/')        #, endpoint='root'
class ProcessedTasks(Resource):         # Root
    # def __init__(self):
    #     parser = reqparse.RequestParser()
    #     # Look only in the json
    #     parser.add_argument('url_list', type=list, location='json')
    #     parser.add_argument('threshold', type=list, location='json')


    def get(self):
        """
        List all work id (folders named with GUIDs if created by Post message)
        :return: list of all ids
        """
        return {'guids': Work.list_ids()}


    @api.expect(task_model)
    @marshal_with(processed_fields)
    def post(self):
        """
        Data processing request.
        Input json data are url list of links to images
        :return: json with guid of unique work ID (and the same name of folder with results and number of successfully processed files)
        """
        #args = self.reqparse.parse_args()
        return Work.create(**api.payload), 201


# @api.​response(404, 'Task id not found')
# @api.​param('guid', 'The task identifier')
@api.route('/<string:guid>/<path:filename>/')   # @api.route('/<path:path>')   #
class ProcessedTaskItem(Resource):
    """

    """

    def get(self, guid, filename=None): #
        """
        :param guid:
        :param filename:
        :return: individual image
        """
        if filename:
            file = Work.get_item(guid, filename)
            try:
                return send_from_directory(
                    app.config['PROCESSED_DIR_PATH'] / guid, str(file.name), as_attachment=True,
                    attachment_filename=filename)
            except Exception as err:
                raise ApiError(f'{filename} not in dir', 'Bad request', 400)
                # api.abort(http_code, self.message)
        # else:
        #     raise ApiError(f'bad format', 'Bad request', 400)

@api.route(f'/<string(length={len_hex_uuid4}):guid>/')  #, doc={'params':task_fields['guid']} @api.route('/<path:path>')   # )
class ProcessedTaskItems(Resource):
    """

    """

    # @api.doc('return processed image')
    # @api.expect(task_fields, validate=True)
    # @api.marshal_with(task_fields, code=201)
    # @api.representation('image/png')
    # def __init__(self, filename):
    #     """
    #     Split filename on work id and
    #     :param filename:
    #     """
    #     parser = reqparse.RequestParser()
    #     # Look only in the json
    #     parser.add_argument('url_list')
    #     parser.add_argument('threshold')
    #     self.guid, self.filename = filename.split('/', 1)

    #@api.marshal_list_with({'files': fields.List(fields.String, description='image file name with extention')})
    def get(self, guid=None):  #
        """
        url list of processed files
        :param guid: globally unique work id
        :return:
            json: processed image(s) urls or
            html: all in html list
        """
        # All images in list
        files = list(Work.get(guid))
        return {'files':
                    [url_for('static',
                             filename=str(file.relative_to(app.config['PROCESSED_DIR_PATH']))) for file in files]
               }

    #@api.doc('delete processed task dir')
    @api.response(204, "{'result': True}" )  #'Processed task deleted'
    def delete(self, guid):
        """Delete a processed task results given its guid"""
        if Work.delete(guid):
            return {'result': True}, 204   # {'deleted': guid}, 204

    @api.expect(task_model)
    def put(self, guid):
        """Update a processed task results given its identifier"""
        return Work.update(guid, **api.payload), 201
