# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta

from ..utils import is_valid_email

class SchoolCourse(models.Model):
    _name = 'school.course' # Nom de la taula que crearà Odoo 
    _description = 'Course Management' # Nom més llegible de la taula

    name = fields.Char('Name', size=60, required=True) # Size és la mida màxima
    hours = fields.Integer('Hours', required=True) # Required vol dir obligatori
    active = fields.Boolean('Active', default=True) # Default és el valor per defecte
    summary = fields.Html('Summary')

    # Relació Many2one: Un curs pot tenir un teacher, i un teacher pot tenir molts cursos.
    manager_id = fields.Many2one('school.teacher', 'Manager', required=True) # No és required perquè és 0..1 // És required des de la versió 8.0

                                    # Relació ja no existent
    # Relació Many2many (Cursos --> Assignatures)
    # Nom de la taula que relacionarà / nom de la taula a crear / nom dels camps - de la nova taula / nom de la relació
    # El nom de la taula serà el mateix que en l'altre relació a "Subject", amb les ids canviades d'ordre.
    # subject_ids = fields.Many2many('school.subject', 'school_course_subject_rel', 'course_id', 'subject_id', 'Subjects', readonly=True)

    # Relació Many2one (Cursos --> Temàtica).
    # Classe apuntada / nom de la relació
    thematic_id = fields.Many2one('school.thematic', 'Thematic', required=True)

    # Relació One2many (Course --> CourseSubject).
    # Classe apuntada / camp de la classe apuntada que fa la relació / nom de la relació
    course_subject_ids = fields.One2many('school.course.subject', 'course_id', 'CourseSubject', readonly=True)

    # Relació One2many (Course --> CourseEdition).
    # Classe apuntada / camp de la classe apuntada que fa la relació / nom de la relació
    edition_ids = fields.One2many('school.course.edition', 'course_id', 'CourseEdition', readonly=True)

    # Constraints Course
    @api.constrains('hours')
    def _check_hours(self):
        for course in self:
            if (course.hours <= 0):
                raise ValidationError(_('Course hours must be positive.'))



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

                                    # Relació ja no existent
    # Relació Many2many (Assignatures --> Cursos)
    # Nom de la taula que relacionarà / nom de la taula a crear / nom dels camps - de la nova taula / nom de la relació
    # El nom de la taula serà el mateix que en l'altre relació a "Subject", amb les ids canviades d'ordre.
    # course_ids = fields.Many2many('school.course', 'school_course_subject_rel', 'subject_id', 'course_id', 'Courses', readonly=True)

    # Relació One2many (Subject --> CourseSubject).
    # Classe apuntada / camp de la classe apuntada que fa la relació / nom de la relació
    course_subject_ids = fields.One2many('school.course.subject', 'subject_id', 'CourseSubject', readonly=True)

    # Constraints Subject
    @api.constrains('hours')
    def _check_hours(self):
        for subject in self:
            if (subject.hours <= 0):
                raise ValidationError(_('Subject hours must be positive.'))


