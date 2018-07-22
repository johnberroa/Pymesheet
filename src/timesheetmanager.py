"""
Timesheet class
Creates a Pandas dataframe that records time worked on various user specified tasks.
Connects to a user interface for ease of use.
@author: John Berroa
"""
import pandas as pd
import pendulum, time, pickle, os
from user_interface import UserInterface

VERSION = ".2"


# TODO: rename src to pysheet or wtathevalj

class TimesheetManager:  # TODO: load other timesheets and save state between them (i.e. default timesheet, etc)
    def __init__(self, name, init_tasks=None, path=os.getcwd()):
        self.__version__ = VERSION
        self.path = os.path.join(path, "timesheets")
        os.makedirs(self.path, exist_ok=True)
        self.name = name
        self.today = pendulum.today()
        new = False
        try:
            self.data = self.load_timesheet(self.name)
        except FileNotFoundError:
            new = True
            if init_tasks:
                self.tasks = init_tasks
            else:
                self.tasks = None
            self.data = pd.DataFrame(index=self.tasks)
        self.UI = UserInterface(name, new, self.today, VERSION)
        # self.start_time = 0

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
            elif code == '41':
                self.list_timesheets()
            elif code == '42':
                self.create_new_timesheet(string)
            elif code == '43':
                self.data = self.load_timesheet(string)
                print("{} Timesheet loaded.".format(string))
                self.UI.user_return()
            elif code == '44':
                self.delete_timesheet(string)
            elif code=='45':
                self.backup_timesheet(string)

            self.UI.banner()  # places banner at top of each new page

    ################ File Management Functions ################

    def save_timesheet(self, path, name, data):
        path = os.path.join(path, "{}.pkl".format(name))
        pickle.dump(data, open(path, "wb"))

    def load_timesheet(self, name):
        path = os.path.join(self.path, "{}.pkl".format(name))
        self.name = name
        self.UI = UserInterface(name, False, self.today, VERSION)
        return pickle.load(open(path, "rb"))

    def delete_timesheet(self, name):
        """
        Deletes a timesheet.  Has a confirmation to make sure a file isn't deleted when not wanted to
        :param name: name of timesheet to delete
        """
        self.UI.banner()
        decision = None
        while decision not in ["y", "n"]:
            decision = input("[WARNING] Confirm DELETION of Timesheet '{}' [y/n]: ".format(name)).lower()
        if decision == "y":
            os.remove(os.path.join(self.path, name+".pkl"))
            print("'{}' deleted.".format(name))
            self.UI.user_return()
        else:
            print("'{}' not deleted.".format(name))
            self.UI.user_return()

    def list_timesheets(self): #TODO: remove backup from list
        """
        Lists Timesheets saved
        """
        self.UI.banner()
        print("List of Timesheets:")
        for i, timesheet in enumerate(os.listdir(self.path)):
            print("\t({}) {}".format(i + 1, timesheet))
            print(self.data)  # TODO:DEBUG
            self.UI.user_return()

    def backup_timesheet(self, name):
        """
        Backups a timesheet by saving it in another folder.  First loads it, then saves it in the
        backup folder
        :param name: name of timesheet to backup
        """
        path = os.path.join(self.path, "backup")
        os.makedirs(path, exist_ok=True)
        data = self.load_timesheet(name)
        print(path)
        self.save_timesheet(path, name, data)
        print("'{}' successfully backed up.".format(name))
        self.UI.user_return()

    def create_new_timesheet(self, name):
        if name in os.listdir(self.path):
            print("Timesheet '{}' already exists.".format(name))
            self.UI.user_return()
        else:
            print("Creating new Timesheet with the name '{}'".format(name))
            self.name = name
            new = True
            self.tasks = None
            self.data = pd.DataFrame(index=self.tasks)
            self.UI = UserInterface(name, new, self.today, VERSION)
            self.start_time = 0



    ################ Logging Functions ################

    def start_task(self, task_name):  # TODO: list tasks and just input number of what you want
        """
        Starts the recording process.  Quietly calls _end_task when done, to record the time into the data.  Creates a
        new task if provided a task not already existing.
        :param task_name: task to record
        """
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
            start_time = time.time()
            # Start the UI logging time, once stopped through the UI, record the time
            self.UI.timelogger(task_name, start_time)
            self._end_task(task_name, start_time)

    def _end_task(self, name, start_time):
        """
        Quietly called from start_task.  Ends the task and records the time by adding it to the time already recorded
        for that task
        :param name: task to record
        """
        self.data[self.today.to_date_string()].loc[name] += int(time.time() - start_time)  # do not care about ms
        print("STOPPED")
        print(self.data.head())
        self.save_timesheet(self.path, self.name, self.data)
        print("Time successfully recorded!")
        self.UI.user_return()

    ################ Task Functions ################

    def list_tasks(self):
        """
        Lists the index of the data, which are the task names
        """
        self.UI.banner()
        print("List of Tasks in Timesheet {}:\n".format(self.name))
        for i, task in enumerate(self.data.index):
            print("\t({}) {}".format(i + 1, task))
        print(self.data)  # TODO:DEBUG
        self.UI.user_return()

    def add_task(self, task_name):
        """
        Adds task to the dataframe by adding it to the index.  If the task already exists, it exits.
        Can take string or [str].
        :param task_name: name of task to add
        """
        if task_name in self.data.index:
            print("Task {} already in Timesheet '{}'.".format(task_name, self.name))
            self.UI.user_return()
        else:
            if type(task_name) == str:
                task_name = [task_name]
            new_task = pd.DataFrame(index=task_name)
            self.data = self.data.append(new_task, verify_integrity=True)
            print(self.data.head())
            self.save_timesheet(self.path, self.name, self.data)

    def delete_task(self, task_name):
        """
        Deletes task from the data.  If it doesn't exist, it does nothing.
        :param task_name: task to delete
        """
        if task_name not in self.data.index:
            print("'{}' task not in database.".format(task_name))
            self.UI.user_return()
        else:
            self.data.drop(task_name, inplace=True)
            print(self.data.head())
            self.save_timesheet(self.path, self.name, self.data)


if __name__ == "__main__":
    # t = Timesheet("nodata")
    #
    tt = TimesheetManager("data", ["Tea", "Kristin"])
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
