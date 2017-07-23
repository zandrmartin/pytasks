import datetime as dt
import json
import scheduling
import settings
import string


def base36(number):
    if number == 0:
        return '0'

    alphabet = string.digits + string.ascii_lowercase
    base = len(alphabet)
    rv = []

    while number:
        number, i = divmod(number, base)
        rv.insert(0, alphabet[i])

    return ''.join(rv)


class TaskJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'to_json') and callable(o.to_json):
            return o.to_json()

        if type(o) in [dt.datetime, dt.date]:
            return o.strftime(settings.date_format)

        return super().default(o)


class TaskCollection:
    def __init__(self):
        self.items = []

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, idx):
        return self.items[idx]

    def __len__(self):
        return len(self.items)

    def add(self, item):
        self.items.append(item)

    def remove(self, item):
        idx = self.items.index(item)
        return self.items.pop(idx)

    def save(self, path):
        for task in self.items:
            if task.id is None:
                task.id = self.find_unused_id()

        with open(path, 'w') as f:
            json.dump(self.items, f, cls=TaskJSONEncoder)

    def load(self, path):
        with open(path, 'r') as f:
            tasks = json.load(f)

        for data in tasks:
            t = Task(**data)
            self.add(t)

    def find_by_id(self, id):
        if type(id) == str:
            id = int(id, 36)

        for task in self.items:
            if task.id == id:
                return task

        return None

    def find_unused_id(self):
        id = 0

        while any(t for t in self.items if t.id == id):
            id += 1

        return id


class Task:
    def __init__(self, **kwargs):
        self.id = None
        self.name = ''
        self._due = None
        self.schedule = None
        self.completed = False
        self.recurs = False

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __eq__(self, other):
        return self.id == other.id

    @property
    def due(self):
        return self._due

    @due.setter
    def due(self, d):
        if type(d) == str:
            self._due = scheduling.parse_due_date(d)
        else:
            self._due = d

    @property
    def display_id(self):
        if self.id is None:
            return ''

        return base36(self.id)

    def to_json(self):
        attrs = {
            'id': self.id,
            'name': self.name,
            'recurs': self.recurs,
            'completed': self.completed
        }

        if self.due:
            attrs['due'] = self.due

        if self.schedule:
            attrs['schedule'] = self.schedule

        return attrs

    def complete(self):
        if self.recurs and self.schedule:
            self.due = scheduling.next_scheduled(self.schedule, self.due)
        else:
            self.completed = True


class TaskListDisplay:
    date_format = '%a %b %d %Y'

    def __init__(self, tasks):
        self.tasks = tasks
        self.show_schedule = False

    def _calculate_column_widths(self):
        widths = {
            'id': max(map(lambda t: len(t.display_id), self.tasks)),
            'task': max(map(lambda t: len(t.name), self.tasks)),
        }

        def _due(due):
            return 0 if due is None else len(due.strftime(self.date_format))
        widths['due'] = max(map(_due, [t.due for t in self.tasks]))

        def _sched(sched):
            return len(sched) if sched is not None else 0
        widths['schedule'] = 0 if not self.show_schedule \
            else max(map(_sched, [t.schedule for t in self.tasks]))

        for title in widths:
            if 0 < widths[title] < len(title):
                widths[title] = len(title)

        self._column_widths = widths

    @property
    def col_widths(self):
        if not hasattr(self, '_column_widths'):
            self._calculate_column_widths()

        return self._column_widths

    @property
    def total_width(self):
        if not hasattr(self, '_total_width'):
            # width of columns themselves
            width = sum(self.col_widths.values())

            # calculate width of 2-space gutters between columns
            for w in self.col_widths.values():
                # add 2-space gutter for every non-zero column
                if w > 0:
                    width += 2

            # subtract final 2-space gutter so right side is flush
            width -= 2
            self._total_width = width

        return self._total_width

    def _generate_output(self):
        output = []
        bar = '-' * self.total_width

        line = ''
        for heading in ['id', 'task', 'due', 'schedule']:
            if self.col_widths[heading] > 0:
                line += heading.title().ljust(self.col_widths[heading] + 2)
            line.rstrip()

        output.append(line)
        output.append(bar)

        for t in self.tasks:
            line = t.display_id.ljust(self.col_widths['id'] + 2)
            line += t.name.ljust(self.col_widths['task'] + 2)

            if t.due is not None:
                line += t.due.strftime(self.date_format) \
                    .ljust(self.col_widths['due'] + 2)
            elif self.col_widths['due'] > 0:
                line += ' ' * (self.col_widths['due'] + 2)

            if self.show_schedule:
                if t.schedule is not None:
                    line += t.schedule.ljust(self.col_widths['schedule'] + 2)
                elif self.col_widths['schedule'] > 0:
                    line += ' ' * (self.col_widths['schedule'] + 2)

            if line.endswith('  '):
                line.rstrip()

            output.append(line)

        output.append(bar)
        output.append(f'{len(self.tasks)} total tasks')
        self._output = output

    def output(self):
        if len(self.tasks) == 0:
            return 'No tasks found.'

        self._generate_output()
        return '\n'.join(self._output)
