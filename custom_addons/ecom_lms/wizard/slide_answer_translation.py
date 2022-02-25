# _*_coding: utf-8 _*_

from odoo import models, fields, api,_
from odoo.exceptions import UserError



class SlideAnswerTitleTranslation(models.Model):
    _name = "slide.answer.title.translation"
    
    slide_ans_lang_translation_ids = fields.One2many('slide.answer.lang.translation.line', 'ans_transaltion_wiz_id', string='Language Translation')
    slide_qus_id=fields.Many2one('slide.question', string='Slide')
    slide_ans_id=fields.Many2one('slide.answer', string='Slide Answer')
    
    
    def translate_done(self):
        return True
    
    
    
    
class SlideAnswerLangTranslationLine(models.Model):
    _name = "slide.answer.lang.translation.line"
    
    language_id = fields.Selection([
                    ('english', 'English'), ('hindi', 'Hindi'), ('gujarati', 'Gujarati'),('marathi', 'Marathi'), ('assamese', 'Assamese'), ('tamil', 'Tamil')
                    , ('kannada', 'Kannada'), ('malyalam', 'Malyalam'), ('telugu', 'Telugu')],
                    string='Language')
    
    translation_value= fields.Char('Text')
    
    ans_transaltion_wiz_id=fields.Many2one('slide.answer.title.translation', string='Answer Wiz')
    
    
    
    
    
class SlideAnswerCommentTranslation(models.Model):
    _name = "slide.answer.comment.translation"
    
    slide_ans_comment_lang_translation_ids = fields.One2many('slide.ans.comment.lang.translation.line', 'ans_comment_transaltion_wiz_id', string='Language Translation')
    slide_qus_id=fields.Many2one('slide.question', string='Slide')
    slide_ans_id=fields.Many2one('slide.answer', string='Slide Answer')
    
    
    def translate_done(self):
        return True
    
    
    
    
class SlideAnsCommentLangTranslationLine(models.Model):
    _name = "slide.ans.comment.lang.translation.line"
    
    language_id = fields.Selection([
                    ('english', 'English'), ('hindi', 'Hindi'), ('gujarati', 'Gujarati'),('marathi', 'Marathi'), ('assamese', 'Assamese'), ('tamil', 'Tamil')
                    , ('kannada', 'Kannada'), ('malyalam', 'Malyalam'), ('telugu', 'Telugu')],
                    string='Language')
    
    translation_value= fields.Char('Text')
    
    ans_comment_transaltion_wiz_id=fields.Many2one('slide.answer.comment.translation', string='Answer Wiz')
    