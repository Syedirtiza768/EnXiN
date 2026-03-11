# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# GPL v3 License. See license.txt

import click

from erpnext.commands.seed import commands as seed_commands


def call_command(cmd, context):
	return click.Context(cmd, obj=context).forward(cmd)


commands = [*seed_commands]
