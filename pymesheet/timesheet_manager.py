"""
TimesheetManager class
Creates a Pandas dataframe that records time worked on various user specified tasks.
Connects to a user interface for ease of use.
@author: John Berroa
"""
import sys
import pandas as pd
import pendulum, time, pickle, os
from os.path import join as pathjoin
from user_interface import UserInterface
from utils.time_utils import Converter, TimeCalculator
from utils.utils import get_current_week_days, generate_day_dict

VERSION = "2.2"
CONFIG_PATH = ".config"
STATE_PATH = "."


# TODO: Add to the feature list that I added confirmation on quit when general is still running
# TODO: Feature idea if a task is no longer used, can export the times to the baseline then delete it from the task list
# TODO: Feature idea: export formatted reports (maybe csvs that are human readable) (does go against privacy principle
# TODO: though
def clear():
    """
    Global function that clears the command line
    """
    os.system('cls' if os.name == 'nt' else 'clear')


class TimesheetManager:
    def __init__(self, name=None, path=os.getcwd()):
        self.__version__ = VERSION
        self.path = pathjoin(path, "timesheets")
        os.makedirs(self.path, exist_ok=True)
        os.makedirs(CONFIG_PATH, exist_ok=True)
        if "config.data" not in os.listdir(CONFIG_PATH):  # TODO: Does this work?
            self.create_config()
        default, tz = self.load_config()
        self.tz = tz
        if name is None:
            if default != "":
                name = default
            else:
                clear()
                print("[SETUP] There is no default Timesheet set.  A temporary Timesheet will be created.")
                print("\nIf you have not yet created a timesheet, or need to set your default timesheet,")
                print("please do so in the 'Timesheet Management' menu.")
                _ = input("\nPress ENTER to continue...")
                name = "TEMPORARY"
        self.name = name
        self.today = pendulum.today(tz=self.tz)
        new = False
        try:
            self.load_timesheet(self.name)
        except FileNotFoundError:
            new = True
            self.tasks = None
            self.data = pd.DataFrame(index=self.tasks)
        self.init_configs()
        self.working_start = None
        self.work_day_tasks = []
        self.UI = UserInterface(name, new, self.today, VERSION)

        if ".state" in os.listdir(STATE_PATH):
            task, start = self.load_state()
            self.start_task_from_state(task, start)

        while True:
            code, string = self.UI.ask_generic_input()

            if code == '1':
                self.start_task(string)
            elif code == '2':
                if string == 'start':
                    self.working_start = time.time()
                else:
                    self.add_workday()
            elif code == '31':
                self.time_per_task(string)
            elif code == '32':
                self.time_per_day(string)
            elif code == '33':
                self.time_per_taskday(*string)
            elif code == '34':
                self.total_time()
            elif code == "35":
                self.weekly_report()
            elif code == '41':
                self.list_tasks()
            elif code == '43':
                self.delete_task(string)
            elif code == '42':
                self.add_task(string)
            elif code == '43':
                self.delete_task(string)
            elif code == '51':
                self.list_timesheets()
            elif code == '52':
                self.create_new_timesheet(string)
            elif code == '53':
                self.load_timesheet(string)
                self.UI.user_return()
            elif code == '54':
                self.delete_timesheet(string)
            elif code == '55':
                self.backup_timesheet(string)
            elif code == '56':
                self.save_config_default(string)
            elif code == '59':
                self.export()
            elif code == '57':
                self.set_baseline(string)
            elif code == '58':
                self.set_workweek(string)
            elif code == '7':
                if self.working_start is not None:
                    self.UI.banner()
                    print("[WARNING] The workday is still running!  Please stop it before exiting.")
                    self.UI.user_return()
                else:
                    sys.exit()
            elif code == 'debug':
                self.debug()

            self.UI.banner()  # places banner at top of each new page

    ################ File Management Functions ################

    def save_timesheet(self, path, name, data):
        """
        Saves current active timesheet at specified path.
        :param path: path to save
        :param name: name of Timesheet
        :param data: data of timesheet
        """
        path = pathjoin(path, "{}.pkl".format(name))
        pickle.dump(data, open(path, "wb"))

    def load_timesheet(self, name, only_data=False):
        """
        Loads a timesheet and sets all the parameters of this class to deal with the new timesheet
        :param name: name of Timesheet
        """
        if name != "":
            path = pathjoin(self.path, "{}.pkl".format(name))
            if not only_data:
                try:
                    self.data = pickle.load(open(path, "rb"))
                    self.name = name
                    self.working_start = None
                    self.UI = UserInterface(name, False, self.today, VERSION)
                    self.init_configs()
                    print("{} Timesheet loaded.".format(name))
                except FileNotFoundError:
                    self.UI.banner()
                    print("Timesheet '{}' does not exist.".format(name))
            else:
                try:
                    return pickle.load(open(path, "rb"))
                except FileNotFoundError:
                    print("[ERROR] Internal error on loading data from TS {}.  The file was not found".format(name))

    def delete_timesheet(self, name):
        """
        Deletes a timesheet.  Has a confirmation to make sure a file isn't deleted when not wanted to
        :param name: name of timesheet to delete
        """
        self.UI.banner()
        if name != "":
            decision = None
            while decision not in ["y", "n"]:
                decision = input("[WARNING] Confirm DELETION of Timesheet '{}' [y/n]: ".format(name)).lower()
            if decision == "y":
                if name == self.name:
                    print("[WARNING] Deleting current Timesheet, new current Timesheet will be the default.")
                    _ = input("\nPress ENTER to continue...")
                    try:
                        self.data = self.load_timesheet(self.load_config()[0])
                    except FileNotFoundError:
                        print("[WARNING] No default Timesheet set, creating a temporary...")
                        _ = input("\nPress ENTER to acknowledge...")
                        self.create_new_timesheet("TEMPORARY")
                os.remove(pathjoin(self.path, name + ".pkl"))
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
        print("List of Timesheets:\n")
        i = 1  # need this because it will also pick up non .pkls if using enumerate
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
        path = pathjoin(self.path, ".backup")
        os.makedirs(path, exist_ok=True)
        data = self.load_timesheet(name, only_data=True)
        self.save_timesheet(path, name, data)
        print("'{}' successfully backed up.".format(name))
        self.UI.user_return()

    def create_new_timesheet(self, name):
        """
        Creates a new timesheet with specified name
        :param name: Name of new timesheet
        """
        if name in os.listdir(self.path):
            print("Timesheet '{}' already exists.".format(name))
            self.UI.user_return()
        else:
            if name != "":
                self.name = name
                new = True
                self.tasks = None
                self.data = pd.DataFrame(index=self.tasks)
                self.UI = UserInterface(name, new, self.today, VERSION)
                self.working_start = None
                self.init_configs()
                print("New Timesheet with the name '{}' loaded.".format(name))
                self.UI.user_return()

    def export(self):
        """
        Exports data to csv after confirmation dialog
        """
        self.UI.banner()
        export = input("[WARNING] Exporting times from the current Timesheet will allow \n"
                       "anyone to view the data without the need for unpickling.\n\n"
                       "Do you wish to continue? [y/n]...")
        if export.lower() == 'y':
            self.UI.banner()
            print("Exporting Timesheet '{}' to '{}.csv'".format(self.name, self.name))
            self.data.to_csv("{}.csv".format(self.name))
            print("\nExport successful.")
            self.UI.user_return()
        elif export.lower() == 'n':
            self.UI.banner()
            print("Exporting canceled.")
            self.UI.user_return()
        else:
            self.UI.banner()
            print("[WARNING] Invalid input...not exporting.")
            self.UI.user_return()

    ################ State Functions ################

    def create_state(self, task, start):
        """
        Creates a hidden state file with the current task and time being recording so it can be started again in
        case of failure.  No need to check for existence since it will always be deleted on startup.
        :param task: task being recorded
        :param start: starting time of task
        """
        with open(pathjoin(STATE_PATH, ".state"), "w") as state:
            state.write("{}={}".format(task, start))

    def load_state(self):
        """
        Loads the information in the saved state file
        :return: the task and start time of the info in the file
        """
        with open(pathjoin(STATE_PATH, ".state"), "r") as state:
            old = state.read().split("=")
            task = old[0]
            start = old[1]
        return task, start

    def delete_state(self):
        """
        Deletes the state file
        """
        os.remove(pathjoin(STATE_PATH, ".state"))

    ################ Configuration Functions ################

    def create_config(self):
        """
        Creates a config with all parameters empty
        """
        with open(pathjoin(CONFIG_PATH, "config.data"), "w") as config:
            config.write("default_timesheet=")
            config.write("\ntz=local")

    def save_config_default(self, default):
        """
        Saves default timesheet in a text file for later usage.
        :param default: name of timesheet to set as default
        """
        self.UI.banner()
        with open(pathjoin(CONFIG_PATH, "config.data"), "r") as config:
            lines = config.readlines()
        with open(pathjoin(CONFIG_PATH, "config.data"), 'w') as config:
            config.seek(0)  # rewind
            config.write("default_timesheet={}\n".format(default))  # write the new line
            for line in lines[1:]:  # paste all future lines
                config.write(line)
        print("'{}' set as default Timesheet.".format(default))
        self.UI.user_return()

    def save_config_timesheet(self, workweek_hours, baseline):
        """
        Saves timesheet specific configurations
        Format:
        [NAME]
        workweek=40
        baseline=23h17m

        [NAME]
        workweek=
        baseline=
        :param workweek_hours: what the workweek hours are; defaults to what is loaded at start
        :param baseline: imported already worked times; defaults to what is loaded at start
        """
        if "{}-config.data".format(self.name) not in os.listdir(CONFIG_PATH):  # create it if it doesn't exist
            with open(pathjoin(CONFIG_PATH, "{}-config.data".format(self.name)), "w") as config:
                config.write("[{}]".format(self.name))
        with open(pathjoin(CONFIG_PATH, "{}-config.data".format(self.name)), "w") as config:
            if workweek_hours == None:
                workweek_hours = ""
            if baseline == None:
                baseline = ""
            config.write("[{}]".format(self.name))
            config.write("\nworkweek={}".format(workweek_hours))
            config.write("\nbaseline={}".format(baseline))

    def load_config_timesheet(self):
        """
        Loads in timesheet specific config information
        """
        with open(pathjoin(CONFIG_PATH, "{}-config.data".format(self.name)), "r") as config:
            for line in config.readlines():
                if line[:8] == "workweek":
                    workweek_line = line
                elif line[:8] == "baseline":
                    baseline_line = line
            workweek = workweek_line.split("=")[1]
            baseline = baseline_line.split("=")[1]
        return workweek[:-1], baseline  # to -2 to avoid \n

    def load_config(self):
        """
        Loads config file
        """
        with open(pathjoin(CONFIG_PATH, "config.data"), "r") as config:
            for line in config.readlines():
                if line[:7] == "default":
                    default_line = line
                elif line[:2] == "tz":
                    tz_line = line
            default = default_line.split("=")[1]
            tz = tz_line.split("=")[1]
        return default[:-1], tz  # to -2 to avoid \n

    def set_baseline(self, baseline):
        """
        Sets baseline by rewriting file and keeping everything the same except baseline
        :param baseline: the baseline to write
        """
        self.UI.banner()
        self.save_config_timesheet(self.workweek, baseline)
        print("Baseline saved for Timesheet '{}'.".format(self.name))
        self.baseline = baseline
        self.UI.user_return()

    def set_workweek(self, workweek):
        """
        Sets workweek by rewriting file and keeping everything the same except workweek
        :param workweek: the workweek to write
        """
        self.UI.banner()
        if workweek != "":
            self.workweek = int(workweek)
        else:
            self.workweek = ""
        self.save_config_timesheet(workweek, self.baseline)
        print("Workweek saved for Timesheet '{}'.".format(self.name))
        self.UI.user_return()

    def init_configs(self):
        """
        Just a function to help keep the code clean since this will appear multiple times.
        """
        try:
            workweek, baseline = self.load_config_timesheet()
            if workweek != "":
                self.workweek = int(workweek)
            else:
                self.workweek = ""
            self.baseline = baseline
        except FileNotFoundError:
            self.workweek = ""
            self.baseline = ""

    ################ Logging Functions ################

    def start_task(self, task_name):
        """
        Starts the recording process.  Quietly calls _end_task when done, to record the time into the data.  Creates a
        new task if provided task is not already existing.
        :param task_name: task to record
        """
        go_on = True
        if task_name != "":
            if task_name not in self.data.index:
                self.UI.banner()
                add = input(
                    "[WARNING] '{}' is not in the list of Tasks...would you like to add it? [y/n]...".format(task_name))
                if add.lower() == 'y':
                    self.add_task(task_name, suppress=True)
                    go_on = True
                elif add.lower() == 'n':
                    go_on = False
                else:
                    print("[WARNING] Invalid input...not creating new Task and returning to the main menu...")
                    go_on = False
                    self.UI.user_return()
            if go_on:
                if self.today.to_date_string() not in self.data.columns:
                    self.data[self.today.to_date_string()] = 0
                start_time = time.time()
                # Save the state in case of crashes:
                self.create_state(task_name, start_time)
                # Start the UI logging time, once stopped through the UI, record the time
                self.UI.timelogger(task_name)
                self._end_task(task_name, start_time)

    def start_task_from_state(self, task_name, start):
        """
        Starts recording time on the given task and then adds on previously recorded time.

        ASSUMES TASK WAS CONTINUED CONTINUOUSLY FROM INITIAL START
        # TODO: Allow resuming task on a different day
        :param task_name: task to resume
        :param start: old starting time
        """
        start = float(start)
        self.UI.timelogger(task_name, start)
        self._end_task(task_name, start)

    def _end_task(self, name, start_time):
        """
        Quietly called from start_task.  Ends the task and records the time by adding it to the time already recorded
        for that task
        :param name: task to record
        """
        self.UI.banner()
        self.data.at[name, self.today.to_date_string()] += int(time.time() - start_time)  # do not care about ms
        print("Logging of Task '{}' stopped...".format(name))
        self.save_timesheet(self.path, self.name, self.data)
        print("Time successfully recorded!")
        self.delete_state()
        if self.working_start:
            if name != "General":
                self.work_day_tasks.append(name)
        self.UI.user_return()
        self.UI.banner()

    def add_workday(self):
        """
        Adds to task "general" all the time during the workday that was not already assigned to a task.
        """
        work_time = time.time() - self.working_start
        self.UI.banner()
        if self.today.to_date_string() not in self.data.columns:
            self.data[self.today.to_date_string()] = 0
        if "General" not in self.data.index:
            print("No Task exists to log general work time...creating Task 'General'")
            self.add_task("General")
        allocated_time = []
        for task in self.work_day_tasks:
            allocated_time.append(self.data[self.today.to_date_string()].loc[task])
        workday = work_time - sum(allocated_time)
        self.work_day_tasks = []
        self.working_start = None
        if workday < 0:
            print("[ERROR] Workday length was negative time.  Did you start your workday properly?")
            print("[DEBUG] workday={}, worktime={}".format(workday, work_time))
            self.UI.user_return()
        else:
            self.UI.banner()
            self.data.at["General", self.today.to_date_string()] += int(workday)  # do not care about ms
            work_time_mins = Converter.sec2min(work_time)
            work_time_hours, work_time_mins = Converter.min2hour(work_time_mins)
            work_hour_min_string = Converter.convert2string(int(work_time_hours), int(work_time_mins))
            general = self.data.at["General", self.today.to_date_string()]
            mins = Converter.sec2min(general)
            hours, mins = Converter.min2hour(mins)
            hour_min_string = Converter.convert2string(int(hours), int(mins))
            print("Total hours accumulated during the work day: {}".format(work_hour_min_string))
            print("Total hours set as general tasks: {}".format(hour_min_string))
            print("\nWork day ended!")
            self.save_timesheet(self.path, self.name, self.data)
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

    def add_task(self, task_name, suppress=False):
        """
        Adds task to the dataframe by adding it to the index.  If the task already exists, it exits.
        Can take string or [str].
        :param task_name: name of task to add
        :param suppress: suppresses user blocking input
        """
        self.UI.banner()
        if task_name in self.data.index:
            print("Task '{}' already in Timesheet '{}'.".format(task_name, self.name))
            self.UI.user_return()
        else:
            if task_name != "":
                if type(task_name) == str:
                    task_name = [task_name]
                new_task = pd.DataFrame(index=task_name)
                self.data = self.data.append(new_task, verify_integrity=True, sort=False)
                print("Task '{}' created.".format(task_name[0]))
                self.data.fillna(0, inplace=True)
                self.save_timesheet(self.path, self.name, self.data)
                if not suppress: self.UI.user_return()

    def delete_task(self, task_name):
        """
        Deletes task from the data.  If it doesn't exist, it does nothing.
        :param task_name: task to delete
        """
        self.UI.banner()
        if task_name not in self.data.index:
            if task_name != "":
                print("'{}' task not in database.".format(task_name))
                self.UI.user_return()
        else:
            self.data.drop(task_name, inplace=True)
            self.save_timesheet(self.path, self.name, self.data)
            print("Task '{}' successfully deleted.".format(task_name))
            self.UI.user_return()

    ################ Time Functions ################

    def time_per_day(self, day):
        """
        Reports total time worked on given day
        :param day: day to report
        """
        self.UI.banner()
        if day == "today":
            day = self.today.to_date_string()
        elif day == "yesterday":
            day = pendulum.yesterday(tz=self.tz).to_date_string()
        if day not in self.data.columns:
            print("There is no data for the selected date ({}).".format(day))
        else:
            times = self.data[day].sum()
            if times == 0:
                print("No Tasks were logged on {}.".format(day))
            else:
                mins = Converter.sec2min(times)
                hours, mins = Converter.min2hour(mins)
                hour_min_string = Converter.convert2string(int(hours), int(mins))
                string = "Summary for {}:".format(day)
                print(string)
                self.UI.summary_divider(string)
                if hours == 0:
                    print(hour_min_string.split(", ")[1])
                else:
                    print(hour_min_string)

                if type(self.workweek) == int:
                    per_day_minutes = (self.workweek / 5) * 60
                    per_day_hours, per_day_minutes = Converter.min2hour(per_day_minutes)

                    diff_hours, diff_mins = TimeCalculator.subtract(per_day_hours, per_day_minutes, hours, mins)
                    print("\nWith a workweek of {} hours, "
                          "the average daily hours equates to: {}.".format(self.workweek,
                                                                           Converter.convert2string(int(per_day_hours),
                                                                                                    int(per_day_minutes)
                                                                                                    )))  # ugly lol
                    if diff_hours is not None:
                        print("{} is left remaining.".format(Converter.convert2string(int(diff_hours), int(diff_mins))))
                    else:
                        print("Sufficient hours have been worked today to meet that amount.")
        self.UI.user_return()

    def time_per_task(self, task):
        """
        Reports total time worked for given task
        :param task: task to report
        """
        self.UI.banner()
        if task not in self.data.index:
            print("There is no Task named '{}'.".format(task))
        else:
            times = self.data.loc[task].sum()
            if times == 0:
                print("No time was logged for Task '{}'.".format(task))
            else:
                mins = Converter.sec2min(times)
                hours, mins = Converter.min2hour(mins)
                hour_min_string = Converter.convert2string(int(hours), int(mins))
                days, hours_day = Converter.hour2day(hours)
                day_hour_min_string = Converter.convert2string_days(int(days), int(hours_day), int(mins))
                string = "Summary for '{}':".format(task)
                print(string)
                self.UI.summary_divider(string)
                if hours == 0:
                    print(hour_min_string.split(", ")[1])
                else:
                    print(hour_min_string)
                if days != 0: print(day_hour_min_string)
        self.UI.user_return()

    def time_per_taskday(self, task, day):
        """
        Reports total time for a given task on a given day
        :param task: task to report
        :param day: day to report on
        """
        self.UI.banner()
        skip = False
        if day == "today":
            day = self.today.to_date_string()
        elif day == "yesterday":
            day = pendulum.yesterday(tz=self.tz).to_date_string()
        if task not in self.data.index:
            print("There is no Task named '{}'.".format(task))
            skip = True
        if day not in self.data.columns:
            print("There is no data for the selected date ({}).".format(day))
            skip = True
        if not skip:
            times = self.data[day].loc[task]
            if times == 0:
                print("No time was logged for Task '{}' on {}.".format(task, day))
            else:
                mins = Converter.sec2min(times)
                hours, mins = Converter.min2hour(mins)
                hour_min_string = Converter.convert2string(int(hours), int(mins))
                string = "Summary for '{}' on {}:".format(task, day)
                print(string)
                self.UI.summary_divider(string)
                if hours == 0:
                    print(hour_min_string.split(", ")[1])
                else:
                    print(hour_min_string)
        self.UI.user_return()

    def total_time(self):
        """
        Report on total time worked
        """
        self.UI.banner()
        times = self.data.values.sum()
        if times == 0:
            print("No time has been logged in this Timesheet yet.")
        else:
            mins = Converter.sec2min(times)
            hours, mins = Converter.min2hour(mins)
            hour_min_string = Converter.convert2string(int(hours), int(mins))
            days, hours_day = Converter.hour2day(hours)
            day_hour_min_string = Converter.convert2string_days(int(days), int(hours_day), int(mins))
            string = "Summary of all time worked stored in Timesheet '{}':".format(self.name)
            print(string)
            self.UI.summary_divider(string)
            if hours == 0:
                print(hour_min_string.split(", ")[1])
            else:
                print(hour_min_string)
            print(day_hour_min_string)
            if self.baseline != "":
                string = "Summary of all time worked including baseline:"
                print("\n" + string)
                self.UI.summary_divider(string)
                back_days, back_hours, back_mins = Converter.parse_DHM(self.baseline)
                total_days = back_days + days
                total_hours = back_hours + hours_day
                total_mins = back_mins + mins
                total_worked_hours = (back_days * 24) + back_hours + hours
                print(Converter.convert2string(int(total_worked_hours), int(mins)))
                print(Converter.convert2string_days(int(total_days), int(total_hours), int(total_mins)))
            print("\nSince the creation of this Timesheet, {} individual days have been worked.".format(
                len(self.data.columns.values)))
        self.UI.user_return()

    def weekly_report(self):
        self.UI.banner()
        workdays = get_current_week_days(self.today)
        summable_days = workdays
        tasks = self.data.index
        report_data = generate_day_dict(workdays, tasks)
        # Fill up dictionary with data
        deletable = []
        for day in workdays:
            for task in tasks:
                try:
                    report_data[day][task] = self.data[day].loc[task]
                except KeyError:
                    report_data[day][task] = 0
                    deletable.append(day)
        for delete in set(deletable):  # to remove duplicates
            summable_days.remove(delete)
        # Get max length of tasks so that spacing works out
        max_len = 0
        for task in tasks:
            if len(task) > max_len:
                max_len = len(task)
        # Start report
        string = "Current Week Report"
        print(string)
        self.UI.summary_divider(string)
        for day in reversed(workdays):
            day_string = day
            day = pendulum.parse(day)
            print("{}, {}".format(Converter.convert_int2day(day.day_of_week), day_string[5:]))
            print("-" * 16)  # length of Wednesday string
            for task in tasks:
                value = report_data[day_string][task]
                if value != 0:
                    mins = Converter.sec2min(value)
                    hours, mins = Converter.min2hour(mins)
                    hour_min_string = Converter.convert2string(int(hours), int(mins))
                    if len(task) < max_len:
                        string = "{}:".format(task) + (" " * (max_len - len(task)))
                    else:
                        string = "{}:".format(task)
                    if hours == 0 and mins != 0:
                        hour_min_string = hour_min_string.split(", ")[1]
                        print("\t" + string + "\t{}".format(hour_min_string))
                    elif hours == 0 and mins == 0:
                        continue
                    else:
                        print("\t" + string + "\t{}".format(hour_min_string))

        print("\n------------")
        print("Weekly Total")
        print("------------")
        total = int(self.data[summable_days].sum().sum())
        mins = Converter.sec2min(total)
        hours, mins = Converter.min2hour(mins)
        hour_min_string = Converter.convert2string(int(hours), int(mins))
        days, hours_day = Converter.hour2day(hours)
        day_hour_min_string = Converter.convert2string_days(int(days), int(hours_day), int(mins))
        if days == 0:
            if hours == 0:
                print(hour_min_string.split(", ")[1])
            else:
                print(hour_min_string)
        else:
            print(hour_min_string)
            print(day_hour_min_string)

        if type(self.workweek) == int:
            if hours > self.workweek:
                print("Sufficient hours have been worked this week to meet the workweek requirements.")
            else:
                diff = self.workweek - hours
                print("{} hours still need to be worked this week in order to meet workweek requirements.".format(diff))
        self.UI.user_return()

    ################ Debug Functions ################

    def debug(self):
        self.UI.banner()
        print("[DEBUG] Printing head(20) of underlying dataframe...\n")
        print(self.data.head(20))
        self.UI.user_return()


if __name__ == "__main__":
    t = TimesheetManager()
