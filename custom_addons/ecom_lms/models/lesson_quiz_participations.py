# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import uuid

from dateutil.relativedelta import relativedelta


class LessonQuizParticipations(models.Model):
    _name = "lesson.quiz.participations"
    _description = "Lesson Quiz Participations"

    lesson_id = fields.Many2one('slide.slide', string='Lesson', required=True, readonly=True, ondelete='cascade')
    start_datetime = fields.Datetime('Start date and time', readonly=True)
    deadline = fields.Datetime('Deadline', help="Datetime until customer can open the Lesson Quiz and submit answers")
    lesson_time_limit_reached = fields.Boolean("Lesson Time Limit Reached",
                                               compute='_compute_lesson_time_limit_reached')
    access_token = fields.Char('Identification token', default=lambda self: str(uuid.uuid4()), readonly=True,
                               required=True, copy=False)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    user_id = fields.Many2one('res.users', string='User', readonly=True)
    completed = fields.Boolean('Done', default=False)

    # attempts_limit = fields.Integer("Number of attempts", related='survey_id.attempts_limit')
    attempts_num = fields.Integer("Attempt n°")

    @api.depends(
        'start_datetime',
        'lesson_id.is_time_limited',
        'lesson_id.time_limit')
    def _compute_lesson_time_limit_reached(self):
        """ Checks that the user_input is not exceeding the survey's time limit. """
        for user_input in self:
            if user_input.start_datetime:
                start_time = user_input.start_datetime
                time_limit = user_input.lesson_id.time_limit
                user_input.lesson_time_limit_reached = user_input.lesson_id.is_time_limited and \
                                                       fields.Datetime.now() >= start_time + relativedelta(
                    minutes=time_limit)
            else:
                user_input.lesson_time_limit_reached = False



