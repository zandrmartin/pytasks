![PRs welcome but not actively maintained](https://img.shields.io/badge/status-PRs%20welcome%20but%20not%20actively%20maintained-red.svg?style=flat-square)

# pytasks

A rewrite of [tasks.js](https://github.com/zandrmartin/tasks.js) in Python.

## Description

pytasks fits somewhere between [Steve Losh's `t`](https://github.com/sjl/t) and
[Taskwarrior](https://taskwarrior.org/) on the complexity spectrum. Tasks in
pytasks can have due dates and can recur at fixed intervals. However, pytasks
is not intended to be a calendar or scheduling system, and does not require you
to organize your tasks in any particular fashion.

pytasks stores all task data in either `$XDG_DATA_HOME/tasks.json` (if
`$XDG_DATA_HOME` is set) or in `~/.tasks.json`. The storage format is
unremarkable; it is just a JSON array dumped to a file. You are free to futz
about with it if you like. Completed tasks remain in the data file until they
are deleted with `clean-cache`.

Each task is assigned a unique id. This id is just an integer, although it is
displayed in base-36 to keep things short. ("abc" is easier to type than
13368.) A given task will always have the same id throughout its life, however
ids will be reused when tasks are deleted (either through `delete` or
`clean-cache`).

## Requirements

- [Click](http://click.pocoo.org)
- [Pytest](https://pytest.org) [optional, if you want to run tests]

## Usage

1. `pip3 install .`
2. `task <action> <option>`

`<action>` is one of `add`, `clean-cache`, `complete`, `delete`, `list`,
`postpone`, `rename`, `reschedule`, `status`

`<options>` depend on `<action>`:

- `add "name of task" [<-d|--due> <date|day-of-week>] [<-r|--recurs> [#] <day|week|month|year|day-of-week>]`
- `complete <id> [<id> <id> ...]`
- `delete <id> [<id> <id> ...]`
- `list [dated] ["search term"] [-c|--completed] [-n|--no-recurring]`
- `postpone <date> <id> [<id> <id> ...]`
- `rename <id> <name>`
- `reschedule <schedule> <id> [<id> <id> ...]`

## Examples

I'd recommend setting up an alias in your shell. Something like `alias task='python3 tasks.py'`.

- Add a task due on Tuesday: `task add "do that thing" -d tuesday`
- Change that task to be due Wednesday: `task postpone wednesday <id>`
- Add a task due the 17th of every other month: `task add "do the monthly
  thing" -d 1-17-2017 -r 2 month`
- Rename that task: `task rename <id> "do the bi-monthly thing"`
- Add a task due on Mondays and Thursdays: `task add "biweekly stuttered thing"
  -d monday -r monday,thursday`
- See all tasks that are not completed: `task list`
- See all tasks that contain the word `foo` in the name: `task list foo`
- Show the completed tasks that contain `foo`: `task list foo -c`
- See all tasks due on a particular day: `task list dated 2014-12-31`

## Explanation of actions

- `add` adds a task
- `clean-cache` deletes all completed tasks from the data file
- `complete` completes a task, either by marking it completed, or rescheduling
  it for its next occurrence
- `delete` deletes a task. There is no recovery.
- `list` list tasks, optionally narrowed by some search criteria
- `postpone` reschedule a specific task
- `rename` rename a specific task
- `status` a special command to list all tasks due today (or in the past)
  joined into a single string, for use in status bars e.g.
  [Lemonbar](https://github.com/LemonBoy/bar) etc.

## License

BSD 2-clause
