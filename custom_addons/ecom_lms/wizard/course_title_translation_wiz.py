# _*_coding: utf-8 _*_

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
import string
import random
import re
from datetime import timedelta
from xlrd import open_workbook, XLRDError, xldate_as_tuple
from datetime import datetime
import base64, urllib
import certifi
import urllib3
import os



class CourseTitleTranslationWiz(models.Model):
    _name = "course.title.translation.wiz"
    
    language_translation_ids = fields.One2many('language.translation.line', 'course_transaltion_wiz_id', string='Language Translation')
    course_id=fields.Many2one('slide.channel', string='Course')
    
    def translate_done(self):
        return True
    
    
    # def translate_done(self):
    #     active_course_id = self._context.get('active_id')
    #     course_id= self.env['slide.channel'].browse(active_course_id)
    #     if course_id:
    #         if course_id.lang_values:
    #             if self.language_translation_ids:
    #                 for lang_line in self.language_translation_ids:
    #                     if lang_line.language_id == course_id.lang_values:
    #                         course_id.name=lang_line.translation_val
        
        
    
class LanguageTranslationLine(models.Model):
    _name = "language.translation.line"
    
    language_id = fields.Selection([
                    ('english', 'English'), ('hindi', 'Hindi'), ('gujarati', 'Gujarati'),('marathi', 'Marathi'), ('assamese', 'Assamese'), ('tamil', 'Tamil')
                    , ('kannada', 'Kannada'), ('malyalam', 'Malyalam'), ('telugu', 'Telugu')],
                    string='Language')
    
    translation_val= fields.Text('Text')
    
    course_transaltion_wiz_id=fields.Many2one('course.title.translation.wiz', string='Course Wiz')
    
    def unlink(self):
        if self.env.user.has_group('ecom_lms.super_admin_group'):
            return super(LanguageTranslationLine, self).unlink()
        else:
            raise ValidationError('You do not have access to delete.')