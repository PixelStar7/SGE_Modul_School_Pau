# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError, UserError
from datetime import date
from dateutil.relativedelta import relativedelta

from ..utils import is_valid_email

class SchoolCourse(models.Model):
    _name = 'school.course' # Nom de la taula que crearà Odoo 
    _description = 'Course Management' # Nom més llegible de la taula
    _order = 'name'

    name = fields.Char('Name', size=60, required=True) # Size és la mida màxima
    hours = fields.Integer('Hours', required=True) # Required vol dir obligatori
    active = fields.Boolean('Active', default=True) # Default és el valor per defecte
    summary = fields.Html('Summary')

    # Relació Many2one: Un curs pot tenir un teacher, i un teacher pot tenir molts cursos.
    # No és required perquè és 0..1 // És required des de la versió 8.0
    manager_id = fields.Many2one('school.teacher', 'Manager', required=True,
                                  domain=['&', 
                                          ('country_id.code', '=', 'ES'),
                                          '|',
                                          ('active', '=', True),
                                          ('active', '=', False)])

    # Condicions domain (camp, operacio, valor)
    # Si no posem operador, es queda sempre '&'

    # Camps related, per aconseguir informació d'una relació
    manager_phone = fields.Char('Phone', related = 'manager_id.phone')
    manager_email = fields.Char('eMail', related = 'manager_id.email')
    manager_citizenship = fields.Many2one('res.country', 'Citizenship', related="manager_id.country_id")

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

    # Constrains Course
    @api.constrains('hours')
    def _check_hours(self):
        for course in self:
            if (course.hours <= 0):
                raise ValidationError(_('Course hours must be positive.'))

    # OnChange Course
    @api.onchange('name')
    def _onchange_name(self):
        if self.name != False:
            # Cal controlar que no sigui buit (quan es dona d'alta o modifica deixant-lo buit
            # ja que no es pot aplicar upper() sobre un "buit" (en realitat "False"))
            self.name = self.name.capitalize()


class SchoolSubject(models.Model):
    _name = 'school.subject'
    _description = 'Subject Management'
    _order = 'name'

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

    # Mètode comentat per l'addició del mètode write
    # @api.onchange('name')
    # def _onchange_name(self):
    #     if self.name != False:
    #         # Cal controlar que no sigui buit (quan es dona d'alta o modifica deixant-lo buit
    #         # ja que no es pot aplicar upper() sobre un "buit" (en realitat "False")
    #         self.name = self.name.capitalize()


    # Sobreescriptura del mètode create --> Quan es crea un Subject
    # Mètode auxiliar creat pel professor per no repetir codi a dins del write
    def _write_aux(self, values):
        # Busquem quins idiomes estan activats a la base de dades
        langs = self.env['res.lang'].search([('active', '=', True)])
        
        # Esbrinem quin és l'idioma de l'usuari que està connectat ara mateix
        usu_lang = self.env['res.users'].browse(self.env.uid).lang
        
        # Recorrem les assignatures afectades per la modificació
        for r in self:
            for lang in langs:
                # Només actuem si l'idioma no és el de l'usuari (perquè aquest ja s'ha fet al write principal)
                if lang.code != usu_lang:
                    # 'with_context(lang=lang.code)' fa que l'Odoo es pensi que som un usuari d'aquell idioma
                    aux = r.with_context(lang=lang.code).name
                    
                    if aux != False:
                        # Posem la primera lletra en majúscula
                        aux = aux.capitalize()
                        # I tornem a usar el context per guardar-ho directament a la traducció d'aquell idioma
                        r.with_context(lang=lang.code).write({'name': aux})

    def write(self, values):
        # Si s'està modificant el 'name', apliquem capitalize a l'idioma actual de l'usuari
        if 'name' in values and values['name']:
            values['name'] = values['name'].capitalize()
            
        # Fem el desament real cridant a la classe base
        r = super().write(values)
        
        # Si s'ha modificat el 'name', cridem la nostra funció auxiliar perquè arregli els altres idiomes
        if 'name' in values:
            self._write_aux(values)
            
        # Retornem si s'ha pogut guardar
        return r

