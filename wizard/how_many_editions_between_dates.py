# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SchoolHowManyEditionsBetweenDates(models.TransientModel):
    _name = 'school.how.many.editions.between.dates'
    _description = 'Wizard to count editions between dates'

    course_id = fields.Many2one('school.course', 'Course', required=True)
    start_date_from = fields.Date('Start Date From', required=True)
    start_date_until = fields.Date('Start Date Until', required=True)
    n_editions = fields.Integer('#Editions', readonly=True)
    state = fields.Selection([('init', 'Init'), ('done', 'Done')], 'State', default='init')

    # El camp "state" és especial
    # L'usarem per indicar quins camps s'invisibilitzen, però en aquest cas podria tenir un altre nom

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for obj in self:
            if obj.start_date_until < obj.start_date_from:
                raise ValidationError(_('Start Date Until must be later or equal Start Date From'))

    def count_editions(self):
        # Per comptar les edicions d'un curs entre determinades dates, hem d'e fer un comptatge
        # de totes les edicions (dins school.course.edition) que són del curs demanat per l'usuari
        # i que la data d'inici del curs estigui entre les dates indicades per l'usuari
        # Per tant, necessitem accedir als recursos de SchoolCourseEdicion
        ce_obj = self.env['school.course.edition']
        # ce_obj és objecte que gestiona els recursos de CourseEdition
        n = ce_obj.search_count([('course_id.id', "=", self.course_id.id),
                                 ('date_start', ">=", self.start_date_from),
                                 ('date_start', '<=', self.start_date_until)])
        # Ja hem efectuat els càlculs. Per fer-los visibles, hem de modificar l'objecte
        # que està visualitzant el formulari
        self.write({'n_editions': n, 'state': 'done'})
        # Amb el següent "return" fem que recarregui el mateix formulari
        # i com que states="done", canviaran els camps visualitzats
        return {
            'name': 'Wizard to count editions before dates',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'res_model': 'school.how.many.editions.between.dates',
            'type': 'ir.actions.act_window',
        }
