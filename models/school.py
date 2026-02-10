# -*- coding: utf-8 -*-

from odoo import models, fields


class SchoolCourse(models.Model):
    _name = 'school.course' # Nom de la taula que crearà Odoo 
    _description = 'Course Management' # Nom més llegible de la taula

    name = fields.Char('Name', size=60, required=True) # Size és la mida màxima
    hours = fields.Integer('Hours', required=True) # Required vol dir obligatori
    active = fields.Boolean('Active', default=True) # Default és el valor per defecte

    # Relació Many2one: Un curs pot tenir un teacher, i un teacher pot tenir molts cursos.
    manager_id = fields.Many2one('school.teacher', 'Manager', readonly=True) # No és required perquè és 0..1

    # Relació Many2many (Cursos --> Assignatures)
    # Nom de la taula que relacionarà / nom de la taula a crear / nom dels camps - de la nova taula / nom de la relació
    # El nom de la taula serà el mateix que en l'altre relació a "Subject", amb les ids canviades d'ordre.
    subject_ids = fields.Many2many('school.subject', 'school_course_subject_rel', 'course_id', 'subject_id', 'Subjects', readonly=True)

    # Relació Many2one (Cursos --> Temàtica).
    # Classe apuntada / camp de la classe apuntada que fa la relació / nom de la relació
    thematic_id = fields.Many2one('school.thematic', 'Thematic', readonly=True)


class SchoolSubject(models.Model):
    _name = 'school.subject'
    _description = 'Subject Management'

    name = fields.Char('Name', size=60, required=True, translate=True) # S'ha de poder traduïr
    hours = fields.Integer('Hours', required=True)
    active = fields.Boolean('Active', default=True)

    # Relació Many2many (Assignatures --> Professors)
    # Nom de la taula que relacionarà / nom de la taula a crear / nom dels camps - de la nova taula / nom de la relació
    # El nom de la taula serà el mateix que en l'altre relació a "Teacher", amb les ids canviades d'ordre.
    teacher_ids = fields.Many2many('school.teacher', 'school_teacher_subject_rel', 'subject_id', 'teacher_id', 'Teachers Authorized', readonly=True)

    # Relació Many2many (Assignatures --> Cursos)
    # Nom de la taula que relacionarà / nom de la taula a crear / nom dels camps - de la nova taula / nom de la relació
    # El nom de la taula serà el mateix que en l'altre relació a "Subject", amb les ids canviades d'ordre.
    course_ids = fields.Many2many('school.course', 'school_course_subject_rel', 'subject_id', 'course_id', 'Courses', readonly=True)


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
    active = fields.Boolean('Active', default=True)

    # Relació One2many (Professor --> Cursos).
    # Classe apuntada / camp de la classe apuntada que fa la relació / nom de la relació
    course_ids = fields.One2many('school.course', 'manager_id', 'Courses', readonly=True)

    # Relació Many2many (Professors --> Assignatures)
    # Nom de la taula que relacionarà / nom de la taula a crear / nom dels camps - de la nova taula / nom de la relació
    # El nom de la taula serà el mateix que en l'altre relació a "Subject", amb les ids canviades d'ordre.
    subject_ids = fields.Many2many('school.subject', 'school_teacher_subject_rel', 'teacher_id', 'subject_id', 'Subjects', readonly=True)

    # Relació Many2one (Professors --> Nacionalitat).
    # Classe apuntada / camp de la classe apuntada que fa la relació / nom de la relació
    country_id = fields.Many2one('res.country', 'Citizenship', readonly=True)


class SchoolThematic(models.Model):
    _name = 'school.thematic'
    _description = 'Thematic Management'

    name = fields.Char('Name', size=30, required=True)

    # Relació One2many (Temàtica --> Cursos).
    # Classe apuntada / camp de la classe apuntada que fa la relació / nom de la relació
    course_ids = fields.One2many('school.course', 'manager_id', 'Courses', readonly=True)

    # Relació One2many (TemàticaFills --> TemàticaPare).
    # Classe apuntada / camp de la classe apuntada que fa la relació / nom de la relació
    child_ids = fields.One2many('school.thematic', 'parent_id', 'Child Thematics', readonly=True)

    # Relació Many2one (TemàticaPare --> TemàticaFills).
    # Classe apuntada / camp de la classe apuntada que fa la relació / nom de la relació
    parent_id = fields.Many2one('school.thematic', 'Parent Thematic', readonly=True, required=False)