class SchoolTeacher(models.Model):
    _name = 'school.teacher'
    _description = 'Teacher Management'
    _order = 'last_name,first_name'
    # Com no hi ha camp "name", haurem d'usar '_rec_name':
    # I si volem tenir el nom complet (first + last name), hem de programar _compute_display_name
    # _rec_name = 'full_name'
    # Si, en canvi, volem posar el display_name, treiem el rec_name...

    _sql_constraints=[
        ('ck_salari', 'check(salary >= 0)', 'Salary must be positive (controlled by DB)' '')
    ]
    # No és habitual incorporar una check a la BD. S'utilitzen les @api.constraints
    # on Odoo controla la restricció abans d'enviar la instrucció insert/update a la BD
    # Aixo només és un exemple acadèmic

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

    # Camps comptador
    course_count = fields.Integer('Courses Managed', compute='_compute_course_count')
    subject_count = fields.Integer('Subjects Authorized', compute='_compute_subject_count')
    teaching_count = fields.Integer('Teachings Assigned', compute='_compute_teaching_count')

    # Camps per calcular Aniversaris (Exercici Setmana Santa 1)
    current_birthday = fields.Date('Current Birthday', compute='_compute_birthday_info')
    celebrated_age = fields.Integer('Celebrated Age', compute='_compute_birthday_info')

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
    
    @api.depends('birthdate')
    def _compute_birthday_info(self):
        current_year = date.today().year
        for teacher in self:
            if teacher.birthdate:
                try:
                    # Intentem canviar només l'any de la data de naixement per l'any actual
                    teacher.current_birthday = teacher.birthdate.replace(year=current_year)
                except ValueError:
                    # Si peta, vol dir que va néixer un 29 de febrer i aquest any no és de traspàs!
                    # Passem l'aniversari a l'1 de març
                    teacher.current_birthday = date(current_year, 3, 1)
            
                # Calculem l'edat que celebra en aquesta data
                teacher.celebrated_age = current_year - teacher.birthdate.year
            else:
                teacher.current_birthday = False
                teacher.celebrated_age = 0

    

    # Constrains Teacher
    # Restriccions o checks sobre la classe Teacher
    # @api.constrains('salary')
    # def _check_salary(self):
    #     for teacher in self:
    #         if teacher.salary < 0:
    #             raise ValidationError(_('Salary must be positive.'))
    # Està comentada per què està introduïda a sql_constrints i així es pot comprovar
    # l'actuació quan s'infringeix la restricció
            
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
    
    # Mètode comentat per l'addició del create i write, més avall
    # @api.onchange("tin")
    # def _onchange_tin(self):
    #     if self.tin != False:
    #         # Cal controlar que no sigui buit (quan es dona d'alta o modifica deixant-lo buit
    #         # ja que no es pot aplicar upper() sobre un "buit" (en realitat "False")
    #         self.tin = self.tin.upper()
    
    def _auto_init(self):
        res = super(SchoolTeacher, self)._auto_init()
        tools.create_unique_index(self._cr, 'school_teacher_unique_tin', self.table, [('lower(tin)')])
        return res
    
    # Mètodes Compute per als comptadors
    @api.depends('course_ids')
    def _compute_course_count(self):
        for teacher in self:
            # Comptem quants elements té la llista One2Many
            teacher.course_count = len(teacher.course_ids)
    
    @api.depends('subject_ids')
    def _compute_subject_count(self):
        for teacher in self:
            # Comptem quants elements té la llista Many2Many
            teacher.subject_count = len(teacher.subject_ids)
    
    def _compute_teaching_count(self):
        for teacher in self:
            # Fem una consulta a la base de dades (search_count) a la taula school.teaching
            # Busquem els registres on el 'teacher_id' sigui igual a la ID d'aquest professor
            teacher.teaching_count = self.env['school.teaching'].search_count([('teacher_id', '=', teacher.id)])

    # Sobreescriptura del mètode unlink --> Quan s'esborra un Teacher
    def unlink(self):
        for teacher in self:
            # És manager d'algun curs?
            if (len(teacher.course_ids) > 0):
                # Si té cursos, no deixem borrar
                raise UserError(_("You cannot delete Teachers that have courses managed."))
            
            # Té teachings?
            teachings = self.env['school.teaching'].search([('teacher_id', '=', teacher.id)])

            # Si en té, les esborrem, cascade manual
            for t in teachings:
                t.unlink()
        
        # Ara si, borrem realment
        resultat = super().unlink()

        # Retornem true o false si s'ha pogut esborrar o no
        return resultat
    
    # Sobreescriptura del mètode create --> Quan es crea un Teacher
    @api.model_create_multi
    def create(self, vals_list):
        # vals_list és una llista de diccionaris. Cada diccionari és un professor nou.
        for vals in vals_list:
            # Comprovem si s'està enviant el camp 'tin' i si té algun valor
            if 'tin' in vals and vals['tin']:
                vals['tin'] = vals['tin'].upper() # Ho posem a majúscules
        
        # I cridem al mètode pare perquè faci la creació real a la BD
        return super().create(vals_list)


    # Sobreescriptura del mètode write --> Quan es modifica un Teacher
    def write(self, vals):
        # En el write, 'vals' és un unic diccionari amb els camps que S'HAN MODIFICAT
        if 'tin' in vals and vals['tin']:
            vals['tin'] = vals['tin'].upper()
        
        # Cridem al pare perquè guardi la modificació
        return super().write(vals)


