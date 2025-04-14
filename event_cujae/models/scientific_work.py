from odoo import models, fields, api

class ScientificWork(models.Model):
    _name = 'scientific.work'
    _description = 'Trabajo Científico'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Para notificaciones

    name = fields.Char(string='Título del Trabajo', required=True)
    author_name=fields.Char(string='Nombre del autor', required=True)
    event_id = fields.Many2one('event.event', string='Evento', required=True)
    attachment = fields.Binary(string='Archivo del Trabajo')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('to_review', 'Por Revisar'),
        ('reviewed', 'Revisado'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
    ], string='Estado', default='draft', tracking=True)
    reviewer_ids = fields.One2many('work.reviewer', 'work_id', string='Revisores')

    def action_to_review(self):
        self.write({'state': 'to_review'})

    def action_reviewed(self):
        self.write({'state': 'reviewed'})

    def action_approved(self):
        self.write({'state': 'approved'})

    def action_rejected(self):
        self.write({'state': 'rejected'})

class WorkReviewer(models.Model):
    _name = 'work.reviewer'
    _description = 'Revisor de Trabajo'

    work_id = fields.Many2one('scientific.work', string='Trabajo', required=True)
    reviewer_id = fields.Many2one('res.users', string='Revisor', required=True)
    opinion = fields.Text(string='Opinión')
    rating = fields.Float(string='Calificación', digits=(2, 1))  # Ejemplo: 4.5
    is_reviewed = fields.Boolean(string='Revisado', default=False)

    def action_mark_reviewed(self):
        self.write({'is_reviewed': True})
        if all(reviewer.is_reviewed for reviewer in self.work_id.reviewer_ids):
            self.work_id.action_reviewed()