# _*_coding: utf-8 _*_

from odoo import models, fields, api,_
from odoo.exceptions import UserError



class SlideQuestionTitleTranslation(models.Model):
    _name = "slide.question.title.translation"
    
    slide_qus_lang_translation_ids = fields.One2many('slide.question.lang.translation.line', 'qus_transaltion_wiz_id', string='Language Translation')
    slide_id=fields.Many2one('slide.slide', string='Slide')
    slide_qus_id=fields.Many2one('slide.question', string='Slide Question')
    
    
    def translate_done(self):
        return True
    
    
    
    
class SlideQuestionLangTranslationLine(models.Model):
    _name = "slide.question.lang.translation.line"
    
    language_id = fields.Selection([
                    ('english', 'English'), ('hindi', 'Hindi'), ('gujarati', 'Gujarati'),('marathi', 'Marathi'), ('assamese', 'Assamese'), ('tamil', 'Tamil')
                    , ('kannada', 'Kannada'), ('malyalam', 'Malyalam'), ('telugu', 'Telugu')],
                    string='Language')
    
    translation_value= fields.Char('Text')
    
    qus_transaltion_wiz_id=fields.Many2one('slide.question.title.translation', string='Lesson Wiz')
    