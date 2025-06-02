from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import textwrap

class SurveyUserInputLine(models.Model):
    _inherit = ['survey.user_input.line']

    max_score= fields.Float(related='question_id.max_score', string='Question score')

    answer_type = fields.Selection(
        selection_add=[
            ('upload_file', 'Upload file'),
            ('true_false', 'Verdadero o Falso'),
            ('link', 'Enlaza'),
        ],
        help="The type of answer for this question (upload_file if the user "
             "is uploading a file).")

    value_file_data_ids = fields.Many2many('ir.attachment',
                                           help="The attachments "
                                                "corresponding to the user's "
                                                "file upload answer, if any.")
    true_false_item_id = fields.Many2one(
        'survey.true_false_item',
        string="Inciso V o F"
    )

    true_false_item_answer = fields.Char('V or F answer')

    link_item_id = fields.Many2one(
        'survey.link_item',
        string='Inciso de enlaza',
    )
    link_item_answer_id = fields.Many2one(
        'survey.link_item',
        string='Respuesta al inciso de pregunta tipo link',
    )

    @api.depends('answer_type')
    def _compute_display_name(self):
        for line in self:
            if line.answer_type == 'char_box':
                line.display_name = line.value_char_box
            elif line.answer_type == 'text_box' and line.value_text_box:
                line.display_name = textwrap.shorten(line.value_text_box, width=50, placeholder=" [...]")
            elif line.answer_type == 'numerical_box':
                line.display_name = line.value_numerical_box
            elif line.answer_type == 'date':
                line.display_name = fields.Date.to_string(line.value_date)
            elif line.answer_type == 'datetime':
                line.display_name = fields.Datetime.to_string(line.value_datetime)
            elif line.answer_type == 'suggestion':
                if line.matrix_row_id:
                    line.display_name = '%s: %s' % (
                        line.suggested_answer_id.value,
                        line.matrix_row_id.value)
                else:
                    line.display_name = line.suggested_answer_id.value
            elif line.answer_type == 'link':
                link_item = self.env['survey.link_item'].browse(int(line.link_item_answer_id))
                line.display_name = link_item.answer
            elif line.answer_type == 'true_false':
                if line.true_false_item_answer == 'V':
                    line.display_name = _('Verdadero')
                elif line.true_false_item_answer == 'F':
                    line.display_name = _('Falso')

            if not line.display_name:
                line.display_name = _('Skipped')

    @api.constrains('skipped', 'answer_type')
    def _check_answer_type_skipped(self):
        """ Check that a line's answer type is not set to 'upload_file' if
        the line is skipped."""
        for line in self:
            if line.answer_type == 'link':
                if not line.link_item_id or not line.link_item_answer_id:
                    raise ValidationError(_('The answer must be in the right type'))
            elif line.answer_type == 'true_false':
                if not line.true_false_item_id or not line.true_false_item_answer:
                    raise ValidationError(_('The answer must be in the right type'))
            elif line.answer_type != 'upload_file':
                super(SurveyUserInputLine, line)._check_answer_type_skipped()


    @api.constrains('answer_score', 'question_id')
    def _check_answer_score_limit(self):
        """Valida que el answer_score no sea mayor que el max_score de la pregunta."""
        for line in self:
            if line.question_id and line.answer_score > line.question_id.max_score:
                raise ValidationError(
                    "The answer score cannot be higher than maximum score (%s)." 
                    % line.question_id.max_score  # <--- Aquí está la corrección
                )

    @api.model
    def _get_answer_score_values(self, vals, compute_speed_score=True):
        res = super(SurveyUserInputLine, self)._get_answer_score_values(vals, compute_speed_score)

        question_id=vals.get('question_id')
        answer_type = vals.get('answer_type')

        link_item_id = vals.get('link_item_id')
        link_item_answer_id = vals.get('link_item_answer_id')

        true_false_item_id = vals.get('true_false_item_id')
        true_false_item_answer = vals.get('true_false_item_answer')

        if not question_id or not answer_type:
            return res

        question = self.env['survey.question'].browse(int(question_id))

        answer_is_correct = False
        answer_score = 0

        if question.question_type in ['char_box']:
            answer=vals['value_char_box']
            normalized_answer = answer.strip().lower() if answer else ""
            # Buscar coincidencia en respuestas válidas
            valid_answers = [ans.value.strip().lower() for ans in question.valid_answer_ids]
            if normalized_answer  in valid_answers:
                answer_is_correct=True
                answer_score = question.answer_score
            return {
                'answer_is_correct': answer_is_correct,
                'answer_score': answer_score
            }
        elif question.question_type == 'link':
            if link_item_answer_id and link_item_id:
                link_item = self.env['survey.link_item'].browse(link_item_id)
                answer_is_correct = link_item_answer_id == link_item_id

                return {
                    'answer_is_correct': answer_is_correct,
                    'answer_score': link_item.score if answer_is_correct else 0
                }
        elif question.question_type == 'true_false':
            if true_false_item_answer and true_false_item_id:
                true_false_item = self.env['survey.true_false_item'].browse(true_false_item_id)
                answer_is_correct = true_false_item.answer == true_false_item_answer

                return {
                    'answer_is_correct': answer_is_correct,
                    'answer_score': true_false_item.score if answer_is_correct else 0
                }
        else:
            return res
