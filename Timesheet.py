import pandas as pd
import pendulum, time, pickle
from .user_interface import UserInterface

VERSION = ".2"


class Timesheet:
    def __init__(self, name,
                 init_tasks=None):  # TODO: load other timesheets and save state between them (i.e. default timesheet, etc)
        self.__version__ = VERSION
        self.name = name
        self.today = pendulum.today()
        new = False
        try:
            self.data = self.load_timesheet()
        except FileNotFoundError:
            new = True
            if init_tasks:
                self.tasks = init_tasks
            else:
                self.tasks = None
            self.data = pd.DataFrame(index=self.tasks)
        self.UI = UserInterface(name, new, self.today, VERSION)
        self.start_time = 0

        while True:
            code, string = self.UI.ask_generic_input()

            if code == '1':
                self.start_task(string)
            elif code == '2':
                self.start_task(string)
            elif code == '31':
                self.list_tasks()
            elif code == '33':
                self.delete_task(string)
            elif code == '32':
                self.add_task(string)
            elif code == '33':
                self.delete_task(string)

            self.UI.banner()  # places banner at top of each new page

    def save_timesheet(self):
        pickle.dump(self.data, open("{}.pkl".format(self.name), "wb"))

    def load_timesheet(self):
        return pickle.load(open("{}.pkl".format(self.name), "rb"))

    def list_tasks(self):
        self.UI.banner()
        print("List of Tasks in Timesheet {}:\n".format(self.name))
        for i, task in enumerate(self.data.index):
            print("\t({}) {}".format(i + 1, task))
        print(self.data)
        self.UI.user_return()

    def add_task(self, task_name):
        if task_name in self.data.index:
            print("Task {} already in Timesheet '{}'.".format(task_name, self.name))
            self.UI.user_return()
        else:
            if type(task_name) == str:
                task_name = [task_name]
            new_task = pd.DataFrame(index=task_name)
            self.data = self.data.append(new_task, verify_integrity=True)
            print(self.data.head())
            self.save_timesheet()

    def delete_task(self, task_name):
        if task_name not in self.data.index:
            print("'{}' task not in database.".format(task_name))
            self.UI.user_return()
        else:
            self.data.drop(task_name, inplace=True)
            print(self.data.head())
            self.save_timesheet()

    def start_task(self, task_name):  # TODO TIEMES DO NOT ADD TO EACHOTHER
        go_on = True
        if task_name not in self.data.index:
            self.UI.banner()
            add = input(
                "[WARNING] {} is not in the list of tasks...would you like to add it? [y/n]...".format(task_name))
            if add.lower() == 'y':
                self.add_task(task_name)
                go_on = True
            elif add.lower() == 'n':
                go_on = False
            else:
                print("[WARNING] Invalid input...not creating new task and returning to the main menu...")
                go_on = False
                self.UI.user_return()
        if go_on:
            if self.today.to_date_string() not in self.data.columns:
                self.data[self.today.to_date_string()] = 0
            self.start_time = time.time()
            # Start the UI logging time, once stopped through the UI, record the time
            self.UI.timelogger(task_name, self.start_time)
            self._end_task(task_name)

    def _end_task(self, name):
        self.data[self.today.to_date_string()].loc[name] += int(time.time() - self.start_time)  # do not care about ms
        print("STOPPED")
        print(self.data.head())
        self.save_timesheet()
        print("Time successfully recorded!")
        self.UI.user_return()

    """
    user input or class that repeats
    input task, you hit start and put in name, it starts.  Hit a button to stop, which calls stop with that name
    """


if __name__ == "__main__":
    # t = Timesheet("nodata")
    #
    tt = Timesheet("data", ["Tea", "Kristin"])
    #
    # t.add_task("TEST1")
    #
    # tt.add_task(["TEST2"])
    # tt.delete_task("Kristin")
    #
    # print("\n\n\n")
    #
    # t.start_task("TEST1")
    # tt.start_task("TEST2")

    print("\n\n\n")

    # ui = UserInterface("test", False, pendulum.today())
    # ui.ask_generic_input()
