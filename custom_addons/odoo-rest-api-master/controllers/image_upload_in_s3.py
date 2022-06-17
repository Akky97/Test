import json

import boto3
import requests
from botocore.exceptions import ClientError
import os
import logging
from odoo import http, _, exceptions, fields
from odoo.http import request
from .exceptions import QueryFormatError
from .error_or_response_parser import *
from werkzeug.utils import secure_filename
from odoo.tools import partition, collections, frozendict, lazy_property, image_process

import  base64
_logger = logging.getLogger(__name__)
import calendar;
import time;

ts = calendar.timegm(time.gmtime())


bucket = 'pandomall'
path = '/home/ubuntu/Pando-Mall/custom_addons/odoo-rest-api-master/static/src/image/'
path2 = '/home/ubuntu/Pando-Mall/custom_addons/odoo-rest-api-master/static/src/image/image2/'


class OdooAPI(http.Controller):

    def ipfs_file_upload(self, file_name):
        url = 'https://clouddasboard.pandoproject.org/api/v0/add'
        myfiles = {'file': open(file_name, 'rb')}
        res = requests.post(url, files=myfiles)
        return res.text

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

    def delete_image(self, file):
        s3_client = boto3.client('s3')
        try:
            s3_client.delete_object(Bucket=bucket, Key=file)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    @validate_token
    @http.route('/api/v1/c/image_upload_ipfs', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def image_upload_in_ipfs(self, **kw):
        if not kw['file']:
            error = {"message": "File is not present in the request", "status": 400}
            return return_Response_error(error)
        file = kw['file']
        filename = secure_filename(file.filename)
        filename = str(ts) + str(filename)
        file.save(os.path.join(path, filename))
        if file:
            res_data = self.ipfs_file_upload(path + filename)
            if res_data:
                res_data = {"message": "Image successfully upload",
                            "result": json.loads(res_data),
                            "status": 200}

                return return_Response(res_data)
            if res_data is False:
                error = {"message": "Image is not uploaded", "status": 400}
                return return_Response_error(error)

    @validate_token
    @http.route('/api/v1/c/image_upload_s3', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def image_upload_in_s3(self, **kw):
        if not kw['file']:
            error = {"message": "File is not present in the request", "status": 400}
            return return_Response_error(error)
        file = kw['file']
        filename = secure_filename(file.filename)
        filename = str(ts) + str(filename)
        file.save(os.path.join(path, filename))
        file_text = open(path + filename, 'rb')
        file_read = file_text.read()
        file_encode = base64.encodebytes(file_read)
        file2 = image_process(file_encode, size=(500, 500))
        file2 = base64.decodebytes(file2)
        completeName = os.path.join(path2, filename)
        file1 = open(completeName, "wb")
        file1.write(file2)
        if file:
            res_data = self.upload_file(path2 + filename, bucket, filename)
            # res_data = self.upload_file(path + filename, bucket, filename)
            data = self.ipfs_file_upload(path2 + filename)
            # data = self.ipfs_file_upload(path + filename)
            if res_data is True:
                res_data = {"message": "Image successfully upload",
                            "image_path": "https://pandomall.s3.ap-southeast-1.amazonaws.com/" + str(filename),
                            "filename": filename,
                            # "messagehash": "Image successfully upload",
                             "result": json.loads(data),
                             "status": 200
                            }

                return return_Response(res_data)
            if res_data is False:
                error = {"message": "Image is not uploaded", "status": 400}
                return return_Response_error(error)

    @validate_token
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

    @validate_token
    @http.route('/api/v1/c/get_system_parameter', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def get_system_parameter(self, **kw):
        try:
            jdata = json.loads(request.httprequest.stream.read())
        except:
            jdata = {}
        try:
            if jdata.get('key'):
                record = request.env['ir.config_parameter'].sudo().search([('key', '=', jdata.get('key'))], limit=1)
                if record:
                    res = {
                        'key': jdata.get('key'),
                        'value': record.value,
                        'status': 200
                    }
                    return return_Response(res)
                else:
                    msg = {"message": "Something Went Wrong.", "status_code": 400}
                    return return_Response_error(msg)
            else:
                msg = {"message": "Something Went Wrong.", "status_code": 400}
                return return_Response_error(msg)
        except (SyntaxError, QueryFormatError) as e:
            return error_response(e, e.msg)
