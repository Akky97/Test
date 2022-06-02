# _*_coding: utf-8 _*_

from odoo import models, fields, api,_
from odoo.exceptions import UserError
import string
import random
import re
from datetime import timedelta
from xlrd import open_workbook, XLRDError, xldate_as_tuple
from datetime import datetime
import base64, urllib
import os



class UploadCertificateQuiz(models.Model):
    _name = "upload.certificate.quiz"
    
    quiz_ids = fields.One2many('survey.question', 'certificate_wiz_id', string='Quiz')