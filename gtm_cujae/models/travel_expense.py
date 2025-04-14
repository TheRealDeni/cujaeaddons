from odoo import models, fields


class TravelExpense(models.Model):
    _name = 'travel.expense'
    _description = "Registro de la información de los costos del viaje"

    ticket_cost = fields.Float(string="Costo del pasaje")
    taxes = fields.Float(string="Impuestos")
    diet_cost = fields.Float(string="Costos de dieta")
    accommodation_cost = fields.Float(string="Costos de alojamiento")
    medical_insurance_cost = fields.Float(string="Costos de seguro médico")
    pocket_money = fields.Float(string="Dinero de bolsillo (efectivo)")
    other_expenses = fields.Float(string="Otros gastos")
    other_expenses_specification = fields.Text(string="Especificación de otros gastos")
