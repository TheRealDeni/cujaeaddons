from odoo import  models, fields


class TravelLoan(models.Model):
    _name = 'travel.loan'
    _description = 'Travel Loan'

    name = fields.Char(string='Name')
    travel_id = fields.Many2one('helpdesk.ticket', string='Solicitud de viaje asociada')
    loan_amount = fields.Float(string='Monto del préstamo')
    loan_concept = fields.Char(string='Concepto del préstamo')

