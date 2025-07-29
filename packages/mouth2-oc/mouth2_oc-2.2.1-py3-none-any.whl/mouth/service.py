# coding=utf8
""" Mouth Service

Handles communication
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__version__		= "1.0.0"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2023-01-05"

# Limit exports
__all__ = [ 'errors', 'Mouth' ]

# Ouroboros imports
from body import Error, Response, Service
from brain.helpers import access
from config import config
import em
from jobject import jobject
from rest_mysql.Record_MySQL import DuplicateException
from strings import to_bool
from tools import clone, evaluate
import undefined

# Python imports
from base64 import b64decode
from operator import itemgetter
import re

# Pip imports
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Records imports
from mouth.records.locale import Locale
from mouth.records.template import Template
from mouth.records.template_email import TemplateEmail
from mouth.records.template_sms import TemplateSMS

# Errors
from mouth import errors

class Mouth(Service):
	"""Mouth Service class

	Service for outgoing communication

	docs-file:
		rest

	docs-body:
		mouth
	"""

	_special_conditionals = {
		'$EMPTY': '',
		'$NULL': None
	}
	"""Special conditional values"""

	_re_if_else = re.compile(
		r'\[[\t ]*if[\t ]+([A-Za-z_]+)(?:[\t ]+(==|<|<=|>|>=|!=)[\t ]+([^\]]+))?[\t ]*\]\n?(.+?)\n?(?:\[[\t ]*else[\t ]*\]\n?(.+?)\n?)?\[[\t ]*fi[\t ]*\]',
		re.DOTALL
	)
	_re_data = re.compile(r'\{([A-Za-z_]+)\}')
	_re_tpl = re.compile(r'\#([A-Za-z_]+)\#')
	"""Regular expressions for parsing/replacing"""

	_conditional = {
		'==': lambda x, y: x == y,
		'<': lambda x, y: x < y,
		'<=': lambda x, y: x <= y,
		'>': lambda x, y: x > y,
		'>=': lambda x, y: x >= y,
		'!=': lambda x, y: x != y
	}
	"""Conditional lambdas"""

	@classmethod
	def _checkTemplateContent(cls, content, names, variables):
		"""Check Template Content

		Goes through template content and makes sure any variables or embedded \
		templates actually exist

		Arguments:
			content (dict): A dictionary of content type data
			names (dict): A list of content type names
			variables (dict): The list of valid variables

		Returns:
			list
		"""

		# Init a list of variables and inner templates
		lsTemplates = set()
		lsVariables = set()

		# Go through each of the content types
		for k in names:
			try:

				# Look for, and store, templates
				for sTpl in cls._re_tpl.findall(content[k]):
					lsTemplates.add(sTpl)

				# Look for, and store, variables
				for sVar in cls._re_data.findall(content[k]):
					lsVariables.add(sVar)

			except KeyError:
				pass

		# Init errors list
		lErrors = []

		# If there's any templates
		if lsTemplates:

			# Look for all of them
			lTemplates = [d['name'] for d in Template.filter({
				'name': list(lsTemplates)
			}, raw = ['name'])]

			# I f  the count doesn't match
			if len(lTemplates) != len(lsTemplates):

				# Get the missing templates
				for s in lsTemplates:
					if s not in lTemplates:
						lErrors.append(['template', s])

		# If there's any variables
		if lsVariables:

			# Go through each one
			for s in lsVariables:

				# If it's not in the templates list
				if s not in variables:
					lErrors.append(['variable', s])

		# Return errors (might be empty)
		return lErrors

	def _email(self, opts):
		"""Email

		Handles the actual sending of the email

		Arguments:
			opts (dict): The options used to generate and send the email

		Returns:
			Response
		"""

		# If the from is not set
		if 'from' not in opts:
			opts['from'] = self._dEmail['from']

		# If there's an attachment
		if 'attachments' in opts:

			# Make sure it's a list
			if not isinstance(opts['attachments'], (list,tuple)):
				opts['attachments'] = [opts['attachments']]

			# Loop through the attachments
			for i in range(len(opts['attachments'])):

				# If we didn't get a dictionary
				if not isinstance(opts['attachments'][i], dict):
					return Error(
						errors.ATTACHMENT_STRUCTURE, 'attachments.[%d]' % i
					)

				# If the fields are missing
				try:
					evaluate(
						opts['attachments'][i], ['body', 'filename']
					)
				except ValueError as e:
					return Error(
						errors.body.DATA_FIELDS,
						[['attachments.[%d].%s' % (i, s), 'invalid'] \
							for s in e.args]
					)

				# Try to decode the base64
				try:
					opts['attachments'][i]['body'] = b64decode(
						opts['attachments'][i]['body']
					)
				except TypeError:
					return Error(errors.ATTACHMENT_DECODE)

		# Only send if anyone is allowed, or the to is in the allowed
		if not self._dEmail['allowed'] or opts['to'] in self._dEmail['allowed']:

			# Set the to and subject
			sTo = opts.pop('to')
			if 'override' in self._dEmail and self._dEmail['override']:
				sTo = self._dEmail['override']
			sSubject = opts.pop('subject')

			# Send the e-mail
			iRes = em.send(sTo, sSubject, opts)

			# If there was an error
			if iRes != em.OK:
				return Response({
					'success': False,
					'error': '%i %s' % (iRes, em.last_error())
				})

		# Return OK
		return Response({ 'success': True })

	@classmethod
	def _generate_content(cls, content, variables):
		"""Generate Content

		Handles variables and conditionals in template content as it's the \
		same logic for Emails and SMSs

		Arguments:
			content (str): The content to render
			variables (dict of str:mixed): The variable names and values

		Returns:
			str
		"""

		# Look for variables
		for sVar in cls._re_data.findall(content):

			# Replace the string with the data value
			content = content.replace(
				'{%s}' % sVar,
				sVar in variables and \
					str(variables[sVar]) or \
					'!!!{%s} does not exist!!!' % sVar
			)

		# Look for if/else conditionals
		for oConditional in cls._re_if_else.finditer(content):

			# Get the entire text to replace
			sReplace = oConditional.group(0)

			# Get the conditional parts
			sVariable, sTest, mValue, sIf, sElse = oConditional.groups()

			# Get the groups and the length
			lGroups = list(oConditional.groups())

			# If we have no test or value
			if sTest is None and mValue is None:

				# Get the status of the variable
				bPassed = sVariable in variables and variables[sVariable]

				# Figure out the replacement content
				sNewContent = bPassed and sIf or (sElse or '')

				# Replace the content
				content = content.replace(sReplace, sNewContent)

			# Else, we have a condition and value to run
			else:

				# Replace special tags in variable value
				for n,v in cls._special_conditionals.items():
					if mValue == n:
						mValue = v

				# Check for the variable
				if sVariable not in variables:
					content = content.replace(
						sReplace,
						'INVALID VARIABLE (%s) IN CONDITIONAL' % sVariable
					)
					continue

				# If we didn't get None for the value
				if mValue is not None:

					# Get the type of value for the variable
					oVarType = type(variables[sVariable])

					# Attempt to convert the value from a string if required
					try:

						# If it's a bool
						if oVarType == bool:
							mValue = to_bool(mValue)

						# Else, if it's not a string
						elif oVarType != str and oVarType != None:
							mValue = oVarType(mValue)

					# If we can't convert the value
					except ValueError:
						content = content.replace(
							sReplace,
							'%s HAS INVALID VALUE IN CONDITIONAL' % sVariable
						)
						continue

				# Figure out if the condition passed or not
				bPassed = cls._conditional[lGroups[cls.COND_TYPE]](
					variables[sVariable], mValue
				)

				# Figure out the replacement content
				sNewContent = bPassed and lGroups[cls.COND_IF_CONTENT] or (
					lGroups[cls.COND_ELSE_CONTENT] or ''
				)

				# Replace the conditional with the inner text if it passed, else
				#	just remove it
				content = content.replace(sReplace, sNewContent)

		# Return new content
		return content

	@classmethod
	def _generate_email(cls, content, locale, variables, templates=None):
		"""Generate Email

		Takes content, locale, and variables, and renders the final result of \
		the three parts of the email template

		Arguments:
			content (dict of str:str): The content to be rendered, 'subject', \
										'text', and 'html'
			locale (str): The locale used for embedded templates
			variables (dict of str:str): The variable names and their values
			templates (dict of str:str): The templates already looked up

		Returns:
			dict of str:str
		"""

		# If there's no templates yet
		if not templates:
			templates = {}

		# Copy the contents
		dContent = clone(content)

		# Go through each each part of the template
		for s in [ 'subject', 'text', 'html' ]:

			# If the part is somehow missing
			if s not in dContent:
				dContent[s] = '!!!%s missing!!!' % s
				continue

			# Look for embedded templates
			for sTpl in cls._re_tpl.findall(dContent[s]):

				# If we don't have the template yet
				if sTpl not in templates:

					# Look for the primary template
					dTemplate = Template.filter({
						'name': sTpl
					}, raw = ['_id'], limit = 1)

 					# If it doesn't exist
					if not dTemplate:
						templates[sTpl] = {
							'subject': '!!!#%s# does not exist!!!' % sTpl,
							'text': '!!!#%s# does not exist!!!' % sTpl,
							'html': '!!!#%s# does not exist!!!' % sTpl
						}

					# Else
					else:

						# Look for the locale dContent
						dEmail = TemplateEmail.filter({
							'template': dTemplate['_id'],
							'locale': locale
						}, raw = ['subject', 'text' ,  'html'], limit = 1)

						# If it doesn't exist
						if not dEmail:
							templates[sTpl] = {
								'subject': '!!!#%s.%s# does not exist!!!' % (
									sTpl, locale
								),
								'text': '!!!#%s.%s# does not exist!!!' % (
									sTpl, locale
								),
								'html': '!!!#%s.%s# does not exist!!!' % (
									sTpl, locale
								)
							}

						# Else, generate the embedded template
						else:
							templates[sTpl] = cls._generate_email(
								dEmail, locale, variables, templates
							)

				# Replace the string with the value from the child
				dContent[s] = dContent[s].replace(
					'#%s#' % sTpl, templates[sTpl][s]
				)

			# Handle the variables and conditionals
			dContent[s] = cls._generate_content(dContent[s], variables)

		# Return the new contents
		return dContent

	@classmethod
	def _generate_sms(cls, content, locale, variables, templates = undefined):
		"""Generate SMS

		Takes content, locale, and variables, and renders the final result of \
		the template

		Arguments:
			content (str): The content to be rendered
			locale (str): The locale used for embedded templates
			variables (dict of str:str): The variable names and their values
			templates (dict of str:str): The templates already looked up

		Returns:
			str
		"""

		# If there's no templates yet
		if templates is undefined:
			templates = {}

		# Look for embedded templates
		for sTpl in cls._re_tpl.findall(content):

			# If we don't have the template yet
			if sTpl not in templates:

				# Look for the primary template
				dTemplate = Template.filter({
					'name': sTpl
				}, raw = ['_id'], limit = 1)

				# If it doesn't exist
				if not dTemplate:
					templates[sTpl] = '!!!#%s# does not exist!!!' % sTpl

				# Else
				else:

					# Look for the locale dContent
					dSMS = TemplateSMS.filter({
						'template': dTemplate['_id'],
						'locale': locale
					}, raw = ['content'], limit = 1)

					# If it doesn't exist
					if not dSMS:
						templates[sTpl] = '!!!#%s.%s# does not exist!!!' % (
							sTpl, locale
						)

					# Else, generate the embedded template
					else:
						templates[sTpl] = cls._generate_sms(
							dSMS['content'], locale, variables, templates
						)

			# Replace the string with the value from the child
			content = content.replace('#%s#' % sTpl, templates[sTpl])

		# Handle the variables and conditionals
		content = cls._generate_content(content, variables)

		# Return the new contents
		return content

	def _sms(self, opts):
		"""SMS

		Sends an SMS using twilio

		Arguments:
			opts (dict): The options used to generate and send the SMS

		Returns:
			Response
		"""

		# Only send if anyone is allowed, or the to is in the allowed
		if not self._dSMS['allowed'] or opts['to'] in self._dSMS['allowed']:

			# Init the base arguments
			dArgs = {
				'to': 'override' in self._dSMS and \
						self._dSMS['override'] or \
						opts['to'],
				'body': opts['content']
			}

			# If we are using a service
			if 'messaging_sid' in self._dSMS['twilio']:
				dArgs['messaging_service_sid'] = \
					self._dSMS['twilio']['messaging_sid']

			# Else, use a phone number
			else:
				dArgs['from_'] = self._dSMS['twilio']['from_number']

			# Try to send the message via Twilio
			try:
				dRes = self._oTwilio.messages.create(**dArgs)

				# Return ok
				return Response({
					'success': True,
					'sid': dRes.sid
				})

			# Catch any Twilio exceptions
			except TwilioRestException as e:

				# Return failure
				return Response({
					'success': False,
					'error': [v for v in e.args]
				})

	def email_create(self, req: jobject) -> Response:
		"""E-Mail create

		Sends out an email to the requested email address given the correct
		locale and template, or content. This request can only be called
		wrapped in an internal key.

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			POST email

		Example:
			```python
			from body import create
			from brain.helpers import access

			create('mouth', 'email', access.generate_key({ 'data': {
			  'to': 'chris@somedomain.com',
			  'template': {
			    'name': 'setup',
			    'locale': 'en-US',
			    'variables': {
			      'name': 'Chris',
			      'key': '123456',
			      'other': '...'
			    }
			  }
			} }))
			```

		Data:
			to, string, no, The address to send the email to
			attachments, array, yes, The optional list of files to attach to the email
			attachments[].body, base64, no, The body of the attachment, required for each attachment
			attachments[].filename, string, no, The filename of the attachment, required for each attachment
			content, object, yes, The raw content to send, required if not using `template`
			content.subject, string, no, The subject if sending raw content
			content.text, string, yes, The text/plain content of the email, one of this or `content.html` must be set
			content.html, string, yes, The text/html content of the email, one of this or `content.text` must be set
			template, object, yes, The template to send, required if not using `content`
			template._id, string, yes, The ID of the template, required if `template.name` is not passed
			template.name, string, yes, The name of the template, required if `template._id` is not passed
			template.locale, string, no, The locale used to generate the template
			template.variables, object, no, The variables required for the template

		Response:
			success, bool, The result of sending the email via SMTP
			error, string, Only passed if success is `false`

		Response Example:
			{
			  "data": {
			    "success": true
			  }
			}

		Error:
			1001, DATA_FIELDS, Data sent to the request is missing or invalid
			1100, DB_NO_RECORD, Failed to find the template by name or locale
			1203, INTERNAL_KEY, Failed to find or decode the internal key
		"""

		# Check for internal key
		access.internal(req)

		# Make sure that at minimum, we have a to field
		if 'to' not in req.data:
			return Error(errors.body.DATA_FIELDS, [ [ 'to', 'missing' ] ])

		# Init the email options
		dEmail = {
			'to': req.data.to.strip()
		}

		# If we have attachments
		if 'attachments' in req.data:

			# Add them to the email
			dEmail['attachments'] = req.data.attachments

		# If we received a template field
		if 'template' in req.data:

			# Check minimum fields
			try:
				evaluate(
					req.data.template, [ 'locale', 'variables' ]
				)
			except ValueError as e:
				return Error(
					errors.body.DATA_FIELDS,
					[ [ 'template.%s' % f, 'missing' ] for f in e.args ]
				)

			# If we have an id
			if '_id' in req.data.template:

				# Store the ID
				sID = req.data.template._id

			# Else, if we have a name
			elif 'name' in req.data.template:

				# Find the template by name
				dTemplate = Template.filter({
					'name': req.data.template.name
				}, raw = ['_id'], limit = 1)

 				# If it's not found
				if not dTemplate:
					return Error(
						errors.body.DB_NO_RECORD,
						[ req.data.template.name, 'template' ]
					)

				# Store the ID
				sID = dTemplate['_id']

			# Else, no way to find the template
			else:
				return Error(
					errors.body.DATA_FIELDS,
					[ [ 'name', 'missing' ] ]
				)

			# Find the content by locale
			dContent = TemplateEmail.filter({
				'template': sID,
				'locale': req.data.template.locale
			}, raw = [ 'subject', 'text', 'html' ], limit = 1)
			if not dContent:
				return Error(
					errors.body.DB_NO_RECORD, [
						'%s.%s' % (
							sID, req.data.template.locale
						),
						'template'
					]
				)

			# Generate the rendered content
			dContent = self._generate_email(
				dContent,
				req.data.template.locale,
				req.data.template.variables
			)

		# Else, if we recieved content
		elif 'content' in req.data:
			dContent = req.data.content

		# Else, nothing to send
		else:
			return Error(errors.body.DATA_FIELDS, [ [ 'content', 'missing' ] ])

		# Add it to the email
		dEmail['subject'] = dContent['subject']
		dEmail['text'] = dContent['text']
		dEmail['html'] = dContent['html']

		# Send the email and return the response
		return self._email(dEmail)

	def reset(self):
		"""Reset

		Called to reset the config and connections

		Returns:
			Mouth
		"""

		# Fetch and store Email config
		self._dEmail = config.email({
			'allowed': None,
			'from': 'support@localehost',
			'override': None
		})

		# Fetch and store SMS config
		self._dSMS = config.sms({
			'active': False,
			'allowed': None,
			'override': None,
			'twilio': {
				'account_sid': '',
				'token': '',
				'from_number': ''
			}
		})

		# If SMS is active
		if self._dSMS['active']:

			# Create Twilio client
			self._oTwilio = Client(
				self._dSMS['twilio']['account_sid'],
				self._dSMS['twilio']['token']
			)

		# Return self for chaining
		return self

	def sms_create(self, req: jobject) -> Response:
		"""SMS create

		Sends out an SMS to the requested phone number given the correct locale
		and template, or content. This request can only be called wrapped in an
		internal key.

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			POST sms

		Example:
			```python
			from body import create
			from brain.helpers import access

			create('mouth', 'sms', access.generate_key({ 'data': {
			  'to': '+15145551289',
			  'template': {
			    'name': 'setup',
			    'locale': 'en-US',
			    'variables': {
			      'name': 'Chris',
			      'key': '123456',
			      'other': '...'
			    }
			  }
			} }))
			```

		Data:
			to, string, no, The phone number to send the SMS to
			content, string, yes, The raw content to send, required if not using `template`
			template, object, yes, The template to send, required if not using `content`
			template._id, string, yes, The ID of the template, required if `template.name` is not passed
			template.name, string, yes, The name of the template, required if `template._id` is not passed
			template.locale, string, no, The locale used to generate the template
			template.variables, object, no, The variables required for the template

		Data Example:


		Response:
			success, bool, The result of sending the email via SMTP,
			sid, string, The ID of the sms, only passed if success is `true`
			error, string, Only passed if success is `false`

		Response Example:
			{
			  "data": {
			    "success": true,
			    "sid": "7d2c3cac52c711f0a922236bb031e5e7"
			  }
			}

		Error:
			1001, DATA_FIELDS, Data sent to the request is missing or invalid
			1100, DB_NO_RECORD, Failed to find the template by name or locale
			1203, INTERNAL_KEY, Failed to find or decode the internal key
		"""

		# Check for internal key
		access.internal(req)

		# Make sure that at minimum, we have a to field
		if 'to' not in req.data:
			return Error(errors.body.DATA_FIELDS, [ [ 'to', 'missing' ] ])

		# If we received a template field
		if 'template' in req.data:

			# Check minimum fields
			try:
				evaluate(
					req.data.template, [ 'locale', 'variables' ]
				)
			except ValueError as e:
				return Error(
					errors.body.DATA_FIELDS,
					[['template.%s' % f, 'missing'] for f in e.args]
				)

			# If we have an id
			if '_id' in req.data.template:

				# Store the ID
				sID = req.data._id

			# Else, if we have a name
			elif 'name' in req.data.template:

				# Find the template by name
				dTemplate = Template.filter({
					'name': req.data.template.name
				}, raw = [ '_id' ], limit = 1)

 				# If it's not found
				if not dTemplate:
					return Error(
						errors.body.DB_NO_RECORD,
						[ req.data.template.name, 'template' ]
					)

				# Store the ID
				sID = dTemplate['_id']

			# Else, no way to find the template
			else:
				return Error(
					errors.body.DATA_FIELDS,
					[ [ 'name', 'missing' ] ]
				)

			# Find the content by locale
			dContent = TemplateSMS.filter({
				'template': sID,
				'locale': req.data.template.locale
			}, raw = [ 'content' ], limit = 1)
			if not dContent:
				return Error(
					errors.body.DB_NO_RECORD, [
						'%s.%s' % (
							sID, req.data.template.locale
						),
						'template'
					]
				)

			# Generate the rendered content
			sContent = self._generate_sms(
				dContent['content'],
				req.data.template.locale,
				req.data.template.variables
			)

		# Else, if we recieved content
		elif 'content' in req.data:
			sContent = req.data.content

		# Else, nothing to send
		else:
			return Error(errors.body.DATA_FIELDS, [ [ 'content', 'missing' ] ])

		# Send the sms and return the response
		return self._sms({
			'to': req.data.to,
			'content': sContent
		})

	def locale_create(self, req: jobject) -> Response:
		"""Locale create

		Creates a new Locale record instance in the system.

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			POST locale

		Data:
			_id, string, no, The ID of the locale in the format [a-z]{2}-[A-Z]{2}, i.e. en-US, fr-CA, sp-ES
			name, string, no, The name of the locale to identify it

		Data Example:
			{
			  "_id": "en-CA",
			  "name": "English (Canada)"
			}

		Response:
			`true` on success, else an error.

		Response Example:
			{ "data": true }

		Error:
			1000, RIGHTS, The user lacks the rights to create a locale
			1001, DATA_FIELDS, Missing or invalid data passed
			1101, DB_DUPLICATE, The ID or name has already been used
		"""

		# Make sure the client has access via the session
		access.verify(
			req.session, { 'name': 'mouth_locale', 'right': access.CREATE }
		)

		# Verify the instance
		try:
			oLocale = Locale(req.data)
		except ValueError as e:
			return Error(errors.body.DATA_FIELDS, e.args[0])

		# If it's valid data, try to add it to the DB
		try:
			oLocale.create()
		except DuplicateException as e:
			return Error(errors.body.DB_DUPLICATE, 'locale')

		# Return OK
		return Response(True)

	def locale_delete(self, req: jobject) -> Response:
		"""Locale delete

		Deletes (or archives) an existing locale record instance.

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			DELETE locale

		Data:
			_id, string, no, The ID of the locale to delete
			archive, bool, yes, Set to true to archive the locale instead of deleting it

		Data Example:
			{
			  "_id": "en-CA"
			}

		Response:
			`true` | `false` on DB success, else an error code

		Response Example:
			{ "data": true }

		Error:
			1000, RIGHTS, The user lacks the rights to delete a locale
			1001, DATA_FIELDS, Missing or invalid data passed
			1100, DB_NO_RECORD, The request template does not exist
			1105, DB_KEY_BEING_USED, The template can't be deleted due to existing child locale templates
		"""

		# Make sure the client has access via the session
		access.verify(
			req.session, { 'name': 'mouth_locale', 'right': access.DELETE }
		)

		# Make sure we have an ID
		if '_id' not in req.data:
			return Error(errors.body.DATA_FIELDS, [ [ '_id', 'missing' ] ])

		# Look for the instance
		oLocale = Locale.get(req.data._id)

		# If it doesn't exist
		if not oLocale:
			return Error(
				errors.body.DB_NO_RECORD,
				[ req.data._id, 'locale' ]
			)

		# If it's being archived
		if 'archive' in req.data and req.data.archive:

			# Mark the record as archived
			oLocale['_archived'] = True

			# Save it in the DB and return the result
			return Response(
				oLocale.save()
			)

		# Check for templates with the locale
		if TemplateEmail.count(filter = { 'locale': oLocale['_id'] }) or \
			TemplateSMS.count(filter = { 'locale': oLocale['_id'] }):

			# Return an error because we have existing templates still using the
			#	locale
			return Error(
				errors.body.DB_KEY_BEING_USED, [ oLocale['_id'], 'locale' ]
			)

		# Delete the record and return the result
		return Response(
			oLocale.delete()
		)

	def locale_exists_read(self, req: jobject) -> Response:
		"""Locale Exists read

		Returns true if one or all locales exists.

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			GET locale/exists

		Data:
			_id, str | str[], no, The ID(s) of the locale(s) to check for

		Data Example:
			{ "_id": "en-CA" }

		Response:
			`true` if the locale(s) exist, else, `false`

		Response Example:
			{ "data": true }

		Error:
			1001, DATA_FIELDS, Missing or invalid data passed
		"""

		# If the ID is missing
		if '_id' not in req.data:
			return Error(errors.body.DATA_FIELDS, [ [ '_id', 'missing' ] ])

		# If we got an array
		if isinstance(req.data._id, list):

			# If the list is empty
			if not req.data._id:
				return Response(False)

			# Get the IDs
			lRecords = Locale.get(req.data._id, raw = [ '_id' ])

			# Return OK if the counts match
			return Response(
				len(lRecords) == len(req.data._id)
			)

		# Return if it exists or not
		return Response(
			Locale.exists(req.data._id)
		)

	def locale_read(self, req: jobject) -> Response:
		"""Locale read

		Returns an existing locale record, all active locales, or all locales.

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			GET locale

		Data:
			_id, string, yes, The ID of the specific locale to get
			archived, bool, yes, Set to true to return all locales instead of just the active (non-archived) ones

		Data Example:
			{ "_id": "en-CA" }

		Response:
			One or more locale objects

		Response Example:
			{
			  "data": {
			    "_id": "en-CA",
			    "_archived": false,
			    "_created": 1750969986,
			    "name": "English (Canada)",
			  }
			}

		Error:
			1000, RIGHTS, The user lacks the rights to read locales
			1100, DB_NO_RECORD, The specific locale requested does not exist
		"""

		# Make sure the client has access via the session
		access.verify(
			req.session, { 'name': 'mouth_locale', 'right': access.READ }
		)

		# If we have data
		if 'data' in req:

			# If there's an ID
			if '_id' in req.data:

				# Fetch the record
				dLocale = Locale.get(req.data._id, raw = True)

				# If it doesn't exist
				if not dLocale:
					return Error(
						errors.body.DB_NO_RECORD, [ req.data._id, 'locale' ]
					)

				# Return the raw data
				return Response(dLocale)

		# If we want to include archived
		if 'archived' in req.data and req.data.archived:

			# Get and return all locales as raw data
			return Response(
				Locale.get(raw = True, orderby='name')
			)

		# Else, return only those not marked as archived
		return Response(
			Locale.get(filter={'_archived': False}, raw = True, orderby='name')
		)

	def locale_update(self, req: jobject) -> Response:
		"""Locale update

		Updates an existing locale record instance, though technically the only
		field that can be updated is the name.

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			PUT locale

		Data:
			_id, string, no, The ID of the locale to update
			name, string, no, The new name of the locale

		Data Example:
			{
			  "_id": "en-CA",
			  "name": "Canadian / English"
			}

		Response:
			`true` on success, else an error

		Response Example:
			{ "data": true }

		Error:
			1000, RIGHTS, The user lacks the rights to update locales
			1001, DATA_FIELDS, Missing or invalid data passed
			1100, DB_NO_RECORD, The ID request doesn't exist
			1101, DB_DUPLICATE, The name conflicts with another record
			1106, DB_ARCHIVED, The record exists but is archived
		"""

		# Make sure the client has access via the session
		access.verify(
			req.session, { 'name': 'mouth_locale', 'right': access.UPDATE }
		)

		# Check minimum fields
		try:
			evaluate(req.data, ['_id', 'name'])
		except ValueError as e:
			return Error(
				errors.body.DATA_FIELDS, [[f, 'missing'] for f in e.args]
			)

		# Find the record
		oLocale = Locale.get(req.data._id)

		# If it doesn't exist
		if not oLocale:
			return Error(errors.body.DB_NO_RECORD, (req.data._id, 'locale'))

		# If it's archived
		if oLocale['_archived']:
			return Error(errors.body.DB_ARCHIVED, (req.data._id, 'locale'))

		# Try to update the name
		try:
			oLocale['name'] = req.data.name
		except ValueError as e:
			return Error(errors.body.DATA_FIELDS, [ e.args[0] ])

		# Save the record and return the result
		try:
			return Response(
				oLocale.save()
			)
		except DuplicateException as e:
			return Error(
				errors.body.DB_DUPLICATE, [ req.data.name, 'template' ])

	def locales_read(self, req: jobject) -> Response:
		"""Locales read

		Returns the list of valid locales without any requirement for being
		signed in.

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			GET locales

		Data:
			archived, bool, yes, Optionally set this to `true` to include archived locales

		Response:
			_id, string, The ID of the locale
			name, string, The name of the locale

		Response Example:
			{
			  "data": [ {
			    "_id": "en-CA",
			    "name": "Canadian / English"
			  } ]
			}
		"""

		# Get and return the ID and name of all active locales as a name ordered
		#	list
		return Response(
			Locale.filter({
				'_archived': False
			}, raw = [ '_id', 'name' ], orderby = 'name')
		)

	def template_create(self, req: jobject) -> Response:
		"""Template create

		Creates a new Template record instance in the DB.

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			POST template

		Data:
			name, string, no, The name of the new Template
			variables, object, no, A key / example store of the acceptable variables for the template

		Data Example:
			{
			  "name": "forgot password",
			  "variables": {
			    "email": "first.last@test.com",
			    "name": "First Last",
			    "url": "https://test.com/forgot/reset/a247e"
			  }
			}

		Response:
			Returns the new trimmed UUID of the Template on success, else an error

		Response Example:
			{ "data": "3369bc9c536f11f086f7c1bd71fea541" }

		Error:
			1000, RIGHTS, The user lacks the rights to create a Template
			1001, DATA_FIELDS, Missing or invalid data passed
			1101, DB_DUPLICATE, The name conflicts with an existing Template
		"""

		# Make sure the client has access via either an internal key, or via the
		#	session
		sUserID = access.internal_or_verify(
			req, { 'name': 'mouth_template', 'right': access.CREATE }
		)

		# If the name is missing
		if 'name' not in req.data:
			return Error(errors.body.DATA_FIELDS, [ [ 'name', 'missing' ] ])

		# Verify the instance
		try:
			oTemplate = Template(req.data)
		except ValueError as e:
			return Error(errors.body.DATA_FIELDS, e.args[0])

		# If it's valid data, try to add it to the DB
		try:
			oTemplate.create(changes = { 'user': sUserID })
		except DuplicateException as e:
			return Error(errors.body.DB_DUPLICATE, 'template')

		# Return the ID to indicate OK
		return Response(oTemplate['_id'])

	def template_delete(self, req: jobject) -> Response:
		"""Template delete

		Deletes an existing template record instance and all locale instances
		associated with it. Be very careful doing this, as this service has no
		way of knowing what other services require templates.

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			DELETE template

		Data:
			_id, string, no, The ID of the template to delete

		Data Example:
			{ "_id": "3369bc9c536f11f086f7c1bd71fea541" }

		Response:
			Returns `true` | `false` on DB result, else an error

		Response Example:
			{ "data": true }

		Error:
			1000, RIGHTS, The user lacks the rights to delete Templates
			1001, DATA_FIELDS, Missing or invalid data passed
			1100, DB_NO_RECORD, The ID requested doesn't exist
		"""

		# Make sure the client has access via the session
		sUserID = access.internal_or_verify(
			req, { 'name': 'mouth_template', 'right': access.DELETE }
		)

		# If the ID is missing
		if '_id' not in req.data:
			return Error(errors.body.DATA_FIELDS, [ [ '_id', 'missing' ] ])

		# Find the record
		oTemplate = Template.get(req.data._id)

		# If it's not found
		if not oTemplate:
			return Error(
				errors.body.DB_NO_RECORD, (req.data._id, 'template')
			)

		# For each email template associated
		for o in TemplateEmail.filter({
			'template': req.data._id
		}):

			# Delete it
			o.delete(changes = { 'user': sUserID })

		# For each sms template associated
		for o in TemplateSMS.filter({
			'template': req.data._id
		}):

			# Delete it
			o.delete(changes = { 'user': sUserID })

		# Delete the template and return the result
		return Response(
			oTemplate.delete(changes = { 'user': sUserID })
		)

	def template_read(self, req: jobject) -> Response:
		"""Template read

		Fetches and returns the template with the associated content records

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			GET template

		Data:
			_id, string, no, The ID of the Template to fetch

		Data Example:
			{ "_id": "3369bc9c536f11f086f7c1bd71fea541" }

		Response:
			_id, string, The ID of the Template
			_created, timestamp, The second in time the Template was created
			_updated, timestamp, The second in time the Template was last updated
			name, string, The name of the Template
			variables, object, The key / example values available for the Template
			contents, array, The list of locale content sub-Template objects available for the Template (See individual types for an idea of the expected data)
			contents[]._id, string, The ID of the locale sub-Template
			contents[]._created, timestamp, The second in time the sub-Template was created
			contents[]._updated, timestamp, The second in time the sub-Template was last updated
			contents[].template, string, The ID you requested originally
			contents[].locale, string, The locale associated with the sub-Template
			contents[].type, string, The type of sub-Template

		Response Example:
			{
			  "data": {
			    "_id": "3369bc9c536f11f086f7c1bd71fea541",
			    "_created": 1751041150,
			    "_updated": 1751041150,
			    "name": "forgot password",
			    "variables": {
			      "email": "first.last@test.com",
			      "name": "First Last",
			      "url": "https://test.com/forgot/reset/a247e"
			    },
			    "contents": [ {
			      "_id": "71539ff5537411f086f7c1bd71fea541",
			      "_created": 1751041296,
			      "_updated": 1751041296,
			      "template": "3369bc9c536f11f086f7c1bd71fea541",
			      "locale": "en-CA",
			      "subject": "Password Reset Request",
			      "text": "Hi {name}, click this {url}",
			      "html": "<p>Hi {name}, <a href=\\"{url}\\">click here</a> to reset your password</p>",
			      "type": "email"
			    } ]
			  }
			}

		Error:
			1000, RIGHTS, The user lacks the rights to read Templates
			1001, DATA_FIELDS, Missing or invalid data passed
			1100, DB_NO_RECORD, The ID requested does not exist
		"""

		# Make sure the client has access via the session
		access.internal_or_verify(
			req, { 'name': 'mouth_template', 'right': access.READ }
		)

		# If the ID is missing
		if '_id' not in req.data:
			return Error(errors.body.DATA_FIELDS, [ [ '_id', 'missing' ] ])

		# Find the record
		dTemplate = Template.get(req.data._id, raw = True)

		# If we got a list
		if isinstance(dTemplate, list):

			# If the counts don't match
			if len(req.data._id) != len(dTemplate):
				return Error(
					errors.body.DB_NO_RECORD, [req.data._id, 'template']
				)

			# Fetch all email templates with the IDs
			lEmails = TemplateEmail.filter({
				'template': req.data._id
			}, raw = True)

			# Go through each email and store it by it's template
			dEmails = {}
			for d in lEmails:
				d['type'] = 'email'
				try:
					dEmails[d['template']].append(d)
				except KeyError:
					dEmails[d['template']] = [d]

			# Fetch all email templates with the IDs
			lSMSs = TemplateSMS.filter({
				'template': req.data._id
			}, raw = True)

			# Go through each email and store it by it's template
			dSMSs = {}
			for d in lSMSs:
				d['type'] = 'sms'
				try:
					dSMSs[d['template']].append(d)
				except KeyError:
					dSMSs[d['template']] = [d]

			# Go through each template and add the emails and sms messages
			for d in dTemplate:
				d['content'] = []

				# Add the email templates
				if d['_id'] in dEmails:
					d['content'].extend(dEmails[d['_id']])

				# Add the SMS templates
				if d['_id'] in dSMSs:
					d['content'].extend(dSMSs[d['_id']])

				# If there's content
				if len(d['content']) > 1:

					# Sort it by locale and type
					d['content'].sort(key=itemgetter('locale', 'type'))

		# Else, it's most likely one
		else:

			# if it doesn't exist
			if not dTemplate:
				return Error(
					errors.body.DB_NO_RECORD, (req.data._id, 'template')
				)

			# Init the list of content
			dTemplate['content'] = []

			# Find all associated email content
			dTemplate['content'].extend([
				dict(d, type='email') for d in
				TemplateEmail.filter({
					'template': req.data._id
				}, raw = True)
			])

			# Find all associated sms content
			dTemplate['content'].extend([
				dict(d, type='sms') for d in
				TemplateSMS.filter({
					'template': req.data._id
				}, raw = True)
			])

			# If there's content
			if len(dTemplate['content']) > 1:

				# Sort it by locale and type
				dTemplate['content'].sort(key=itemgetter('locale', 'type'))

		# Return the template
		return Response(dTemplate)

	def template_update(self, req: jobject) -> Response:
		"""Template update

		Updates an existing Template record instance. In the example we are
		removing the "email" variable since it is not being used.

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			PUT template

		Data:
			_id, string, no, The ID of the Template to update
			name, string, yes, The name of the new Template
			variables, object, yes, A key / example store of the acceptable variables for the template

		Data Example:
			{
			  "_id": "",
			  "name": "forgot password",
			  "variables": {
			    "name": "First Last",
			    "url": "https://test.com/forgot/reset/a247e"
			  }
			}

		Response:
			Returns `true` | `false` on DB result, else an error

		Response Example:
			{ "data": true }

		Error:
			1000, RIGHTS, The user lacks the rights to update Templates
			1001, DATA_FIELDS, Missing or invalid data passed
			1100, DB_NO_RECORD, The ID requested does not exist
			1101, DB_DUPLICATE, The new name conflicts with an existing Template
		"""

		# Make sure the client has access via the session
		sUserID = access.internal_or_verify(
			req, { 'name': 'mouth_template', 'right': access.UPDATE }
		)

		# Check for ID
		if '_id' not in req.data:
			return Error(errors.body.DATA_FIELDS, [ [ '_id', 'missing' ] ])

		# Find the record
		oTemplate = Template.get(req.data._id)

		# If it doesn't exist
		if not oTemplate:
			return Error(
				errors.body.DB_NO_RECORD, [ req.data._id, 'template' ]
			)

		# Remove fields that can't be updated
		for k in ['_id', '_created', '_updated']:
			try: del req.data[k]
			except KeyError: pass

		# If there's nothing left
		if not req.data:
			return Response(False)

		# Init errors list
		lErrors = []

		# Update remaining fields
		for k in req.data:
			try:
				oTemplate[k] = req.data[k]
			except ValueError as e:
				lErrors.extend(e.args[0])

		# Save the record and return the result
		try:
			return Response(
				oTemplate.save(changes = { 'user': sUserID })
			)
		except DuplicateException as e:
			return Error(
				errors.body.DB_DUPLICATE, [ req.data.name, 'template' ]
			)

	def template_contents_read(self, req: jobject) -> Response:
		"""Template Contents read

		Returns all the content records for a single template. The response
		variables listed below should be consider only the list of mandatory
		variables, as each Template type will contain it's own variables which
		will be included alongside the listed ones.

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			GET template/contents

		Data:
			_id, string, no, The ID of the template to find contents for

		Data Example:
			{ "_id": "3369bc9c536f11f086f7c1bd71fea541" }

		Response:
			[]._id, string, The ID of the locale sub-Template
			[]._created, timestamp, The second in time the sub-Template was created
			[]._updated, timestamp, The second in time the sub-Template was last updated
			[].template, string, The ID you requested originally
			[].locale, string, The locale associated with the sub-Template
			[].type, string, The type of sub-Template

		Response Example:
			{
			  "data": [ {
			    "_id": "71539ff5537411f086f7c1bd71fea541",
			    "_created": 1751041296,
			    "_updated": 1751041296,
			    "template": "3369bc9c536f11f086f7c1bd71fea541",
			    "locale": "en-CA",
			    "subject": "Password Reset Request",
			    "text": "Hi {name}, click this {url}",
			    "html": "<p>Hi {name}, <a href=\\"{url}\\">click here</a> to reset your password</p>",
			    "type": "email"
			  } ]
			}

		Error:
			1000, RIGHTS, The user lacks the rights to read Templates
			1001, DATA_FIELDS, Missing or invalid data passed
			1100, DB_NO_RECORD, The ID requested does not exist
		"""

		# Make sure the client has access via the session
		access.internal_or_verify(
			req, { 'name': 'mouth_content', 'right': access.READ }
		)

		# If 'template' is missing
		if 'template' not in req.data:
			return Error(errors.body.DATA_FIELDS, [ [ 'template', 'missing' ] ])

		# If the template doesn't exist
		if not Template.exists(req.data.template):
			return Error(
				errors.body.DB_NO_RECORD, [ req.data.template, 'template' ]
			)

		# Init the list of content
		lContents = []

		# Find all associated email content
		lContents.extend([
			dict(d, type = 'email') for d in
			TemplateEmail.filter({
				'template': req.data.template
			}, raw = True)
		])

		# Find all associated sms content
		lContents.extend([
			dict(d, type = 'sms') for d in
			TemplateSMS.filter({
				'template': req.data.template
			}, raw = True)
		])

		# If there's content
		if len(lContents) > 1:

			# Sort it by locale and type
			lContents.sort(key = itemgetter('locale', 'type'))

		# Return the template
		return Response(lContents)

	def template_email_create(self, req: jobject) -> Response:
		"""Template Email create

		Adds an email content record to an existing template record instance by
		locale.

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			POST template/email

		Data:
			template, string, no, The ID of the Template to add to
			locale, string, no, The locale associated
			subject, string, no, The subject of the email
			text, string, no, The text/plain version of the email
			html, string, no, The text/html version of the email

		Data Example:
			{
			  "template": "3369bc9c536f11f086f7c1bd71fea541",
			  "locale": "en-CA",
			  "subject": "Password Reset Request",
			  "text": "Hi {name}, click this {url}",
			  "html": "<p>Hi {name}, <a href=\\"{url}\\">click here</a> to reset your password</p>"
			}

		Response:
			Returns the ID of the new email content record, else an error

		Response Example:
			{ "data": "71539ff5537411f086f7c1bd71fea541" }

		Error:
			1000, RIGHTS, The user lacks the rights to create sub-Templates
			1001, DATA_FIELDS, Missing or invalid data passed
			1100, DB_NO_RECORD, The template or locale requested does not exist
			1101, DB_DUPLICATE, The locale is already used in the template
			1300, TEMPLATE_CONTENT_ERROR, The template has errors related to variables or imports
		"""

		# Make sure the client has access via the session
		sUserID = access.internal_or_verify(
			req, { 'name': 'mouth_content', 'right': access.CREATE }
		)

		# Check minimum fields
		try:
			evaluate(req.data, [ 'template', 'locale' ])
		except ValueError as e:
			return Error(
				errors.body.DATA_FIELDS, [ [ f, 'missing' ] for f in e.args ]
			)

		# Make sure the template exists
		dTemplate = Template.get(req.data.template, raw = [ 'variables' ])
		if not dTemplate:
			return Error(
				errors.body.DB_NO_RECORD, [ req.data.template, 'template' ]
			)

		# Make sure the locale exists
		if not Locale.exists(req.data.locale):
			return Error(
				errors.body.DB_NO_RECORD, [ req.data.locale, 'locale' ]
			)

		# Verify the instance
		try:
			oEmail = TemplateEmail(req.data)
		except ValueError as e:
			return Error(errors.body.DATA_FIELDS, e.args[0])

		# Check content for errors
		lErrors = self._checkTemplateContent(
			req.data,
			[ 'subject', 'text', 'html' ],
			dTemplate[ 'variables' ]
		)

		# If there's any errors
		if lErrors:
			return Error(errors.TEMPLATE_CONTENT_ERROR, lErrors)

		# Create the record
		try:
			oEmail.create(changes = { 'user': sUserID })
		except DuplicateException as e:
			return Error(
				errors.body.DB_DUPLICATE,
				[ req.data.locale, 'template_locale' ]
			)

		# Return the ID to indicate OK
		return Response(oEmail['_id'])

	def template_email_delete(self, req: jobject) -> Response:
		"""Template Email delete

		Deletes email content from an existing template record instance.

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			DELETE template/email

		Data:
			_id, string, no, The ID of the email content record to delete

		Data Example:
			{ "_id": "71539ff5537411f086f7c1bd71fea541" }

		Response:
			Returns `true` | `false` on DB result, else an error

		Response Example:
			{ "data": true }

		Error:
			1000, RIGHTS, The user lacks the rights to delete sub-Templates
			1001, DATA_FIELDS, Missing or invalid data passed
			1100, DB_NO_RECORD, The ID requested doesn't exist
		"""

		# Make sure the client has access via the session
		sUserID = access.internal_or_verify(
			req, { 'name': 'mouth_content', 'right': access.DELETE }
		)

		# If the ID is missing
		if '_id' not in req.data:
			return Error(errors.body.DATA_FIELDS, [ [ '_id', 'missing' ] ])

		# Find the record
		oEmail = TemplateEmail.get(req.data._id)

		# If it doesn't exist
		if not oEmail:
			return Error(
				errors.body.DB_NO_RECORD,
				[ req.data._id, 'template_email' ]
			)

		# Delete the record and return the result
		return Response(
			oEmail.delete(changes = { 'user': sUserID })
		)

	def template_email_update(self, req: jobject) -> Response:
		"""Template Email update

		Updated email content of an existing template record instance by locale.

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			PUT template/email

		Data:
			_id, string, no, The ID of the sub-Template to update
			subject, string, yes, The subject of the email
			text, string, yes, The text/plain version of the email
			html, string, yes, The text/html version of the email

		Data Example:
			{
			  "_id": "71539ff5537411f086f7c1bd71fea541",
			  "subject": "Password forgot request"
			}

		Response:
			Returns `true` | `false` on DB result, else an error

		Response Example:
			{ "data": true }

		Error:
			1000, RIGHTS, The user lacks the rights to update Templates
			1001, DATA_FIELDS, Missing or invalid data passed
			1100, DB_NO_RECORD, The ID requested does not exist
			1300, TEMPLATE_CONTENT_ERROR, The template has errors related to variables or imports
		"""

		# Make sure the client has access via the session
		sUserID = access.internal_or_verify(
			req, { 'name': 'mouth_content', 'right': access.UPDATE }
		)

		# If the ID is missing
		if '_id' not in req.data:
			return Error(errors.body.DATA_FIELDS, [ [ '_id', 'missing' ] ])

		# Find the record
		oEmail = TemplateEmail.get(req.data._id)

		# If it doesn't exist
		if not oEmail:
			return Error(
				errors.body.DB_NO_RECORD, [ req.data._id, 'template_email' ]
			)

		# Remove fields that can't be updated
		for k in [ '_id', '_created', '_updated', 'template', 'locale' ]:
			try: del req.data[k]
			except KeyError: pass

		# If there's nothing left
		if not req.data:
			return Response(False)

		# Init errors list
		lErrors = []

		# Update remaining fields
		for k in req.data:
			try:
				oEmail[k] = req.data[k]
			except ValueError as e:
				lErrors.extend(e.args[0])

		# If there's any errors
		if lErrors:
			return Error(errors.body.DATA_FIELDS, lErrors)

		# Find the primary template variables
		dTemplate = Template.get(oEmail['template'], raw = [ 'variables' ])

	 	 # Check content for errors
		lErrors = self._checkTemplateContent(
			req.data,
			[ 'subject', 'text', 'html' ],
			dTemplate[ 'variables' ]
		)

		# If there's any errors
		if lErrors:
			return Error(errors.TEMPLATE_CONTENT_ERROR, lErrors)

		# Save the record and return the result
		return Response(
			oEmail.save(changes = { 'user': sUserID })
		)

	def template_email_generate_create(self, req: jobject) -> Response:
		"""Template Email Generate create

		Generates and returns a template from the base variable data for the
		purposes of testing and / or validating.

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			POST template/email/generate

		Data:
			template, string, no, The ID of the template to generate
			locale, string, no, The locale to generate the template in
			subject, string, yes, The subject of the email to test
			text, string, no, The text/plain version of the email to test
			html, string, no, The text/html version of the email to test

		Data Example:
			{
			  "template": "3369bc9c536f11f086f7c1bd71fea541",
			  "locale": "en-CA",
			  "subject": "Password Reset Request",
			  "text": "Hi {name}, click this {url}",
			  "html": "<p>Hi {name}, <a href=\\"{url}\\">click here</a> to reset your password</p>"
			}

		Response:
			subject, str, The generated subject
			text, str, The generated text/plain
			html, str, The generated text/html

		Response Example:
			{
			  "data": {
			    "subject": "Forgot Password Request",
			    "text": "Hi First Last, click this https://test.com/forgot/reset/a247e",
			    "html": "<p>Hi First Last, <a href=\\"https://test.com/forgot/reset/a247e\\">click here</a> to reset your password</p>"
			  }
			}

		Error:
			1000, RIGHTS, The user lacks rights to read sub-Templates
			1001, DATA_FIELDS, Missing or invalid data passed
			1100, DB_NO_RECORD, The template or locale does not exist
		"""

		# Make sure the client has access via the session
		access.internal_or_verify(
			req, { 'name': 'mouth_content', 'right': access.READ }
		)

		# Check minimum fields
		try:
			evaluate(req.data, [ 'template', 'locale', 'text', 'html' ])
		except ValueError as e:
			return Error(
				errors.body.DATA_FIELDS, [ [ f, 'missing' ] for f in e.args ]
			)

		# If the subject isn't passed
		if 'subject' not in req.data:
			req.data.subject = ''

		# Find the template variables
		dTemplate = Template.get(req.data.template, raw = [ 'variables' ])
		if not dTemplate:
			return Error(
				errors.body.DB_NO_RECORD, [ req.data.template, 'template' ]
			)

		# If the locale doesn't exist
		if not Locale.exists(req.data.locale):
			return Error(
				errors.body.DB_NO_RECORD, [ req.data.locale, 'locale' ]
			)

		# Generate the template and return it
		return Response(
			self._generate_email({
				'subject': req.data.subject,
				'text': req.data.text,
				'html': req.data.html
			}, req.data.locale, dTemplate[ 'variables' ])
		)

	def template_sms_create(self, req: jobject) -> Response:
		"""Template SMS create

		Adds an sms content record to an existing template record instance

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			POST template/sms

		Data:
			template, string, no, The ID of the Template to add to
			locale, string, no, The locale associated
			content, string, no, The content of the sms

		Data Example:
			{
			  "template": "f63b6cba538011f086f7c1bd71fea541",
			  "locale": "en-US",
			  "content": "You have {count} new notifications!"
			}

		Response:
			Returns the ID of the new sms content record, else an error

		Response Example:
			{ "data": "00114302538111f086f7c1bd71fea541" }

		Error:
			1000, RIGHTS, The user lacks the rights to create sub-Templates
			1001, DATA_FIELDS, Missing or invalid data passed
			1100, DB_NO_RECORD, The template or locale requested does not exist
			1101, DB_DUPLICATE, The locale is already used in the template
			1300, TEMPLATE_CONTENT_ERROR, The template has errors related to variables or imports
		"""

		# Make sure the client has access via the session
		sUserID = access.internal_or_verify(
			req, { 'name': 'mouth_content', 'right': access.CREATE }
		)

		# Check minimum fields
		try: evaluate(req.data, ['template', 'locale'])
		except ValueError as e:
			return Error(
				errors.body.DATA_FIELDS, [[f, 'missing'] for f in e.args]
			)

		# Make sure the template exists
		dTemplate = Template.get(req.data.template, raw = [ 'variables' ])
		if not dTemplate:
			return Error(
				errors.body.DB_NO_RECORD, [ req.data.template, 'template' ]
			)

		# Make sure the locale exists
		if not Locale.exists(req.data.locale):
			return Error(
				errors.body.DB_NO_RECORD, [ req.data.locale, 'locale' ]
			)

		# Verify the instance
		try:
			oSMS = TemplateSMS(req.data)
		except ValueError as e:
			return Error(errors.body.DATA_FIELDS, e.args[0])

		# Check content for errors
		lErrors = self._checkTemplateContent(
			req.data,
			[ 'content' ],
			dTemplate[ 'variables' ]
		)

		# If there's any errors
		if lErrors:
			return Error(errors.TEMPLATE_CONTENT_ERROR, lErrors)

		# Create the record
		try:
			oSMS.create(changes = { 'user': sUserID })
		except DuplicateException as e:
			return Error(
				errors.body.DB_DUPLICATE,
				[ req.data.locale, 'template_locale' ]
			)

		# Return the ID to indicate OK
		return Response(oSMS['_id'])

	def template_sms_delete(self, req: jobject) -> Response:
		"""Template SMS delete

		Deletes sms content from an existing template record instance

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			DELETE template/sms

		Data:
			_id, string, no, The ID of the sms content record to delete

		Data Example:
			{ "_id": "00114302538111f086f7c1bd71fea541" }

		Response:
			Returns `true` | `false` on DB result, else an error

		Response Example:
			{ "data": true }

		Error:
			1000, RIGHTS, The user lacks the rights to delete sub-Templates
			1001, DATA_FIELDS, Missing or invalid data passed
			1100, DB_NO_RECORD, The ID requested doesn't exist
		"""

		# Make sure the client has access via the session
		sUserID = access.internal_or_verify(
			req, { 'name': 'mouth_content', 'right': access.DELETE }
		)

		# If the ID is missing
		if '_id' not in req.data:
			return Error(errors.body.DATA_FIELDS, [ [ '_id', 'missing' ] ])

		# Find the record
		oSMS = TemplateSMS.get(req.data._id)

		# If it doesn't exist
		if not oSMS:
			return Error(
				errors.body.DB_NO_RECORD, [ req.data._id, 'template_sms' ]
			)

		# Delete the record and return the result
		return Response(
			oSMS.delete(changes = { 'user': sUserID })
		)

	def template_sms_update(self, req: jobject) -> Response:
		"""Template SMS update

		Updated sms content of an existing template record instance

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			PUT template/sms

		Data:
			_id, string, no, The ID of the sub-Template to update
			content, string, yes, The content of the sms

		Data Example:
			{
			  "_id": "00114302538111f086f7c1bd71fea541",
			  "content": "You have {count} notification(s) waiting for you!"
			}

		Response:
			Returns `true` | `false` on DB result, else an error

		Response Example:
			{ "data": true }

		Error:
			1000, RIGHTS, The user lacks the rights to update Templates
			1001, DATA_FIELDS, Missing or invalid data passed
			1100, DB_NO_RECORD, The ID requested does not exist
			1300, TEMPLATE_CONTENT_ERROR, The template has errors related to variables or imports
		"""

		# Make sure the client has access via the session
		sUserID = access.internal_or_verify(
			req, { 'name': 'mouth_content', 'right': access.UPDATE }
		)

		# Check minimum fields
		try: evaluate(req.data, [ '_id', 'content' ])
		except ValueError as e:
			return Error(
				errors.body.DATA_FIELDS, [ [ f, 'missing' ] for f in e.args ]
			)

		# Find the record
		oSMS = TemplateSMS.get(req.data._id)

		# If it doesn't exist
		if not oSMS:
			return Error(
				errors.body.DB_NO_RECORD, [ req.data._id, 'template_sms' ]
			)

		# Update the content
		try:
			oSMS['content'] = req.data.content
		except ValueError as e:
			return Error(errors.body.DATA_FIELDS, [ e.args[0] ])

		# Find the primary template variables
		dTemplate = Template.get(oSMS['template'], raw = [ 'variables' ])

		# Check content for errors
		lErrors = self._checkTemplateContent(
			req.data,
			[ 'content' ],
			dTemplate[ 'variables' ]
		)

		# If there's any errors
		if lErrors:
			return Error(errors.TEMPLATE_CONTENT_ERROR, lErrors)

		# Save the record and return the result
		return Response(
			oSMS.save(changes = { 'user': sUserID })
		)

	def template_sms_generate_create(self, req: jobject) -> Response:
		"""Template SMS Generate create

		Generates and returns a template from the base variable data for the
		purposes of testing and / or validating.

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			POST template/sms/generate

		Data:
			template, string, no, The ID of the template to generate
			locale, string, no, The locale to generate the template in
			content, string, yes, The content of the sms to test

		Data Example:
			{
			  "template": "00114302538111f086f7c1bd71fea541",
			  "locale": "en-US",
			  "content": "You have {count} new notifications!"
			}

		Response:
			A string of the generated content

		Response Example:
			{ "data": "You have 5 new notifications!" }

		Error:
			1000, RIGHTS, The user lacks rights to read sub-Templates
			1001, DATA_FIELDS, Missing or invalid data passed
			1100, DB_NO_RECORD, The template or locale does not exist
		"""

		# Make sure the client has access via the session
		access.internal_or_verify(
			req, { 'name': 'mouth_content', 'right': access.READ }
		)

		# Check minimum fields
		try: evaluate(req.data, [ 'template', 'locale', 'content' ])
		except ValueError as e:
			return Error(
				errors.body.DATA_FIELDS, [ [ f, 'missing' ] for f in e.args ]
			)

		# Find the template variables
		dTemplate = Template.get(req.data.template, raw = [ 'variables' ])
		if not dTemplate:
			return Error(
				errors.body.DB_NO_RECORD, [ req.data.template, 'template' ]
			)

		# If the locale doesn't exist
		if not Locale.exists(req.data.locale):
			return Error(
				errors.body.DB_NO_RECORD, [ req.data.locale, 'locale' ]
			)

		# Generate the template and return it
		return Response(
			self._generate_sms(
				req.data.content,
				req.data.locale,
				dTemplate['variables']
			)
		)

	def templates_read(self, req: jobject) -> Response:
		"""Templates read

		Returns all templates in the system

		Arguments:
			req (jobject): The request details, which can include 'data', \
						'environment', and 'session'

		Returns:
			Response

		Noun:
			GET templates

		Response:
			Returns an array of Template objects ordered by name

		Response Example:
			{
			  "data": [ {
			    "_id": "3369bc9c536f11f086f7c1bd71fea541",
			    "_created": 1751041150,
			    "_updated": 1751041150,
			    "name": "forgot password",
			    "variables": {
			      "email": "first.last@test.com",
			      "name": "First Last",
			      "url": "https://test.com/forgot/reset/a247e"
			    }
			  } ]
			}

		Error:
			1000, RIGHTS, The user lacks the rights to read Templates
		"""

		# Make sure the client has access via the session
		access.verify(
			req.session, { 'name': 'mouth_template', 'right': access.READ }
		)

		# Fetch and return all templates
		return Response(
			Template.get(raw = True, orderby = 'name')
		)