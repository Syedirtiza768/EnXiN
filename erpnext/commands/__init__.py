# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# GPL v3 License. See license.txt

import click


def call_command(cmd, context):
	return click.Context(cmd, obj=context).forward(cmd)


commands = []

try:
	from erpnext.commands.seed import commands as seed_commands

	commands.extend(seed_commands)
except Exception:
	pass
