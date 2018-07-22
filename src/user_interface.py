"""
User interface for the Timesheet class
Command line user interface for ease of use of logging time and other functions.
@author: John Berroa
"""
import time, os, sys, re
from pyfiglet import Figlet


def clear():
    """
    Global function that clears the command line
    """
    os.system('cls' if os.name == 'nt' else 'clear')


class UserInterface:
    def __init__(self, name, new, today, version):
        self.__version__ = version
        self.today = today
        self.name = name
        self.banner()
        if new:
            print("New Timesheet created for '{}'!".format(name))
        else:
            print("Timesheet for '{}' loaded!".format(name))

    ################ UI Printing Functions ################

    def _main_divider(self):
        """
        Prints a row of === for a divider
        """
        print("=" * 80)

    def summary_divider(self):
        """
        Prints a row of --- for a divider
        """
        print("-" * 40)

    def banner(self):
        """
        Prints the banner.  Calling this function clears the screen.
        """
        clear()  # FOR DEBUGGING, COMMENT IT OUT
        self._main_divider()
        f = Figlet(font='doom')
        print(f.renderText('Timesheet'))
        print("Welcome to Timesheet v{}!\nToday's date: {}".format(self.__version__,
                                                                   self.today.to_formatted_date_string()))
        print("Active Timesheet: '{}'\n".format(self.name))
        self._main_divider()


    ################ Main Page ################

    def ask_generic_input(self):
        """
        Main menu. This function talks to the timesheet class
        :return: selection number (what function to use in timesheet), and task name if applicable
        """
        print("Please select desired function:\n")
        print("\t[1] Start logging time for a Task...")
        print("\t[2] Get time summaries...")
        print("\t[3] Task management...")
        print("\t[4] Timesheet management...")
        print("\t[5] Help")
        print("\t[6] Quit")
        selection = None
        while selection not in ["1", "2", "3", "4", "5", "6"]:
            selection = input("\t...")
            if selection == "1":  # Log time
                task = self._ask_what_string(work=True)
                return selection, task
            elif selection == '2':  # Summary
                second_selection, summary_request = self.ask_time_summaries_input()
                selection = selection + second_selection
                return selection, summary_request
            elif selection == '3':  # Task management
                second_selection, task = self.ask_task_management_input()
                selection = selection + second_selection
                return selection, task
            elif selection == '4':  # Timesheet management
                second_selection, sheet = self.ask_timesheet_management_input()
                selection = selection + second_selection
                return selection, sheet
            elif selection == '5':  # Help
                self._help("main")
                return 0, '0'
            elif selection == '6':  # Quit
                self.banner()
                print("Exiting...")
                sys.exit()

    ################ Sub Pages ################

    def _help(self, which):
        """
        Prints the various help pages.  Which one is determined by the which parameter.
        :param which: which help page to print
        """
        self.banner()
        if which == "main":
            print("Timesheet is a program to keep track of times on your tasks to the second.")
            print("It can track any number of tasks, and persists your work log indefinitely.")
            print("Various summary functions allow you to analyze your time effortlessly.")
            print("When selecting Timesheets or Tasks, you have to type out their full names.")
            print("This is to prevent accidental deletions.")
            print("\nIn the main menu, you can...")
            print("1) Start logging time for a Task:\n  -Record time worked on a specific Task.")
            print("2) Get time summaries:\n  -Get statistics on data within the Timesheet.")
            print("3) Task management:\n  -Create, delete, and list Tasks within the Timesheet.")
            print("4) Timesheet management:\n  -Create, delete, load, and backup Timesheets.")
            print("5) Help:\n  -Print this page.")
            print("6) Quit:\n  -Exit the program.")
            self.user_return()
        elif which == "timesheet":
            print("Here you can create, delete, load, list, or backup Timesheets.\n")
            print("1) List Timesheets:\n  -Returns a list of all saved Timesheets.")
            print("2) Create new Timesheet:\n  -Create a new Timesheet with a specific name.")
            print("3) Load a Timesheet:\n  -Load a Timesheet with a given name.")
            print("4) Delete a Timesheet:\n  -Delete a Timesheet with a given name.")
            print("5) Backup a Timesheet:\n  -Backup a Timesheet in another location (backups folder).")
            print("6) Set default Timesheet:\n  -Set the Timesheet to open on a fresh start of the program.")
            print("7) Help:\n  -Print this page.")
            print("8) Return:\n  -Return to the main menu.")
            self.user_return()
        elif which == "task":
            print("Here you can create, delete, or list the tasks within the '{}' Timesheet.\n".format(self.name))
            print("1) List Tasks:\n  -Returns a list of all Tasks within the Timesheet file, enumerated.")
            print("2) Create new Task:\n  -Creates a new Task with the desired name if it does not already exist.")
            print("3) Delete a Task:\n  -Deletes a Task with the desired name.")
            print("4) Help:\n  -Print this usage page.")
            print("5) Return:\n  -Return to the main menu.")
            self.user_return()
        elif which == "summary":
            raise NotImplementedError

    def ask_time_summaries_input(self):
        """
        Page for time summaries.
        :return: selection and sheet to fulfill requirements by TimesheetManager for a return
        """# TODO: OVertime section, daily, total, per task
        self.banner()
        print("Please select desired summary:\n")
        print("\t[1] Time per Task...")
        print("\t[2] Time per day...")
        print("\t[3] Time per Task per day...")
        print("\t[4] Total Time")
        print("\t[5] Paid/Actual Time")
        print("\t[6] Help")
        print("\t[7] Return")
        selection = None
        while selection not in ["1", "2", "3", "4", "5", "6", "7"]:
            selection = input("\t...")
            if selection == "1":  # time per task
                return selection, None
            elif selection == "2":  # time per day
                day = self._ask_for_day()
                return selection, day
            elif selection == "3":  # time per task per day
                sheet = self._ask_what_string(load=True)
                return selection, sheet
            elif selection == '4':  # total time
                sheet = self._ask_what_string(remove=True)
                return selection, sheet
            elif selection == '5':  # paid/actual
                sheet = self._ask_what_string(backup=True)
                return selection, sheet
            # elif selection == '6':  # help
            #     self._help("summary")
            #     return selection, None
            # elif selection == '7':  # Help
            #     return selection, None


    def ask_timesheet_management_input(self):
        """
        Page for timesheet management.
        :return: selection and sheet to fulfill requirements by TimesheetManager for a return
        """
        self.banner()
        print("Please select desired Timesheet management function:\n")
        print("\t[1] List Timesheets")
        print("\t[2] Create new Timesheet...")
        print("\t[3] Load a Timesheet...")
        print("\t[4] Delete a Timesheet...")
        print("\t[5] Backup a Timesheet...")
        print("\t[6] Set default Timesheet...")
        print("\t[7] Help")
        print("\t[8] Return")
        selection = None
        while selection not in ["1", "2", "3", "4", "5", "6", "7", "8"]:
            selection = input("\t...")
            if selection == "1":  # List timesheets
                return selection, None
            elif selection == "2":  # Create new sheet
                sheet = self._ask_what_string(create=True)
                return selection, sheet
            elif selection == "3":  # Load a sheet
                sheet = self._ask_what_string(load=True)
                return selection, sheet
            elif selection == '4':  # Delete a sheet
                sheet = self._ask_what_string(remove=True)
                return selection, sheet
            elif selection == '5':  # Backup a sheet
                sheet = self._ask_what_string(backup=True)
                return selection, sheet
            elif selection == '6':  # Default
                sheet = self._ask_what_string(default=True)
                return selection, sheet
            elif selection == '7':  # Help
                self._help("timesheet")
                return selection, None
            elif selection == '8':  # Return
                return selection, None

    def ask_task_management_input(self):
        """
        Page for task management.  Returns the task name for a function to be applied to.
        :return: selection and task to fulfill requirements by TimesheetManager for a return
        """
        self.banner()
        print("Please select desired Task management function:\n")
        print("\t[1] List Tasks")
        print("\t[2] Create new Task...")
        print("\t[3] Delete a Task...")
        print("\t[4] Help")
        print("\t[5] Return")
        selection = None
        while selection not in ["1", "2", "3", "4", "5"]:
            selection = input("\t...")
            if selection == "1":  # List tasks
                return selection, None
            elif selection == "2":  # Create new task
                task = self._ask_what_string(add=True)
                return selection, task
            elif selection == '3':  # Delete task
                task = self._ask_what_string(delete=True)
                return selection, task
            elif selection == '4':  # Help task
                self._help("task")
                return selection, None
            elif selection == '5':  # Return
                return selection, None

    ################ Specific User Inputs ################

    def user_return(self): #TODO: Dependencies list
        """
        Tells the user to hit enter to return, but works for any key (doesn't matter what they press, just need a press)
        """
        _ = input("\nPress ENTER to return...")

    def _ask_what_string(self, work=False, add=False, delete=False, load=False, remove=False, backup=False,
                         create=False, default=False):
        """
        Asks for a task/sheet, and the prompt depends on the context.
        :param work: context for string output (task)
        :param add: context for string output (task)
        :param delete: context for string output (task)
        :param load: context for string output (timesheet)
        :param remove: context for string output (timesheet)
        :param backup: context for string output (timesheet)
        :return: task name
        """
        self.banner()
        if work:
            string = input("Log work for which Task?\n\t...")
        elif add:
            string = input("Add which Task?\n\t...")
        elif delete:
            string = input("Delete which Task?\n\t...")
        elif load:
            string = input("Load which Timesheet?\n\t...")
        elif remove:
            string = input("Delete which Timesheet?\n\t...")
        elif backup:
            string = input("Backup which Timesheet?\n\t...")
        elif create:
            string = input("What will the new Timesheet be called?\n\t...")
        elif default:
            string = input("What Timesheet will be the default?\n\t...")
        return string

    def _ask_for_day(self):
        DATE_REGEX = r"^\d{4}-\d{2}-\d{2}$"
        self.banner()
        day = ""
        valid = False
        while not re.match(DATE_REGEX, day) and valid == False:
            if day.lower() == "today" or day.lower() == "yesterday":
                return day
            else:
                day = input("What day do you want to summarize?\n\tAvailable options:\n\t"
                      "1. YYYY-MM-DD\n\t"
                      "2. Today\n\t"
                      "3. Yesterday\n\t...")
                valid = self._check_date_validity(day)
        return day

    ################ Specific Functions ################

    def timelogger(self, name):
        """
        Page for starting the logging of time.
        :param name: name of task
        """
        start_time = time.strftime("%H:%M:%S", time.gmtime()) # may lose a second on loading time between functions
        self.banner()
        print("Starting to log time on {} at {}".format(name, start_time))
        while input("\nPress ENTER to end logging...") != "": continue

    def _check_date_validity(self, date):
        """
        Checks if the date is a valid date, i.e. the month isn't 77.
        :param date: potential date string
        :return: boolean
        """
        if len(date) == 10 and int(date[5:7]) <= 12 and int(date[-2:]) <= 31:
            return True
        return False
