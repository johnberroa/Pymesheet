import pandas as pd
import pendulum, time, os, sys, pickle
from pyfiglet import Figlet

VERSION = ".2"


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


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
        self.UI = UserInterface(name, new, self.today)
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

    def start_task(self, task_name): #TODO TIEMES DO NOT ADD TO EACHOTHER
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


class UserInterface:
    def __init__(self, name, new, today):
        self.__version__ = VERSION
        self.today = today
        self.name = name
        self.banner()
        if new:
            print("New Timesheet created for '{}'!".format(name))
        else:
            print("Timesheet for '{}' loaded!".format(name))

    def _main_divider(self):
        print("=" * 80)

    def banner(self):
        clear()  # FOR DEBUGGING, COMMENT OUT
        self._main_divider()
        f = Figlet(font='doom')
        print(f.renderText('Timesheet'))
        print("Welcome to Timesheet v{}!\nToday's date: {}".format(self.__version__,
                                                                   self.today.to_formatted_date_string()))
        self._main_divider()

    def _help(self, which):
        self.banner()
        if which == "main": # TODO: WRONG
            print("Timesheet is a program to keep track of times on your tasks to the second.")
            print("It can track any number of tasks, and persists your work log indefinitely.")
            print("Various summary functions allow you to analyze your time effortlessly.")
            print("\nIn the main menu, you can...")
            print("1) Start logging time for a Task:\n  -Record time worked on a specific Task.")
            print("2) Get time summaries:\n  -Get statistics on data within the Timesheet.")
            print("3) Task management:\n  -Create, delete, and list Tasks within the Timesheet.")
            print("4) Timesheet management:\n  -Create, delete, load, and backup Timesheets.")
            print("5) Help:\n  -Print this page.")
            print("5) Quit:\n  -Exit the program.")
            self.user_return()

        elif which == "timesheet":
            raise NotImplementedError
        elif which == "task":
            print("Here you can create, delete, or list the tasks within the '{}' Timesheet.\n".format(self.name))
            print("1) List Tasks:\n  -Returns a list of all Tasks within the Timesheet file, enumerated.")
            print("2) Create new Task:\n  -Creates a new Task with the desired name if it does not already exist.")
            print("3) Delete a Task:\n  -Deletes a Task with the desired name.")
            print("4) Help:\n  -Print this usage page.")
            print("5) Return:\n  -Return to the main menu.")
            self.user_return()

    def user_return(self):
        _ = input("\nPress ENTER to return...")

    def ask_generic_input(self):
        print("Active Timesheet - '{}'\n".format(self.name))
        print("Please select desired function:\n")
        print("\t[1] Start logging time for a Task...")
        print("\t[2] Get time summaries...")
        print("\t[3] Task management...")
        print("\t[4] Timesheet management...")
        print("\t[5] Help")
        print("\t[6] Quit")
        selection = input("\t...")
        if selection == "1":  # Log time
            task = self._ask_what_task(work=True)
            return selection, task
        elif selection == '2':  # Summary
            raise NotImplementedError
        elif selection == '3':  # Task management
            second_selection, task = self.ask_task_management_input()
            selection = selection + second_selection
            return selection, task
        elif selection == '4':  # Timesheet management
            self.ask_timesheet_management_input()
        elif selection == '5':  # Help
            self._help("main")
            return 0, '0'
        elif selection == '6':  # Quit
            self.banner()
            print("Exiting...")
            sys.exit()

    def ask_timesheet_management_input(self):
        self.banner()
        print("Please select desired Timesheet management function:\n")
        print("\t[1] Create new Timesheet...")
        print("\t[2] Load a Timesheet...")
        print("\t[2] Delete a Timesheet...")
        print("\t[2] Backup a Timesheet...")
        print("\t[3] Help")
        print("\t[4] Return")
        selection = input("\t...")
        print("[WARNING] NOTHING IN MANAGEMENT IS CURRENTLY IMPLEMENTED...RETURNING TO MAIN MENU IN 5 SECONDS...")
        time.sleep(5)

    def ask_task_management_input(self):
        self.banner()
        print("Please select desired Task management function:\n")
        print("\t[1] List Tasks")
        print("\t[2] Create new Task...")
        print("\t[3] Delete a Task...")
        print("\t[4] Help")
        print("\t[5] Return")
        selection = input("\t...")
        if selection == "1":  # List tasks
            return selection, None
        elif selection == "2":  # Create new task
            task = self._ask_what_task(add=True)
            return selection, task
        elif selection == '3':  # Delete task
            task = self._ask_what_task(delete=True)
            return selection, task
        elif selection == '4':  # Help task
            self._help("task")
            return selection, None
        elif selection == '5':  # Return
            return selection, None
        # TODO: invalid input case

    def _ask_what_task(self, work=False, add=False, delete=False):
        self.banner()
        if work:
            task = input("\nLog work for which task?\n\t...")
        elif add:
            task = input("\nAdd which task?\n\t...")
        elif delete:
            task = input("\nDelete which task?\n\t...")
        return task  # TODO: make robust? or is it?

    def timelogger(self, name, start_time):
        self.banner()
        print("Starting to log time on {} at {}".format(name, start_time))
        while input("\nPress ENTER to end logging...") != "": continue

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