class SchoolTeacher(models.Model):
    _name = 'school.teacher'
    _description = 'Teacher Management'
    # Com no hi ha camp "name", haurem d'usar '_rec_name':
    # I si volem tenir el nom complet (first + last name), hem de programar _compute_display_name
    # _rec_name = 'full_name'
    # Si, en canvi, volem posar el display_name, treiem el rec_name...

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
    active = fields.Boolean('Active?', default=True)
    photo = fields.Binary('Photo')

    # Relació One2many (Professor --> Cursos).
    # Classe apuntada / camp de la classe apuntada que fa la relació / nom de la relació
    course_ids = fields.One2many('school.course', 'manager_id', 'Courses', readonly=True)

    # Relació Many2many (Professors --> Assignatures)
    # Nom de la taula que relacionarà / nom de la taula a crear / nom dels camps - de la nova taula / nom de la relació
    # El nom de la taula serà el mateix que en l'altre relació a "Subject", amb les ids canviades d'ordre.
    subject_ids = fields.Many2many('school.subject', 'school_teacher_subject_rel', 'teacher_id', 'subject_id', 'Subjects authorized', readonly=True)

    # Relació Many2one (Professors --> Nacionalitat).
    # Classe apuntada / camp de la classe apuntada que fa la relació / nom de la relació
    country_id = fields.Many2one('res.country', 'Citizenship', required=True)

    # Camps Calculats Teacher
    # Nom del camp calculat / Nom del mètode que ho computa
    # full_name = fields.Char('Full Name', compute='_compute_full_name')
    # Tret el camp calculat per que usem el display_name

    # Nom del camp calculat / Nom del mètode que ho computa
    age = fields.Integer('Age', compute='_compute_age')
    
    # Mètodes Teacher
    # La barra baixa '_' --> significa private
    # self és equivalent al this de Java;
    # és un conjunt de registres (RecordSet) sobre el que s'executarà el mètode.
    # @api.depends() marca amb la modificació de quins camps recalcularà el camp calculat.
    @api.depends('first_name', 'last_name')
    def _compute_display_name(self):
        for teacher in self:
            if teacher.last_name != False and teacher.first_name != False:
                # display_name és un camp d'Odoo directament
                teacher.display_name = teacher.last_name + ", " + teacher.first_name
            else:
                teacher.display_name = "Nou professor"


    @api.depends('birthdate')
    def _compute_age(self):
        avui = date.today()
        for teacher in self:
            if teacher.birthdate:
                teacher.age = relativedelta(avui, teacher.birthdate).years
            else:
                teacher.age = 0

    # Constrains Teacher
    # Restriccions o checks sobre la classe Teacher
    @api.constrains('salary')
    def _check_salary(self):
        for teacher in self:
            if teacher.salary < 0:
                raise ValidationError(_('Salary must be positive.'))
            
    @api.constrains('phone')
    def _check_phone(self):
        for teacher in self:
            if teacher.phone != False:
                for car in teacher.phone:
                    if car < '0' or car > '9':
                        raise ValidationError(_('Phone number must only have numbers.'))

    @api.constrains('email')
    def _check_email(self):
        for teacher in self:
            if is_valid_email(teacher.email) == False:
                raise ValidationError(_('Email is not valid.'))

class SchoolThematic(models.Model):
    _name = 'school.thematic'
    _description = 'Thematic Management'

    name = fields.Char('Name', size=60, required=True)

    # Relació One2many (Temàtica --> Cursos).
    # Classe apuntada / camp de la classe apuntada que fa la relació / nom de la relació
    course_ids = fields.One2many('school.course', 'manager_id', 'Courses', readonly=True)

    # Relació One2many (TemàticaFills --> TemàticaPare).
    # Classe apuntada / camp de la classe apuntada que fa la relació / nom de la relació
    child_ids = fields.One2many('school.thematic', 'parent_id', 'Child Thematics', readonly=True)

    # Relació Many2one (TemàticaPare --> TemàticaFills).
    # Classe apuntada / camp de la classe apuntada que fa la relació / nom de la relació
    parent_id = fields.Many2one('school.thematic', 'Parent Thematic')


    # Constrains Thematic
    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('Error! You cannot create recursive thematics.'))


# ===== Classes N a M =====
class SchoolCourseEdition(models.Model):
    _name = 'school.course.edition'
    _description = 'Course Edition Management'

    name = fields.Char('Name', size=60, required=True)
    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date') # No és obligatòria

    # Relació Many2one (CourseEdition --> Course).
    # Classe apuntada / nom de la relació
    course_id = fields.Many2one('school.course', 'Course', ondelete='cascade') # Si s'elimina un curs, s'eliminaràn les edicions del mateix

    # Constrains CourseEdition
    @api.constrains('date_end')
    def _check_date_end(self):
        for courseEdition in self:
            if courseEdition.date_end != False:
                if courseEdition.date_end < courseEdition.date_start:
                    raise ValidationError(_('End date must be newer or equal than start date.'))

class SchoolCourseSubject(models.Model):
    _name = 'school.course.subject'
    _description = 'Course Subject Management'

    number = fields.Integer('Number', required=True)

    # Relació Many2one (CourseSubject --> Course).
    # Classe apuntada / nom de la relació
    course_id = fields.Many2one('school.course', 'Course', ondelete='cascade', required=True) # Si s'elimina un curs, s'eliminaràn les assignatures del mateix

    # Relació Many2one (CourseSubject --> Subject).
    # Classe apuntada / nom de la relació
    subject_id = fields.Many2one('school.subject', 'Subject', required=True, ondelete='restrict') # No es pot esborrar una assignatura si ja està assignada a un curs

    # Constrains CourseSubject
    @api.constrains('number')
    def _check_number(self):
        for courseSubject in self:
            if courseSubject.number <= 0:
                raise ValidationError(_('Number must be positive.'))
    
    # TO DO Un curs no pot tenir dues assignatures amb el mateix number o repetides.