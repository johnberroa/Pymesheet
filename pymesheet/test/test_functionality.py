import pytest


@pytest.mark.parametrize("end, start, task1, task2, total, worktime, workday, final", [
    (30, 0, 10, 0, 0, 30, 20, 20),
    (60, 30, 0, 10, 20, 30, 20, 40)
])
def test_workday(end, start, task1, task2, total, worktime, workday, final):
    worktime1, workday1, final1 = add_workday(end, start, task1, task2, total)
    assert worktime1 == worktime
    assert workday1 == workday
    assert final1 == final


def add_workday(end, start, task1, task2, total):
    work_time = end - start
    allocated_time = []
    for task in [task1, task2]:
        allocated_time.append(task)
    workday = work_time - sum(allocated_time)
    if workday < 0:
        raise ValueError
    else:
        total += int(workday)
    return work_time, workday, total
