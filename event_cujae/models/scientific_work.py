from odoo import models, fields, api

class ScientificWork(models.Model):
    _name = 'scientific.work'
    _description = 'Trabajo Científico'

    name = fields.Char(string='Título del Trabajo', required=True)
    author_name=fields.Char(string='Nombre del autor', required=True)
    event_id = fields.Many2one('event.event', string='Evento', required=True)
    attachment = fields.Binary(string='Archivo del Trabajo', filename='attachment_filename')
    attachment_filename = fields.Char(string='Nombre del Archivo')
    reviewer_ids = fields.One2many('work.reviewer', 'work_id', string='Revisores')
    state = fields.Selection([
        ('to_review', 'Por Revisar'),
        ('reviewed', 'Revisado'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
    ], string='Estado', tracking=True)

    def action_approved(self):
        self.write({'state': 'approved'})

    def action_rejected(self):
        self.write({'state': 'rejected'})

    def write(self, vals):
        # Guardamos el estado anterior para evitar bucles
        old_states = {w.id: w.state for w in self}

        res = super().write(vals)

        for work in self:
            # 1) Si el número de revisores llega a 3 y aún no está en to_review:
            if len(work.reviewer_ids) >= 3 and old_states[work.id] != 'to_review':
                work.state = 'to_review'
            # 2) Si TODOS los revisores marcaron is_reviewed y estamos en to_review:
            if work.state == 'to_review' and work.reviewer_ids and all(r.is_reviewed for r in work.reviewer_ids):
                work.state = 'reviewed'

        return res

class WorkReviewer(models.Model):
    _name = 'work.reviewer'
    _description = 'Revisor de Trabajo'

    name = fields.Char(string='Título del Trabajo', related = 'work_id.name')
    work_id = fields.Many2one('scientific.work', string='Trabajo', required=True)
    reviewer_id = fields.Many2one('res.users', string='Revisor', required=True)
    opinion = fields.Text(string='Opinión')
    rating = fields.Float(string='Calificación', digits=(2, 1))
    is_reviewed = fields.Boolean(string='Revisado', default=False)
    attachment = fields.Binary(string='Archivo del Trabajo',related='work_id.attachment',readonly=False)
    attachment_filename = fields.Char(string='Nombre del Archivo',related='work_id.attachment_filename')

    def action_confirm_review(self):
        """Se llama desde el botón con confirm"""
        self.write({'is_reviewed': True})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Trabajos por Revisar',
            'res_model': 'work.reviewer',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('is_reviewed', '=', False)],
        }
