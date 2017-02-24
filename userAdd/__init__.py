# -*- coding: utf-8 -*-

from django.dispatch import receiver
from django.dispatch import Signal
from django.contrib import messages
from django.dispatch import receiver
from django.dispatch import Signal
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django_auth_ldap.backend import LDAPBackend

def ready(self):
	user_logged_in.connect(receiver, sender=User)
	user_logged_out.connect(receiver, sender=User)

# Listener Signals
@receiver([user_logged_in, user_logged_out], sender=User)
def log_user_activity(sender, **kwargs):
	signal = kwargs.get('signal', None)
	user = kwargs.get('user', None)
	request = kwargs.get('request', None)
	session_key = request.session.session_key

	if signal == user_logged_in:
		action = "login"
		messages.info(request, "¡Bienvenido!")
		create_page(user,'en')

	elif signal == user_logged_out:
		action = "logout"
		messages.info(request, '¡Hasta Otra!')

def create_page(user,lang):
	import cms.api
	from cms.models.pagemodel import Page
	from aldryn_newsblog.cms_appconfig import NewsBlogConfig, NewsBlogConfigTranslation
	try:
		if user.is_staff:
			group = "Profesores"
		else:
			group = "Alumnos"

		user_conf = NewsBlogConfig(app_title=user.username,namespace=user.username)
		user_conf.save_base()

		parent_page = Page.objects.filter(title_set__title=group)[0]

		page = cms.api.create_page(user.username,'fullwidth.html',lang,apphook="NewsBlogApp",apphook_namespace=user_conf.namespace,parent=parent_page,published=True,in_navigation=True)

		placeholder = page.placeholders.get(slot='feature')

		plugin1 = cms.api.add_plugin(placeholder,'StylePlugin',lang)
		plugin2 = cms.api.add_plugin(placeholder,'StylePlugin',lang)
		plugin2.class_name="feature-content"
		plugin2.save()

		page_user = cms.api.create_page_user(user, user, can_add_page=False, can_change_page=False, can_delete_page=False, can_recover_page=False, can_add_pageuser=False, can_change_pageuser=False, can_delete_pageuser=False, can_add_pagepermission=False, can_change_pagepermission=False, can_delete_pagepermission=False, grant_all=False)
	except:
		None
