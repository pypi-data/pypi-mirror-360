# coding=utf8
""" Mouth Template Email Records

Handles the individual template email records available on the system
"""

__author__		= "Chris Nasr"
__version__		= "1.0.0"
__maintainer__	= "Chris Nasr"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2025-03-11"

# Limit exports
__all__ = [ 'TemplateEmail' ]

# Ouroboros imports
from config import config
from define import Tree
from rest_mysql.Record_MySQL import Record

# Python imports
import pathlib

class TemplateEmail(Record):
	"""Template Email

	Represents an E-Mail sub-template in the system

	Extends:
		Record_MySQL.Record
	"""

	_conf = Record.generate_config(
		Tree.from_file('%s/define/template_email.json' % pathlib.Path(
			__file__
		).parent.parent.resolve(), {
			'__name__': 'record',
			'__sql__': {
				'auto_primary': True,
				'changes': [ 'user' ],
				'create': [
					'_created', '_updated', 'template', 'locale', 'subject',
					'text', 'html'
				],
				'db': config.mysql.db('mouth'),
				'host': config.mouth.mysql('records'),
				'indexes': {
					'ui_template_locale': { 'unique': [ 'template', 'locale' ] }
				},
				'table': 'mouth_template_email',
				'charset': 'utf8mb4',
				'collate': 'utf8mb4_unicode_ci'
			},

			'_id': { '__sql__': { 'binary': True } },
			'_created': { '__sql__': {
				'opts': 'not null default CURRENT_TIMESTAMP'
			} },
			'_updated': { '__sql__': {
				'opts': 'not null default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP'
			} },
			'template': { '__sql__': { 'binary': True } },
			'locale': { '__sql__': { 'type': 'char(5)' } }
		})
	)
	"""Configuration"""

	@classmethod
	def config(cls):
		"""Config

		Returns the configuration data associated with the record type

		Returns:
			dict
		"""
		return cls._conf