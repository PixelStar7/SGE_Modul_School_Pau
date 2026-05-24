# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.tools.sql import drop_view_if_exists

class SchoolYearCourseQtyEditions(models.Model):
    _name = 'school.year.course.qty.editions'
    _description = 'Year-Course-Editions statistics'
    _auto = False # Molt important!!! Això fa que Odoo no generi una taula d'aquesta classe!!!!
    _order = 'year desc, qty_editions desc, course_name'

    # Camps equivalents a les columnes de la vista SQL
    course_name = fields.Char(string='Course', size=60)
    year = fields.Integer(string="Year")
    qty_editions = fields.Integer(string="# Editions")

    # Per a crear la vista
    def init(self):
        # Eliminem la vista si ja existeix abans de recrear-la
        cr = self._cr
        drop_view_if_exists(cr, 'school_year_course_qty_editions')

        # Creació de la vista SQL
        self.env.cr.execute(
            """
                CREATE OR REPLACE VIEW school_year_course_qty_editions AS (
                    SELECT min(sce.id) as "id",
                           sc.name as "course_name",
                           date_part('year', sce.date_start) as "year",
                           count(*) as "qty_editions"
                    FROM school_course_edition sce
                    JOIN school_course sc ON sce.course_id = sc.id
                    GROUP BY sce.course_id, sc.name, date_part('year', sce.date_start)
                )
            """)
