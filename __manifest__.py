# -*- coding: utf-8 -*-
{
    'name': 'School',
    'version': '24.0',
    'category': 'Education',
    'summary': 'School Management',
    'description': """
          Module prepared by department 'Informàtica i comunicacions'
          of Institute Milà i Fontanals in Igualada (Barcelona-Spain)
          for learning in development and adaptation of modules of Odoo ERP.

          It is part of the learning materials for the module
          'Sistemes de gestió empresarial' in the course
          'CFS Desenvolupament d''aplicacions multiplataforma'.
    """,
    'author': 'Group DAM2 - Course 2025-2026',
    'website': 'http://www.infomila.info',
    'depends': ['base', 'board', 'mail'],
    'data': [
        'security/school_security.xml', # Primer la definció dels grups de seguretat 
        'security/ir.model.access.csv', # Després les regles d'accés als models
        'views/school_views.xml',
        'report/school_report_qweb.xml',
        'report/exercici_report_qweb.xml',
        'wizard/how_many_editions_between_dates.xml',
        'views/school_year_course_qty_editions.xml',
        'views/school_dashboards.xml'
    ],
    'demo': [
        'data/school_demo.xml',
        'data/school_images_demo.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}