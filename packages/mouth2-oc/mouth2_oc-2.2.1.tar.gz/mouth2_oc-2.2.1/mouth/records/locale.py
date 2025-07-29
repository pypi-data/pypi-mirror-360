# coding=utf8
""" Mouth Locale Records

Handles the individual locale records available on the system
"""

__author__		= "Chris Nasr"
__version__		= "1.0.0"
__maintainer__	= "Chris Nasr"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2025-03-11"

# Limit exports
__all__ = [ 'Locale' ]

# Ouroboros imports
from config import config
from define import Tree
from rest_mysql.Record_MySQL import Record

# Python imports
import pathlib

class Locale(Record):
	"""Locale

	Represents a locale in the system

	Extends:
		Record_MySQL.Record
	"""

	_conf = Record.generate_config(
		Tree.from_file('%s/define/locale.json' % pathlib.Path(
			__file__
		).parent.parent.resolve(), {
			'__name__': 'record',
			'__sql__': {
				'auto_primary': False,
				'create': [ '_archived', '_created', 'name' ],
				'db': config.mysql.db('mouth'),
				'host': config.mouth.mysql('records'),
				'indexes': {
					'ui_name': { 'unique': [ 'name' ] }
				},
				'table': 'mouth_locale',
				'charset': 'utf8mb4',
				'collate': 'utf8mb4_bin'
			},

			'_id': { '__sql__': { 'type': 'char(5)' } },
			'_archived': { '__sql__': { 'opts': 'default 0' } },
			'_created': { '__sql__': {
				'opts': 'not null default CURRENT_TIMESTAMP'
			} }
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