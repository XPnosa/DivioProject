#-*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django_auth_ldap.backend import LDAPBackend

import json
import cms.api
from cms.models.pagemodel import Page
from aldryn_newsblog.cms_appconfig import NewsBlogConfig, NewsBlogConfigTranslation

class Command(BaseCommand):
	help = 'Creacion de perfiles de usuarios mediante un fichero JSON'

	def add_arguments(self, parser):
		parser.add_argument('fichero', nargs='?', type=str)

	def handle(self, *args, **options):
		print "Leyendo fichero: " + options['fichero']
		with open(options['fichero']) as data_file:    
			data = json.load(data_file)
			for key, value in data.iteritems():
				username = value["user"]
				group = value["group"]
				lang = value["lang"]
				try:
					user = LDAPBackend().populate_user(username)
					user_conf = NewsBlogConfig(app_title=user.username,namespace=user.username)
					user_conf.save_base()
					user_conf.create_translation(language_code=lang)
					parent_page = Page.objects.filter(title_set__title=group)[0]
					page = cms.api.create_page(user.username,'fullwidth.html',lang,apphook="NewsBlogApp",apphook_namespace=user_conf.namespace,parent=parent_page,published=True,in_navigation=True)
					placeholder = page.placeholders.get(slot='feature')
					plugin1 = cms.api.add_plugin(placeholder,'StylePlugin',lang)
					plugin2 = cms.api.add_plugin(placeholder,'StylePlugin',lang)
					plugin2.class_name="feature-content"
					plugin2.save()
					page_user = cms.api.create_page_user(user, user, can_add_page=False, can_change_page=False, can_delete_page=False, can_recover_page=False, can_add_pageuser=False, can_change_pageuser=False, can_delete_pageuser=False, can_add_pagepermission=False, can_change_pagepermission=False, can_delete_pagepermission=False, grant_all=False)
					print "Perfil '"+username+"' creado."
				except:
					print "¡Horror!"
