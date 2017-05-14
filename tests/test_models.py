import datetime
import json
import models
import settings


def test_base36():
    for num in range(0, 10000, 9):
        b36str = models.base36(num)
        new_int = int(b36str, 36)
        assert new_int == num


def test_task_json_encoder(incomplete_task):
    due_string = incomplete_task.due.strftime(settings.date_format)
    due_json = f'"due": "{due_string}"'

    task_json = incomplete_task.__json__()
    task_json['due'] = due_string

    j = json.dumps(incomplete_task, cls=models.TaskJSONEncoder)
    assert due_json in j

    reloaded = json.loads(j)

    for k, v in task_json.items():
        assert reloaded[k] == v


def test_task_collection(task_collection, incomplete_task,
                         task_not_in_collection, task_without_id, tmpdir):
    # collection should have 3 tasks to start
    assert len(task_collection) == 3

    # should be able to get individual task by indexing
    assert task_collection[1] is not None

    # should be able to iterate through tasks
    count = 0
    for task in task_collection:
        count += 1
    assert count == 3

    # test find_by_id()
    result = task_collection.find_by_id(incomplete_task.id)
    assert result == incomplete_task
    result = task_collection.find_by_id(99999999)
    assert result is None

    old_id = incomplete_task.id
    incomplete_task.id = 56
    result = task_collection.find_by_id('1k')
    assert result == incomplete_task

    # test find_unused_id()
    incomplete_task.id = old_id
    result = task_collection.find_unused_id()
    assert result == 2

    # test remove()
    removed = task_collection.remove(incomplete_task)
    assert removed == incomplete_task
    assert len(task_collection) == 2

    # test add()
    task_collection.add(task_not_in_collection)
    assert len(task_collection) == 3
    found = task_collection.find_by_id(task_not_in_collection.id)
    assert found == task_not_in_collection

    # test ids get added on save
    path = tmpdir.join('test-tasks.json')
    task_collection.add(task_without_id)
    task_collection.save(path)
    assert task_without_id is not None

    # assert saved data will load
    new_collection = models.TaskCollection()
    new_collection.load(path)
    assert len(new_collection) == 4
    assert new_collection.find_by_id(incomplete_task.id) == incomplete_task


def test_task(incomplete_task, weekly_recurring_task):
    # test initial attrs
    t = models.Task()
    assert t.id is None
    assert t.name == ''
    assert t.due is None
    assert t.schedule is None
    assert t.tags == []
    assert not t.completed
    assert not t.recurs

    # test initial attr override
    t = models.Task(id=123, name='foobar', recurs=True, tags=['a', 'b', 'c'])
    assert t.id == 123
    assert t.name == 'foobar'
    assert t.recurs
    assert t.tags == ['a', 'b', 'c']

    # test due date scheduling property
    t.due = 'today'
    assert t.due == datetime.date.today()

    # test display_id property
    t.id = 56
    assert t.display_id == '1k'

    # test __json__ props
    j = t.__json__()

    assert 'id' in j
    assert j['id'] == t.id

    assert 'name' in j
    assert j['name'] == t.name

    assert 'recurs' in j
    assert j['recurs'] == t.recurs

    assert 'completed' in j
    assert j['completed'] == t.completed

    assert 'due' in j
    assert j['due'] == datetime.date.today()

    # schedule not set so it shouldn't even be in the attrs
    assert 'schedule' not in j

    assert 'tags' in j
    assert j['tags'] == ['a', 'b', 'c']

    # test complete() - non-recurring task should be completed
    assert not incomplete_task.completed
    incomplete_task.complete()
    assert incomplete_task.completed

    # recurring task should be rescheduled - it is never complete
    assert not weekly_recurring_task.completed
    weekly_recurring_task.complete()
    assert not weekly_recurring_task.completed
    assert weekly_recurring_task.due == datetime.date(2017, 1, 10)
