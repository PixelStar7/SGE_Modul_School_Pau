# -*- coding: utf-8 -*-

from odoo import models, fields


class SchoolCourse(models.Model):
    _name = 'school.course' # Nom de la taula que crearà Odoo 
    _description = 'Course Management' # Nom més llegible de la taula

    name = fields.Char('Name', size=60, required=True) # Size és la mida màxima
    hours = fields.Integer('Hours', required=True) # Required vol dir obligatori
    active = fields.Boolean('Active', default=True) # Default és el valor per defecte

    # Relació Many2one: Un curs pot tenir un teacher, i un teacher pot tenir molts cursos.
    manager_id = fields.Many2one('school.teacher', 'Manager') # No és required perquè és 0..1


class SchoolSubject(models.Model):
    _name = 'school.subject'
    _description = 'Subject Management'

    name = fields.Char('Name', size=60, required=True, translate=True) # S'ha de poder traduïr
    hours = fields.Integer('Hours', required=True)
    active = fields.Boolean('Active', default=True)


class SchoolTeacher(models.Model):
    _name = 'school.teacher'
    _description = 'Teacher Management'
    # Com no hi ha camp "name", haurem d'usar '_rec_name':
    # I si volem tenir el nom complet (first + last name), hem de programar _compute_display_name
    _rec_name = 'last_name'

    first_name = fields.Char('First Name', size=30, required=True)
    last_name = fields.Char('Last Name', size=40, required=True)
    birthdate = fields.Date('Birthdate', required=True) # Date per a les dates
    tin = fields.Char('Tax ID', size=14)

    # Llista desplegable fixa [(valor1, valor2)]
        # valor1 --> Clau interna de la BD [male]
        # valor2 --> El que veu l'usuari a la pantalla [Male]
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Gender')

    salary = fields.Integer('Salary')
    email = fields.Char('eMail', size=60, required=True)
    phone = fields.Char('Phone')

    # Relació One2many (Curs --> Professors).
    course_ids = fields.One2many('school.course', 'manager_id', 'Courses', readonly=True)