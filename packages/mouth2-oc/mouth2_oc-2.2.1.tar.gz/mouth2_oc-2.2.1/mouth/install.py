# coding=utf8
""" Install

Method to install the necessary mouth tables
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__version__		= "1.0.0"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2024-12-14"

# Ouroboros imports
from config import config
from upgrade_oc import set_latest
from rest_mysql import Record_MySQL

# Python imports
from os.path import abspath, expanduser
from pathlib import Path

# Module imports
from mouth.records import locale, template, template_email, template_sms

def run() -> int:
	"""Run

	Entry point into the install process. Will installs required files, \
	tables, records, etc. for the service

	Returns:
		int
	"""

	# Notify
	print('Installing tables')

	# Install tables
	locale.Locale.table_create()
	template.Template.table_create()
	template_email.TemplateEmail.table_create()
	template_sms.TemplateSMS.table_create()

	# Notify
	print('Setting lastest version')

	# Get the path to the data folder
	sData = config.brain.data('./.data')
	if '~' in sData:
		sData = expanduser(sData)
	sData = abspath(sData)

	# Store the last known upgrade version
	set_latest(
		sData,
		Path(__file__).parent.resolve()
	)

	# Notify
	print('Done')

	# Return OK
	return 0