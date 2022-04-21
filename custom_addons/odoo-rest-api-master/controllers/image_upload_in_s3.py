import logging
import boto3
from botocore.exceptions import ClientError
import os
import json
import math
import logging
import requests
import ast
import base64
from odoo import http, _, exceptions, fields
from datetime import timedelta, time
from odoo.tools.float_utils import float_round
from odoo.http import request
from .serializers import Serializer
from .exceptions import QueryFormatError
from .error_or_response_parser import *
from werkzeug.utils import secure_filename

_logger = logging.getLogger(__name__)
import calendar;
import time;

ts = calendar.timegm(time.gmtime())


bucket = 'pandomall'
# path = '/home/aman/Downloads/project14new/custom_addons/odoo-rest-api-master/static/src/image/'
path = '/home/aakash/Pando-Mall/custom_addons/odoo-rest-api-master/static/src/image/'

class OdooAPI(http.Controller):

    def upload_file(self, file_name, bucket, object_name):
        """Upload a file to an S3 bucket
        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """
        s3_client = boto3.client(
            's3')
        try:
            print(object_name, "OBJECT NAME")
            with open(file_name, 'rb') as f:
                response = s3_client.upload_fileobj(f, bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def delete_image(self, bucket, file):
        s3_client = boto3.client('s3')
        try:
            s3_client.delete_object(Bucket=bucket, Key=file)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    @http.route('/api/v1/c/image_upload_s3', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def image_upload_in_s3(self, **kw):
        if not kw['file']:
            error = {"message": "File is not present in the request", "status": 400}
            return return_Response_error(error)
        file = kw['file']
        filename = secure_filename(file.filename)
        filename = str(ts) + str(filename)
        file.save(os.path.join(path, filename))
        if file:
            res_data = self.upload_file(path + filename, bucket, filename)
            if res_data is True:
                res_data = {"message": "Image successfully upload",
                            "image_path": "https://pandomall.s3.ap-southeast-1.amazonaws.com/" + str(filename),
                            "filename":filename}

                return return_Response(res_data)
            if res_data is False:
                error = {"message": "Image is not uploaded", "status": 400}
                return return_Response_error(error)

    @http.route('/api/v1/c/image_upload_s3_delete', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def image_upload_in_delete(self, **kw):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        try:
            file = jdata.get('filename')
            res_data = self.delete_image(file)
            if res_data is True:
                res_data = {"message": "Successfully Delete"}
                return return_Response(res_data)
            if res_data is False:
                res_data = {"message": "No image found"}
                return return_Response(res_data)

        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
