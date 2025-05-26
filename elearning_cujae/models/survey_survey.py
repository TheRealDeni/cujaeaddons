from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
class Survey(models.Model):
    _inherit="survey.survey"
    grade_ranges = fields.One2many('survey.grade.range', 'survey_id', string="Grade Ranges")
    exam = fields.Boolean('Is an exam', compute='_compute_exam',readonly=False, store=True, precompute=True)
    exam_give_badge = fields.Boolean('Give exam badge', compute='_compute_exam_give_badge',readonly=False, store=True, copy=False)
    exam_badge_id = fields.Many2one('gamification.badge', 'Exam badge', copy=False)
    exam_badge_id_dummy = fields.Many2one(related='exam_badge_id', string='Exam badge')
    professor_check= fields.Boolean('Checked by teacher', compute='_compute_check_survey',store=True)
    user_input_ids = fields.One2many('survey.user_input', 'survey_id', string='User responses', readonly=False, groups='survey.group_survey_user')
    slides_asociated= fields.One2many('slide.slide','exam_id' , string="Exam Slides")
    @api.depends('scoring_type')
    def _compute_exam(self):
        for survey in self:
            if not survey.exam or survey.scoring_type == 'no_scoring':
                survey.exam = False
    
    @api.depends('users_login_required', 'exam')
    def _compute_exam_give_badge(self):
        for survey in self:
            if not survey.exam_give_badge or \
               not survey.users_login_required or \
               not survey.exam:
                survey.exam_give_badge = False 

    @api.depends('question_ids')
    def _compute_check_survey(self):
        flag=False
        for survey in self:
            survey.professor_check = False
            for question in survey.question_ids:
                if question.question_type in ('text_box', 'upload_file') and question.is_scored_question and flag==False:
                    survey.professor_check = True
                    flag=True
                    

    def _create_default_grade_ranges(self):
        self.ensure_one()
        self.grade_ranges.unlink()  # Eliminar existentes
        
        scoring_min = self.scoring_success_min
        ranges = []
        
        # Caso especial cuando el mínimo es 100%
        if scoring_min == 100:
            ranges = [
                {
                    'min_percentage': 0,
                    'max_percentage': 99.99,  # Hasta 99.99% es nota 2
                    'grade': 2
                },
                {
                    'min_percentage': 100,    # Exactamente 100% es nota 5
                    'max_percentage': 100,
                    'grade': 5
                }
            ]
        else:
            # Nota 2 (suspenso)
            ranges.append({
                'min_percentage': 0,
                'max_percentage': scoring_min,
                'grade': 2
            })
            
            # Calcular rangos para notas 3,4,5
            remaining = 100 - scoring_min
            if remaining > 0:
                step = remaining / 3
                if step < 0.01:
                    raise ValidationError("The range between grades is too short")
                ranges.extend([
                    {
                        'min_percentage': scoring_min,
                        'max_percentage': scoring_min + step,
                        'grade': 3
                    },
                    {
                        'min_percentage': scoring_min + step,
                        'max_percentage': scoring_min + (2 * step),
                        'grade': 4
                    },
                    {
                        'min_percentage': scoring_min + (2 * step),
                        'max_percentage': 100,  # Aseguramos llegar al 100%
                        'grade': 5
                    }
                ])
        
        # Crear registros en orden
        for range_data in ranges:
            self.env['survey.grade.range'].create({
                **range_data,
                'survey_id': self.id
            })
    
    @api.model_create_multi
    def create(self, vals):

        
        survey = super().create(vals)
        survey._create_default_grade_ranges()
        return survey

    def write(self, vals):
        # Actualizar rangos si cambia scoring_success_min
        res = super().write(vals)
        if 'scoring_success_min' in vals:
            for survey in self:
                survey._create_default_grade_ranges()
        return res

    @api.constrains('scoring_success_min')
    def _check_scoring_min(self):
        for record in self:
            if record.scoring_success_min < 0 or record.scoring_success_min > 100:
                raise ValidationError("The minimum scoring percentage must be between 0 and 100")
            

    @api.depends('slide_ids.channel_id','slides_asociated.channel_id')
    def _compute_slide_channel_data(self):
        super(Survey, self)._compute_slide_channel_data()
        for survey in self:
            survey.slide_channel_ids = survey.slides_asociated.mapped('channel_id')
            survey.slide_channel_count = len(survey.slides_asociated)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_linked_to_course(self):
        # we consider it's ok to show certification names for people trying to delete courses
        # even if they don't have access to those surveys hence the sudo usage
        super(Survey,self)._unlink_except_linked_to_course()
        exams = self.sudo().slides_asociated.filtered(lambda slide: slide.slide_type == "exam").mapped('exam_id').exists()
        if exams:
            exams_course_mapping = [_('- %s (Courses - %s)', ex.title, '; '.join(ex.slide_channel_ids.mapped('name'))) for ex in exams]
            raise ValidationError(_(
                'Any Survey listed below is currently used as a Course Exam and cannot be deleted:\n%s',
                '\n'.join(exams_course_mapping)))