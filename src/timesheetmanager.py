"""
Timesheet class
Creates a Pandas dataframe that records time worked on various user specified tasks.
Connects to a user interface for ease of use.
@author: John Berroa
"""
import pandas as pd
import pendulum, time, pickle, os
from user_interface import UserInterface
from time_utils import Converter

VERSION = ".7"


def clear():
    """
    Global function that clears the command line
    """
    os.system('cls' if os.name == 'nt' else 'clear')


# TODO: rename src to pysheet or wtathevalj

class TimesheetManager:
    def __init__(self, name=None, path=os.getcwd()):
        self.__version__ = VERSION
        self.path = os.path.join(path, "timesheets")
        os.makedirs(self.path, exist_ok=True)
        if name is None:
            try:
                default = self.load_config()
                name = default
            except FileNotFoundError:
                clear()
                print("[SETUP] There is no default Timesheet set.  A temporary Timesheet will be created.")
                print("\nIf you have not yet created a timesheet, or need to set your default timesheet,")
                print("please do so in the 'Timesheet Management' menu.")
                _ = input("\nPress ENTER to continue...")
                name = "TEMPORARY"
        self.name = name
        self.today = pendulum.today()
        new = False
        try:
            self.data = self.load_timesheet(self.name)
        except FileNotFoundError:
            new = True
            self.tasks = None
            self.data = pd.DataFrame(index=self.tasks)
        self.UI = UserInterface(name, new, self.today, VERSION)

        while True:
            code, string = self.UI.ask_generic_input()

            if code == '1':
                self.start_task(string)
            elif code == '22':
                self.time_per_day(string)
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
            elif code == '45':
                self.backup_timesheet(string)
            elif code == '46':
                self.save_config(string)

            self.UI.banner()  # places banner at top of each new page

    ################ File Management Functions ################

    def save_config(self, default):
        """
        Saves default timesheet in a text file for later usage.
        :param default: name of timesheet to set as default
        """
        self.UI.banner()
        config = open("config.data", "w")
        config.write("default_timesheet={}".format(default))
        config.close()
        print("{} set as default Timesheet.".format(default))
        self.UI.user_return()

    def load_config(self):
        config = open("config.data", "r")
        default = config.read()
        default = default.split('=')
        return default[1]

    def save_timesheet(self, path, name, data):
        path = os.path.join(path, "{}.pkl".format(name))
        pickle.dump(data, open(path, "wb"))

    def load_timesheet(self, name):
        """
        Loads a timesheet and sets all the parameters of this class to deal with the new timesheet
        :param name: name of Timesheet
        """
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
            if name == self.name:
                print("[WARNING] Deleting current Timesheet, new current Timesheet will be the default.")
                _ = input("\nPress ENTER to continue...")
                try:
                    self.data = self.load_timesheet(self.load_config())
                except FileNotFoundError:
                    print("[WARNING] No default Timesheet set, creating a temporary...")
                    _ = input("\nPress ENTER to acknowledge...")
                    self.create_new_timesheet("TEMPORARY")
            os.remove(os.path.join(self.path, name + ".pkl"))
            print("'{}' deleted.".format(name))
            self.UI.user_return()
        else:
            print("'{}' not deleted.".format(name))
            self.UI.user_return()

    def list_timesheets(self):
        """
        Lists Timesheets saved
        """
        self.UI.banner()
        print("List of Timesheets:")
        i = 1
        for timesheet in os.listdir(self.path):
            if timesheet[-4:] == '.pkl':
                print("\t({}) {}".format(i, timesheet))
                i += 1
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

    def start_task(self, task_name):
        """
        Starts the recording process.  Quietly calls _end_task when done, to record the time into the data.  Creates a
        new task if provided a task not already existing.
        :param task_name: task to record
        """
        go_on = True
        if task_name not in self.data.index:
            self.UI.banner()
            add = input(
                "[WARNING] '{}' is not in the list of tasks...would you like to add it? [y/n]...".format(task_name))
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
            self.UI.timelogger(task_name)
            self._end_task(task_name, start_time)

    def _end_task(self, name, start_time):
        """
        Quietly called from start_task.  Ends the task and records the time by adding it to the time already recorded
        for that task
        :param name: task to record
        """
        self.UI.banner()
        self.data[self.today.to_date_string()].loc[name] += int(time.time() - start_time)  # do not care about ms
        print("Logging of Task '{}' stopped...".format(name))
        print(self.data.head(20))
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
        self.UI.user_return()

    def add_task(self, task_name):
        """
        Adds task to the dataframe by adding it to the index.  If the task already exists, it exits.
        Can take string or [str].
        :param task_name: name of task to add
        """
        if task_name in self.data.index:
            print("\nTask {} already in Timesheet '{}'.".format(task_name, self.name))
            self.UI.user_return()
        else:
            if type(task_name) == str:
                task_name = [task_name]
            new_task = pd.DataFrame(index=task_name)
            self.data = self.data.append(new_task, verify_integrity=True, sort=False)
            print("Task '{}' created.".format(task_name[0]))
            self.data.fillna(0, inplace=True)
            self.save_timesheet(self.path, self.name, self.data)
            self.UI.user_return()

    def delete_task(self, task_name):
        """
        Deletes task from the data.  If it doesn't exist, it does nothing.
        :param task_name: task to delete
        """
        if task_name not in self.data.index:
            print("\n'{}' task not in database.".format(task_name))
            self.UI.user_return()
        else:
            self.data.drop(task_name, inplace=True)
            self.save_timesheet(self.path, self.name, self.data)

    ################ Time Functions ################

    def time_per_day(self, day):
        if day == "today":
            day = self.today.to_date_string()
        elif day == "yesterday":
            day = pendulum.yesterday().to_date_string()
        time = self.data[day].sum()
        print(time)
        mins = Converter.sec2min(time)
        print(mins)
        hours, mins = Converter.min2hour(mins)
        print(hours, mins)
        hour_min_string = Converter.convert2string(hours, mins)
        print(hour_min_string)
        days, hours_day = Converter.hour2day(hours)
        print(days, hours_day)
        day_hour_min_string = Converter.convert2string_days(days, hours_day, mins)
        self.UI.banner()
        print("Summary for {}".format(day)) #TODO: Make prettier
        self.UI.summary_divider()
        print(hour_min_string)
        print(day_hour_min_string)
        self.UI.user_return()

if __name__ == "__main__":
    t = TimesheetManager()
