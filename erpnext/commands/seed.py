import click
import frappe
from frappe.commands import get_site, pass_context


@click.command("import-demo-seed")
@click.option("--seed-dir", default="seed_output", help="Path to seed CSV directory")
@click.option("--company", default=None, help="Target company name (auto-created if missing)")
@pass_context
def import_demo_seed(context, seed_dir, company):
	"""Import demo seed data (biomedical & hospital waste) into the current site."""
	site = get_site(context)
	frappe.init(site)
	frappe.connect()
	try:
		from erpnext.seed.import_executor import import_seed

		report = import_seed(seed_dir=seed_dir, company_override=company)
		click.echo()
		click.echo(click.style("Seed import complete.", fg="green", bold=True))
		click.echo()

		for doctype, stats in report.items():
			if isinstance(stats, dict) and "inserted" in stats:
				err_count = len(stats.get("errors", []))
				line = f"  {doctype:25s}  inserted={stats['inserted']}  skipped={stats['skipped']}  errors={err_count}"
				color = "red" if err_count else "white"
				click.echo(click.style(line, fg=color))
			elif isinstance(stats, dict):
				click.echo(f"  {doctype:25s}  {stats}")
		click.echo()
	finally:
		frappe.destroy()


commands = [import_demo_seed]
