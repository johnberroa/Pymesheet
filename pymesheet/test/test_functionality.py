import pytest


@pytest.mark.parametrize("end, start, totaltime, worktime, workday, diff, final", [
    (30, 0, 10, 30, 20, 10, 20),
    (30, 0, 20, 30, 20, 10, 30)
])
def test_workday(end, start, totaltime, worktime, workday, diff, final):
    worktime1, workday1, final1 = add_workday(end, start, workday, totaltime)
    assert worktime1 == worktime
    assert workday1 == diff
    assert final1 == final


def add_workday(end, start, allocated, total):
    work_time = end - start
    workday = work_time - allocated
    if workday < 0:
        raise ValueError
    else:
        total += int(workday)
    return work_time, workday, total
