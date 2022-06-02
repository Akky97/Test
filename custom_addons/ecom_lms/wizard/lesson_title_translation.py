# _*_coding: utf-8 _*_

from odoo import models, fields, api,_
from odoo.exceptions import UserError



class LessonTitleTranslation(models.Model):
    _name = "lesson.title.translation"
    
    lesson_lang_translation_ids = fields.One2many('lesson.lang.translation.line', 'lesson_transaltion_wiz_id', string='Language Translation')
    slide_id=fields.Many2one('slide.slide', string='Slide')
    
    def translate_done(self):
        return True
    
    
class LessonLangTranslationLine(models.Model):
    _name = "lesson.lang.translation.line"
    
    language_id = fields.Selection([
                    ('english', 'English'), ('hindi', 'Hindi'), ('gujarati', 'Gujarati'),('marathi', 'Marathi'), ('assamese', 'Assamese'), ('tamil', 'Tamil')
                    , ('kannada', 'Kannada'), ('malyalam', 'Malyalam'), ('telugu', 'Telugu')],
                    string='Language')
    
    translation_val= fields.Text('Text')
    
    lesson_transaltion_wiz_id=fields.Many2one('lesson.title.translation', string='Lesson Wiz')
    