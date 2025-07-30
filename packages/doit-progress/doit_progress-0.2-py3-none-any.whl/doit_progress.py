import time

from doit.cmd_base import DoitCmdBase


opt_bar_length = {
    'name': 'bar_length',
    'short': '',
    'long': 'bar-length',
    'type': int,
    'default': 50,
    'help': "Progress bar length"
    }


opt_interactive = {
    'name': 'interactive',
    'short': 'i',
    'long': 'interactive',
    'type': bool,
    'default': False,
    'help': "Run in interactive mode, showing progress bar updates"
}


class ProgressCmd(DoitCmdBase):
    name = "progress"
    doc_purpose = "Show the overall progress of tasks"
    doc_usage = ""
    cmd_options = (opt_bar_length, opt_interactive)
    doc_description = """
    Show the overall progress of all tasks defined in the dodo file.
    """

    def _execute(self, bar_length=50, interactive=False, pos_args=None):
        tasks = {task.name: task for task in self.task_list}

        try:
            if interactive:
                while True:
                    self._calculate_print_progress(tasks, bar_length)
                    time.sleep(1)
            else:
                self._calculate_print_progress(tasks, bar_length)
        except KeyboardInterrupt:
            print("\nProgress monitoring interrupted by user.")
        finally:
            self.dep_manager.close()

    def _calculate_print_progress(self, tasks, bar_length):
        up_to_date = [task for task in self.task_list
                      if self.dep_manager.get_status(task, tasks).status == "up-to-date"]
        self.print_progress(progress=len(up_to_date) / len(self.task_list),
                            bar_length=bar_length)

    @staticmethod
    def print_progress(progress, bar_length=50):
        """
        Print a progress bar to the terminal.

        :param progress: A float between 0 and 1 indicating the progress.
        :param bar_length: The length of the progress bar in characters.
        """
        # Calculate the number of filled and empty slots
        filled_length = int(round(bar_length * progress))
        empty_length = bar_length - filled_length

        # Create the progress bar string using block characters
        bar = '█' * filled_length + '░' * empty_length

        # Print the progress bar
        print(f'\rProgress: |{bar}| {progress * 100:.2f}% Complete')