class SchoolThematic(models.Model):
    _name = 'school.thematic'
    _description = 'Thematic Management'
    _order = 'name'

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

    @api.onchange('name')
    def _onchange_name(self):
        if self.name != False:
            # Cal controlar que no sigui buit (quan es dona d'alta o modifica deixant-lo buit
            # ja que no es pot aplicar upper() sobre un "buit" (en realitat "False")
            self.name = self.name.capitalize()


# ===== Classes N a M =====
class SchoolCourseEdition(models.Model):
    _name = 'school.course.edition'
    _description = 'Course Edition Management'
    _order = 'date_start' # Les edicions s'ordenen per data d'inici

    # SQL Constraints per evitar que un mateix curs tingui dues edicions començant el matetx dia
    _sql_constraints = [
        ('unique_course_date_start', 'unique(course_id, date_start)',
          _('It is not possible 2 course editions with the same course and start date.'))
    ]
    

    name = fields.Char('Name', size=60, required=True)
    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date') # No és obligatòria

    # Relació Many2one (CourseEdition --> Course).
    # Classe apuntada / nom de la relació
    course_id = fields.Many2one('school.course', 'Course', ondelete='cascade') # Si s'elimina un curs, s'eliminaràn les edicions del mateix

    # Camp calculat per a comptar els professors
    teacher_count = fields.Integer('Teacher count', compute='_compute_teacher_count')

    # Constrains CourseEdition
    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for courseEdition in self:
            if courseEdition.date_end != False:
                if courseEdition.date_end < courseEdition.date_start:
                    raise ValidationError(_('End date must be newer or equal than start date.'))

    # Mètode comentat per l'addició dels mètodes create i write
    # @api.onchange('name')
    # def _onchange_name(self):
    #     if self.name != False:
    #         # Cal controlar que no sigui buit (quan es dona d'alta o modifica deixant-lo buit
    #         # ja que no es pot aplicar upper() sobre un "buit" (en realitat "False")
    #         self.name = self.name.title()
    
    @api.depends('name', 'course_id')
    def _compute_display_name(self):
        for courseEdition in self:
            if courseEdition.name != False and courseEdition.course_id != False:
                # Mostrarà: "Nom Course - Nom Edició"
                courseEdition.display_name = courseEdition.course_id.name + " - " + courseEdition.name
            else:
                courseEdition.display_name = ''

    # Comptador de Professors
    def _compute_teacher_count(self):
        for edition in self:
            # Comptem quants registres a school.teaching tenen aquesta edition_id
            teachings = self.env['school.teaching'].search([('edition_id', '=', edition.id)])
            teachers = []

            for t in teachings:
                if t.teacher_id not in teachers:
                    teachers.append(t.teacher_id)
            
            edition.teacher_count = len(teachers)


    # Sobreescriptura del mètode create --> Quan es crea un CourseEdition
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' in vals and vals['name']:
                vals['name'] = vals['name'].title() # Ho posem a format Títol (Primeres lletres a majúscula)
        
        return super().create(vals_list)
    

    # Sobreescriptura del mètode write --> Quan es crea un CourseEdition
    def write(self, vals):
        if 'name' in vals and vals['name']:
            vals['name'] = vals['name'].title()
        
        return super().write(vals)


