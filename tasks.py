import click
import datetime
import settings
import models


tasks = models.TaskCollection()
tasks.load(settings.data_file)


@click.group()
def cli():
    pass


@cli.command()
@click.argument('name')
@click.option('-d', '--due', help='Due date of task.')
@click.option('-r', '--recurs',
              help='Schedule for task to recur. Requires --due option. \
Format: [#] <day|week|month|year|day-of-week>')
@click.option('-t', '--tags', multiple=True, help='List of tags.')
def add(name, due, recurs, tags):
    """Add a new task."""
    t = models.Task(name=name)

    if due is not None:
        t.due = due

    if recurs is not None:
        t.recurs = True
        t.schedule = recurs

    t.tags = [t for t in tags]

    tasks.add(t)
    tasks.save(settings.data_file)
    click.echo(f'Added task {t.name} (id {t.display_id}).')


@cli.command(name='clean-cache')
def clean_cache():
    """Remove all completed tasks."""
    starting = len(tasks)
    tasks.items = list(filter(lambda t: not t.completed, tasks))
    ending = len(tasks)
    tasks.save(settings.data_file)

    click.echo(f'Cleared {starting-ending} tasks.')


@cli.command()
@click.argument('ids', nargs=-1)
def complete(ids):
    """Mark a task completed."""
    for id in ids:
        t = tasks.find_by_id(id)
        t.complete()
        click.echo(f'Task {t.display_id} ({t.name}) completed.')

    tasks.save(settings.data_file)


@cli.command()
@click.argument('ids', nargs=-1)
def delete(ids):
    """Delete a task."""
    for id in ids:
        t = tasks.find_by_id(id)
        tasks.remove(t)
        click.echo(f'Task {t.display_id} ({t.name}) deleted.')

    tasks.save(settings.data_file)


@cli.command(name='list')
@click.argument('search', nargs=-1)
@click.option('-n', '--no-recurring', is_flag=True,
              help='Only show non-recurring tasks.')
@click.option('-c', '--completed', is_flag=True,
              help='Only show completed tasks.')
@click.option('-a', '--all', is_flag=True,
              help="Show all tasks (don't limit to next six months).")
@click.option('-s', '--show-schedule', is_flag=True,
              help='Show schedule of recurring tasks.')
def list_tasks(search, no_recurring, completed, all, show_schedule):
    """List (or optionally search) tasks."""
    selected = list(tasks)

    if not all:
        limit = datetime.date.today() + datetime.timedelta(days=180)
        selected = filter(lambda t: not t.recurs or t.recurs and t.due < limit,
                          selected)

    if no_recurring:
        selected = filter(lambda t: t.schedule is None, selected)

    selected = filter(lambda t: t.completed == completed, selected)

    if len(search) > 0:
        new_tasks = []

        for term in search:
            def _search_filter(t):
                if term.lower() in t.name.lower():
                    return True
                for tag in t.tags:
                    if term.lower() in tag.lower():
                        return True
                return False

            new_tasks.extend(filter(_search_filter, selected))

        selected = new_tasks

    def _date_sort(t):
        return datetime.date.max if t.due is None else t.due

    selected = sorted(selected, key=_date_sort, reverse=True)

    display = models.TaskListDisplay(selected)
    display.show_schedule = show_schedule
    click.echo(display.output())


@cli.command()
@click.argument('date')
@click.argument('ids', nargs=-1)
def postpone(date, ids):
    """Change the due date of a task."""
    for id in ids:
        t = tasks.find_by_id(id)
        t.due = date
        to_date = t.due.strftime('%A, %B %d %Y')
        click.echo(f'Changed due date of task "{t.name}" to {to_date}.')

    tasks.save(settings.data_file)


@cli.command()
@click.argument('schedule')
@click.argument('ids', nargs=-1)
def reschedule(schedule, ids):
    """Change the recurrence schedule of a task."""
    for id in ids:
        t = tasks.find_by_id(id)
        t.schedule = schedule
        click.echo(f'Changed schedule of task "{t.name}" to {schedule}.')

    tasks.save(settings.data_file)


@cli.command()
@click.argument('id')
@click.argument('name')
def rename(id, name):
    """Change the name of a task."""
    t = tasks.find_by_id(id)
    old_name = t.name
    t.name = name
    click.echo(f'Renamed task "{old_name}" to "{t.name}".')
    tasks.save(settings.data_file)


@cli.command()
def reorder():
    """Reset task ids."""
    for i, t in enumerate(tasks):
        t.id = i

    tasks.save(settings.data_file)


@cli.command()
@click.argument('id')
@click.argument('tags', nargs=-1)
def retag(id, tags):
    """Change tags of a task."""
    t = tasks.find_by_id(id)
    old_tags = ', '.join(t.tags)
    t.tags = [t for t in tags]
    new_tags = ', '.join(t.tags)
    tasks.save(settings.data_file)

    msg = f'Retagged task {t.name}; removed [{old_tags}], added [{new_tags}].'
    click.echo(msg)


@cli.command()
def status():
    """Statusbar-friendly output of (over)due tasks."""
    today = datetime.date.today()
    due = sorted(
        filter(lambda t: t.due and not t.completed and t.due <= today, tasks),
        key=lambda t: t.id
    )
    status = ' '.join(f'[{t.display_id}] {t.name}' for t in due)

    if status != '':
        click.echo(status)


if __name__ == '__main__':
    try:
        cli()
    except Exception as e:
        click.echo(e)
