import datetime
import models
import pytest


@pytest.fixture(scope='session')
def jan_3_2017():
    """Base known date for day-specific tests. 1-3-2017 was a Tuesday."""
    d = datetime.date(2017, 1, 3)
    yield d


@pytest.fixture(scope='function')
def incomplete_task():
    t = models.Task()
    t.id = 0
    t.name = 'incomplete task'
    t.due = '2017-12-31'
    t.completed = False
    yield t


@pytest.fixture(scope='function')
def completed_task():
    t = models.Task()
    t.id = 1
    t.name = 'completed task'
    t.due = '2017-12-31'
    t.completed = True
    yield t


@pytest.fixture(scope='function')
def weekly_recurring_task():
    t = models.Task()
    t.id = 3
    t.name = 'weekly recurring task'
    t.due = '2017-1-3'
    t.recurs = True
    t.schedule = '1 week'
    t.completed = False
    yield t


@pytest.fixture(scope='function')
def task_not_in_collection():
    t = models.Task()
    t.id = 4
    t.name = 'task not in collection'
    t.completed = False
    yield t


@pytest.fixture(scope='function')
def task_without_id():
    t = models.Task()
    t.name = 'task without id'
    t.completed = False
    yield t


@pytest.fixture(scope='function')
def task_collection(incomplete_task, completed_task, weekly_recurring_task):
    t = models.TaskCollection()
    t.add(incomplete_task)
    t.add(completed_task)
    t.add(weekly_recurring_task)
    yield t