class SchoolCourseSubject(models.Model):
    _name = 'school.course.subject'
    _description = 'Course Subject Management'
    _order = 'number'

    # SQL Constraints per evitar duplicitat en la combinació de camps
    _sql_constraints = [
        ('course_subject_unique', 'unique(course_id, subject_id)', _('The subject in a course must be unique!')),
        ('course_number_unique', 'unique(course_id, number)', _('The number in a course must be unique!'))
    ]

    number = fields.Integer('Number', required=True)

    # Relació Many2one (CourseSubject --> Course).
    # Classe apuntada / nom de la relació
    course_id = fields.Many2one('school.course', 'Course', required=True, ondelete='cascade') # Si s'elimina un curs, s'eliminaràn les assignatures del mateix

    # Relació Many2one (CourseSubject --> Subject).
    # Classe apuntada / nom de la relació
    subject_id = fields.Many2one('school.subject', 'Subject', required=True, ondelete='restrict') # No es pot esborrar una assignatura si ja està assignada a un curs

    # Camp relacionat per portar les hores de l'assignatura a aquesta taula intermitja
    subject_hours = fields.Integer('Hours', related = 'subject_id.hours')


    # Constrains CourseSubject
    @api.constrains('number')
    def _check_number(self):
        for courseSubject in self:
            if courseSubject.number <= 0:
                raise ValidationError(_('Number must be positive.'))
    
    # Display_name de la taula sencera
    @api.depends('course_id', 'subject_id', 'number')
    def _compute_display_name(self):
        for courseSubject in self:
            if courseSubject.course_id != False and courseSubject.subject_id != False and courseSubject.number != False:
                # Mostrarà: "Nom course - 1 - Introducció"
                courseSubject.display_name = courseSubject.course_id.name + " - " + str(courseSubject.number) + " - " + courseSubject.subject_id.name
            else:
                courseSubject.display_name = ''


# ===== Classes Ternàries =====

# "Aquest PROFESSOR, en aquesta EDICIÓ concreta d'un curs, fa aquesta ASSIGNATURA"
class SchoolTeaching(models.Model):
    _name = 'school.teaching'
    _description = 'Teaching Management (Teacher-Subject-Edition)'

    # Qui fa la classe?
    teacher_id = fields.Many2one('school.teacher', 'Teacher', required=True)

    # En quina edició del curs? (Ex: Python Bàsic - Edició Octubre)
    edition_id = fields.Many2one('school.course.edition', 'Edition', required=True)

    # Camp relacionat per saber a quin curs pertany aquesta edició
    edition_course_id = fields.Many2one('school.course', related="edition_id.course_id")

    # Quina assignatura impartirà? (Apunta a la taula intermitja, no a l'assignatura)
    subject_id = fields.Many2one('school.course.subject', 'Subject', required=True)

    # Camp relacionat de "Doble Salt" per a tenir la llista de profes per a l'assignatura
    # Teaching -> CourseSubject (subject_id) -> Subject (subject_id) -> Teacher (teacher_ids)
    subject_teacher_ids = fields.Many2many('school.teacher', related='subject_id.subject_id.teacher_ids')