# coding=utf8
""" Upgrade 1.0.0 to 2.1.0

Handles taking the existing 1.0.0 data and converting it to a usable format in
2.1.0
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__version__		= "1.0.0"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2025-03-12"

# Ouroboros imports
from config import config
import jsonb
from strings import uuid_strip_dashes

# Python imports
from os.path import abspath, expanduser, exists

# Pip imports
from rest_mysql.Record_MySQL import Commands, DuplicateException, ESelect

# Local imports
from mouth.records import template, template_email, template_sms

def run():
	"""Run

	Main entry into the script, called by the upgrade module

	Returns:
		bool
	"""

	# Get Mouth data folder
	sDataPath = config.mouth.data('./.mouth')
	if '~' in sDataPath:
		sDataPath = expanduser(sDataPath)
	sDataPath = abspath(sDataPath)

	############################################################################
	# Template section

	# Get the templates struct
	dStruct = template.Template.struct()

	# Generate the name of the template changes backup file
	sTemplateChangesFile = '%s/mouth_v1_0_template_changes.json' % sDataPath

	# If the backup file already exists
	if exists(sTemplateChangesFile):

		# Load it
		lChangeRecords = jsonb.load(sTemplateChangesFile)

	# Else, no backups yet
	else:

		# Pull out all the records from the template changes table
		lChangeRecords = Commands.select(
			dStruct['host'],
			'SELECT `_id`, UNIX_TIMESTAMP(`created`) as `created`, `items` ' \
			'FROM `%(db)s`.`%(table)s_changes` ORDER BY `created`' % dStruct,
			ESelect.ALL
		)

		# Store them to a local file
		jsonb.store(lChangeRecords, sTemplateChangesFile)

	# Generate the name of the templates backup file
	sTemplatesFile = '%s/mouth_v1_0_templates.json' % sDataPath

	# If the backup file already exists
	if exists(sTemplatesFile):

		# Load it
		lRecords = jsonb.load(sTemplatesFile)

	# Else, no backup yet
	else:

		# Pull out all the records from the template table
		lRecords = Commands.select(
			dStruct['host'],
			'SELECT `_id`, ' \
				'UNIX_TIMESTAMP(`_created`) as `_created`, ' \
				'UNIX_TIMESTAMP(`_updated`) as `_updated`, ' \
				'`name`, `variables` ' \
			'FROM `%(db)s`.`%(table)s` ORDER BY `_created`' % dStruct,
			ESelect.ALL
		)

		# Store them to a local file
		jsonb.store(lRecords, sTemplatesFile)

		# Drop the table
		template.Template.table_drop()

		# Recreate the table
		template.Template.table_create()

	# Go through each record, convert the values, and add them
	for d in lRecords:
		try:
			d['_id'] = uuid_strip_dashes(d['_id'])
			d['variables'] = jsonb.decode(d['variables'])
			template.Template.create_now(d, changes = False)
		except DuplicateException as e:
			print(e.args)

	# Go through each changes record, convert the values, and add them
	for d in lChangeRecords:
		dStruct['_id'] = uuid_strip_dashes(d['_id'])
		dStruct['created'] = d['created']
		dStruct['items'] = Commands.escape(dStruct['host'], d['items'])
		sSQL = "INSERT INTO `%(db)s`.`%(table)s_changes` " \
					"(`_id`, `created`, `items`) " \
				"VALUES (UNHEX('%(_id)s'), FROM_UNIXTIME(%(created)s), " \
					"'%(items)s')" % dStruct
		Commands.execute(dStruct['host'], sSQL)

	############################################################################
	# Template Email section

	# Get the template_emails struct
	dStruct = template_email.TemplateEmail.struct()

	# Generate the name of the template email changes backup file
	sEmailChangesFile = '%s/mouth_v1_0_template_email_changes.json' % sDataPath

	# If the backup file already exists
	if exists(sEmailChangesFile):

		# Load it
		lChangeRecords = jsonb.load(sEmailChangesFile)

	# Else, no backups yet
	else:

		# Pull out all the records from the template email changes table
		lChangeRecords = Commands.select(
			dStruct['host'],
			'SELECT `_id`, UNIX_TIMESTAMP(`created`) as `created`, `items` ' \
			'FROM `%(db)s`.`%(table)s_changes` ORDER BY `created`' % dStruct,
			ESelect.ALL
		)

		# Store them to a local file
		jsonb.store(lChangeRecords, sEmailChangesFile)

	# Generate the name of the template_emails backup file
	sEmailsFile = '%s/mouth_v1_0_template_emails.json' % sDataPath

	# If the backup file already exists
	if exists(sEmailsFile):

		# Load it
		lRecords = jsonb.load(sEmailsFile)

	# Else, no backup yet
	else:

		# Pull out all the records from the template email table
		lRecords = Commands.select(
			dStruct['host'],
			'SELECT `_id`, ' \
				'UNIX_TIMESTAMP(`_created`) as `_created`, ' \
				'UNIX_TIMESTAMP(`_updated`) as `_updated`, ' \
				'`template`, `locale`, `subject`, `text`, `html` ' \
			'FROM `%(db)s`.`%(table)s` ORDER BY `_created`' % dStruct,
			ESelect.ALL
		)

		# Store them to a local file
		jsonb.store(lRecords, sEmailsFile)

		# Drop the table
		template_email.TemplateEmail.table_drop()

		# Recreate the table
		template_email.TemplateEmail.table_create()

	# Go through each record, convert the values, and add them
	for d in lRecords:
		try:
			d['_id'] = uuid_strip_dashes(d['_id'])
			d['template'] = uuid_strip_dashes(d['template'])
			template_email.TemplateEmail.create_now(d, changes = False)
		except DuplicateException as e:
			print(e.args)

	# Go through each changes record, convert the values, and add them
	for d in lChangeRecords:
		dStruct['_id'] = uuid_strip_dashes(d['_id'])
		dStruct['created'] = d['created']
		dStruct['items'] = Commands.escape(dStruct['host'], d['items'])
		sSQL = "INSERT INTO `%(db)s`.`%(table)s_changes` " \
					"(`_id`, `created`, `items`) " \
				"VALUES (UNHEX('%(_id)s'), FROM_UNIXTIME(%(created)s), " \
					"'%(items)s')" % dStruct
		Commands.execute(dStruct['host'], sSQL)

	############################################################################
	# Template SMS section

	# Get the template_sms struct
	dStruct = template_sms.TemplateSMS.struct()

	# Generate the name of the template sms changes backup file
	sSmsChangesFile = '%s/mouth_v1_0_template_sms_changes.json' % sDataPath

	# If the backup file already exists
	if exists(sSmsChangesFile):

		# Load it
		lChangeRecords = jsonb.load(sSmsChangesFile)

	# Else, no backups yet
	else:

		# Pull out all the records from the template sms changes table
		lChangeRecords = Commands.select(
			dStruct['host'],
			'SELECT `_id`, UNIX_TIMESTAMP(`created`) as `created`, `items` ' \
			'FROM `%(db)s`.`%(table)s_changes` ORDER BY `created`' % dStruct,
			ESelect.ALL
		)

		# Store them to a local file
		jsonb.store(lChangeRecords, sSmsChangesFile)

	# Generate the name of the template_sms backup file
	sTemplateSmsFile = '%s/mouth_v1_0_template_sms.json' % sDataPath

	# If the backup file already exists
	if exists(sTemplateSmsFile):

		# Load it
		lRecords = jsonb.load(sTemplateSmsFile)

	# Else, no backup yet
	else:

		# Pull out all the records from the template sms table
		lRecords = Commands.select(
			dStruct['host'],
			'SELECT `_id`, ' \
				'UNIX_TIMESTAMP(`_created`) as `_created`, ' \
				'UNIX_TIMESTAMP(`_updated`) as `_updated`, ' \
				'`template`, `locale`, `content` ' \
			'FROM `%(db)s`.`%(table)s` ORDER BY `_created`' % dStruct,
			ESelect.ALL
		)

		# Store them to a local file
		jsonb.store(lRecords, sTemplateSmsFile)

		# Drop the table
		template_sms.TemplateSMS.table_drop()

		# Recreate the table
		template_sms.TemplateSMS.table_create()

	# Go through each record, convert the values, and add them
	for d in lRecords:
		try:
			d['_id'] = uuid_strip_dashes(d['_id'])
			d['template'] = uuid_strip_dashes(d['template'])
			template_sms.TemplateSMS.create_now(d, changes = False)
		except DuplicateException as e:
			print(e.args)

	# Go through each changes record, convert the values, and add them
	for d in lChangeRecords:
		dStruct['_id'] = uuid_strip_dashes(d['_id'])
		dStruct['created'] = d['created']
		dStruct['items'] = Commands.escape(dStruct['host'], d['items'])
		sSQL = "INSERT INTO `%(db)s`.`%(table)s_changes` " \
					"(`_id`, `created`, `items`) " \
				"VALUES (UNHEX('%(_id)s'), FROM_UNIXTIME(%(created)s), " \
					"'%(items)s')" % dStruct
		Commands.execute(dStruct['host'], sSQL)

	# Return OK
	return True