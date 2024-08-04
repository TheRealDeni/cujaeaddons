from odoo import api, fields, models 

class GenInvoiceSuccess(models.TransientModel):

    _name = 'gen.invoice.success'

    _description = 'Successful generation of invoices'

    message = fields.Text(default="The invoices were generated successfully", readonly=True, store=True)