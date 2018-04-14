import calendar
import click
import tasks


@click.group()
def completion():
    pass


@completion.command()
def list_commands():
    for c in tasks.cli.commands.values():
        click.echo(f'{c.name}:{c.help}')


@completion.command()
@click.argument('cmd')
@click.argument('args', nargs=-1)
def list_ids(cmd, args):
    if cmd not in tasks.cli.commands:
        return

    if cmd not in ['delete', 'complete', 'postpone', 'reschedule']:
        return

    for t in tasks.tasks:
        if t.display_id not in args:
            click.echo(f'{t.display_id}:{t.name}')


@completion.command()
@click.argument('cmd')
@click.argument('args', nargs=-1)
def list_options(cmd, args):
    if cmd not in tasks.cli.commands:
        return

    if cmd == 'postpone':
        opts = [d.lower() for d in calendar.day_name]
        opts.extend(['today', 'tomorrow'])

        for opt in opts:
            click.echo(opt)

    else:
        c = tasks.cli.commands[cmd]
        opts = [a for a in c.params if type(a) == click.core.Option]

        for opt in opts:
            help = opt.help.replace('[', '\[').replace(']', '\]') \
                .replace(':', '\:')
            click.echo(f'{opt.opts[0]}:{help}')


@completion.command()
def dmenu():
    for t in sorted([t for t in tasks.tasks if not t.completed],
                    key=lambda t: t.id):
        click.echo(f'[{t.display_id}] {t.name}')


if __name__ == '__main__':
    try:
        completion()
    except:
        pass
