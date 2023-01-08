from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.core.text.markup import MarkupLabel
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.utils import platform
from backup_functions import start, log
from random import randint

# to create executable
import os, sys
from kivy.resources import resource_add_path, resource_find


class WelcomeScreen(Screen):
    def get_most_recent_backup_date(self):
        with open(BackupApp.resource_path('files/most_recent_backup.txt'), 'r') as f:
            recent_datetime = f.read()
        return recent_datetime
        # on_enter these ids haven't been created yet
        # self.ids.lbl_latest_backup_date.text = recent_datetime

    def take_backup(self):
        self.manager.current = "default_screen"
        pass

    def see_log(self):
        self.manager.current = "log_screen"

    def clear_log(self):
        self.manager.current = 'clear_log_screen'

    def see_help(self):
        self.manager.current = "help_screen"

    @staticmethod
    def close_app():
        exit()


class DefaultScreen(Screen):
    def on_enter(self):
        with open(BackupApp.resource_path('files/dir_from'), 'r') as f:
            dir_from = f.read()
        with open(BackupApp.resource_path('files/dir_to'), 'r') as f:
            dir_to = f.read()
        self.ids.lbl_default_from.text = dir_from
        self.ids.lbl_default_to.text = dir_to

    def use_current_selection(self, root):
        # go to prOgress screen and trigger backup
        root.manager.current = 'progress_screen'

    def select_new_folders(self, root):
        root.manager.current = 'drive_selection_screen_from'


class DriveSelector(RecycleView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def switch_to_target_screen(self):
        # which screen is the recycleview in?
        # pass that value to parent_screen object
        app = App.get_running_app()
        sm = app.root.ids.sm
        if "_from" in sm.current:
            sm.current = 'selection_screen'
            ss = app.root.ids.ss_from
        else:
            sm.current = 'selection_screen_to'
            ss = app.root.ids.ss_from
        return ss

    def refresh_view(self):
        # take out of init so we can call if via the kv id
        # root_widget is set to self, so, the recycleview, so that we can link the
        # recycleview buttons with a function in recycleview
        self.data = [{'text': str(x), 'root_widget': self} for x in self.get_available_drives()]

    def get_available_drives(self):
        # for linux drives need to be mounted
        # for Windows you need to get the logical drives
        # TODO how does this work for MAC?
        if platform == "win":
            pass
            drives = ['C:\\', 'D:\\']
            return [x[:-1] for x in drives]
        elif platform == 'linux':
            # don't select a different filechooser path
            # TODO; update the screen selection above to skip this screen for linux
            # TODO: remove the below after testing
            # drives = [f'{x}:\\' for x in range(randint(0, 10))]
            drives = ['C:\\', 'D:\\']
            return [x[:-1] for x in drives]
        else:
            print(f'update app for {platform}')
            return []

    def goToUpdate(self, text):
        # I need to know which screen to go to
        # that depends on where I am in the process
        # so that's the page in which my recycleview sits
        # change screen and capture new screen object
        target_screen = self.switch_to_target_screen()
        # change file chooser path in target screen
        # file_chooser_obj is created in kv file
        target_screen.file_chooser_obj.path = text
        # TODO test this in Windows





class SelectionRecycleView(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.header_text = StringProperty('')

    def on_enter(self, *args, **kwargs):
        # on_enter of the SelectionRecycleView (not the RecycleView itself)
        # we want to update the content of the RecycleView (connected drives)
        self.ids.rv_drives.refresh_view()


class DriveSelectionScreenFrom(SelectionRecycleView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header_text = "Select drive to backup FROM"


class DriveSelectionScreenTo(SelectionRecycleView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header_text = 'Select drive to backup TO'


class SelectionScreen(Screen):
    class FileChooser(BoxLayout):

        def select(self, *args, root):
            # args is a tuple with one list element
            # (['/home/xubuntu'],)
            # (['/home/xubuntu/Documents/_notes_to_process/how_to.txt'],)
            # update the from_label in the SelectionScreen
            root.ids.from_label.text = args[0][0]

        def confirm_selection(self, *args, root, from_or_to):
            if from_or_to == 'from':
                with open(BackupApp.resource_path('files/dir_from'), 'w') as f:
                    f.write(root.ids.from_label.text)
                app = App.get_running_app()
                sm = app.root.ids.sm
                sm.current = 'selection_screen_to'
            elif from_or_to == 'to':
                with open(BackupApp.resource_path('files/dir_to'), 'w') as f:
                    f.write(root.ids.from_label.text)
                app = App.get_running_app()
                sm = app.root.ids.sm
                sm.current = 'confirmation_screen'

                # populate the labels
                # id's don't exist yet
                # root.ids.conf_from_label.text = 'test function'
                # root.ids.conf_to_label.text = 'test function rr'
            else:
                exit()


class ConfirmationScreen(Screen):
    def on_enter(self):
        with open(BackupApp.resource_path('files/dir_from'), 'r') as f:
            dir_from = f.read()
        with open(BackupApp.resource_path('files/dir_to'), 'r') as f:
            dir_to = f.read()
        self.ids.conf_from_label.text = dir_from
        self.ids.conf_to_label.text = dir_to

    def confirmed(self):
        app = App.get_running_app()
        sm = app.root.ids.sm
        sm.current = 'progress_screen'

    def get_from_dir(self):
        with open(BackupApp.resource_path('files/dir_from'), 'r') as f:
            print(f.read())
            return f.read()

    def get_to_dir(self):
        with open(BackupApp.resource_path('files/dir_to'), 'r') as f:
            print(f.read())
            return f.read()


class ProgressScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.progress_label_update = None

    def on_enter(self):
        # in the background, run the update_label function every 1/100 seconds
        self.progress_label_update = Clock.schedule_interval(self.update_label, 1 / 100)
        # for testing, stop the label update after 20 seconds
        # while testing schedule interval i'll stop the clock after 20 seconds
        # Clock.schedule_once(self.cancel_update_label, 20)

        # Start the backup process from here
        # ==================================
        # clear recent back up log
        with open(BackupApp.resource_path('backup_log_recent.txt'), 'w') as f:
            f.write('')
        with open(BackupApp.resource_path('files/dir_from'), 'r') as f:
            source_dir = f.read()
        with open(BackupApp.resource_path('files/dir_to'), 'r') as f:
            destination_dir = f.read()
        start(source_dir, destination_dir)
        # Show 'backup complete'
        # log() updates the log, and the clock functions updates the label
        # via the update label function
        log('Back up Complete !')

    def update_label(self, *args):
        with open(BackupApp.resource_path('backup_log_recent.txt'), 'r') as f:
            log_content = f.read()
        self.ids.lbl_progress.text = log_content
        # stop checking for label updates. Process is done
        if log_content == 'Back up Complete !':
            self.cancel_update_label()

    def cancel_update_label(self, *args):
        self.progress_label_update.cancel()


class InfoScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use this class and kv equivalent as a template and parent class
        self.header_text = StringProperty('')
        self.label_text = StringProperty('')


class LogScreen(InfoScreen):
    def __init__(self, *args, **kwargs):
        # inherits from InfoScreen
        super().__init__(*args, **kwargs)
        self.header_text = 'Your Current Log'
        with open(BackupApp.resource_path('backup_log.txt'), 'r') as f:
            log_content = f.read()
        self.label_text = log_content
        self.size_hint_label_y = 3

    def on_enter(self):
        # so that log refreshes even you have checked it before
        # in the background, run the update_label function every 1/100 seconds
        Clock.schedule_interval(self.update_label, 1 / 100)

    def update_label(self, *args):
        with open(BackupApp.resource_path('backup_log.txt'), 'r') as f:
            log_content = f.read()
        # for the label to update you need to call the ID
        # just using the assignment below doesn't work
        # self.label_text = log_content
        self.ids.lbl_info.text = log_content


class HelpScreen(InfoScreen):
    def __init__(self, *args, **kwargs):
        # inherits from InfoScreen
        super().__init__(*args, **kwargs)
        self.header_text = 'Instructions'
        with open(BackupApp.resource_path('instructions.txt'), 'r') as f:
            help_content = f.read()
        self.label_text = help_content
        self.size_hint_label_y = 5

    # header_text = 'Instructions'
    #
    # with open(BackupApp.resource_path('instructions.txt'), 'r') as f:
    #     help_content = f.read()
    # label_text = help_content


class InfoActionScreen(Screen):
    # Use this class and kv equivalent as a template adn parent class
    header_text = StringProperty('')
    label_text = StringProperty('')
    action_text = StringProperty('')


class ClearLogScreen(InfoActionScreen):
    header_text = 'Clear Backup Log'
    label_text = """
    WARNING
    --------
    
    Clicking the button below will delete all entries in the Backup log. 
    
    """
    action_text = 'OK, delete entries'

    def update_label(self, *args):
        self.ids.lbl_action.text = "Backup log cleared"

    def cancel_update_label(self, *args):
        self.lbl_action_update.cancel()

    def action_click(self):
        with open(BackupApp.resource_path('backup_log.txt'), 'w') as f:
            f.write('')
        # only start the clock here, (no need for it on_enter) and stop after 10 secs
        self.lbl_action_update = Clock.schedule_interval(self.update_label, 1 / 100)
        # stop updating label after 10 seconds
        Clock.schedule_once(self.cancel_update_label, 10)


class MyLabel(Label):
    # this Label automatically adjusts font size to fill the Label
    # the refresh method only applies to markup labels
    markup = True

    def on_text(self, instance, new_text):
        self.adjust_font_size()

    def on_size(self, instance, new_size):
        self.adjust_font_size()

    def adjust_font_size(self):
        font_size = self.font_size
        while True:
            # this loops reduces font size if needed
            lbl = MarkupLabel(font_name=self.font_name, font_size=font_size, text=self.text)
            lbl.refresh()
            lbl_available_height = self.height - self.padding_y * 2
            lbl_available_width = self.width - self.padding_x * 2
            if font_size > lbl_available_height:
                font_size = lbl_available_height
            elif lbl.content_width > lbl_available_width or \
                    lbl.content_height > lbl_available_height:
                font_size *= 0.95
            else:
                break
        while True:
            # this loop increases font size if needed
            lbl = MarkupLabel(font_name=self.font_name, font_size=font_size, text=self.text)
            lbl.refresh()
            if lbl.content_width * 1.1 < lbl_available_width and \
                    lbl.content_height * 1.1 < lbl_available_height:
                font_size *= 1.05
            else:
                break

        self.font_size = font_size


class DirLabel(MyLabel):
    pass


class MyButton(Button):
    pass


class RecycleViewButton(MyButton):
    """
    Create a custom button to link to RecycleView function
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    root_widget = ObjectProperty()

    def on_release(self, **kwargs):
        # inherit all the parent's on_release, but then adjust
        super().on_release(**kwargs)
        # refer to function in recycleview
        # we will need to set the root_widget to be the recycleview
        # so that we can access a function in the recycleview
        # this way, we can easily link this all together via the
        # 'root_widget': self statement in the self.data statement
        # of the recycleview
        # the text on the button is the drive that I need
        self.root_widget.goToUpdate(self.text)

class HomeButton(Button):
    def to_home_screen(self):
        app = App.get_running_app()
        sm = app.root.ids.sm
        sm.current = 'welcome_screen'


class ExitButton(Button):
    def close_app(self):
        exit()


class ActionButton(Button):
    pass


class BackupApp(App):
    def build(self):
        self.title = 'Simple Backup Solution'
        return Builder.load_file(self.resource_path('gui.kv'))

    # === Add to create executable with PyInstaller ======
    # we need a function to makes our script look in the correct folder for files
    # when pyinstaller has created the MEIPASS directory then we need to look there
    # so this assumes all our files (.py, .kv, .jpeg, .png, ... everything) is copied
    # into a new folder for pyinstaller to look in
    # in the .spec file we'll then need to to some extra work to make this work
    # if MEIPASS isn't there, then we want the relative path as per the code
    # we do this by creating the absolute path to the current directory, represented by a dot '.'
    # we then need to use this function everywhere we refer to a file, including file references
    # in the kv file. that's why i stuck that function in the App class, so I can refer to it
    # in kv file via app
    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath('.')
        return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    # === Add to create executable with PyInstaller ======
    if hasattr(sys, '_MEIPASS'):
        resource_add_path((os.path.join(sys._MEIPASS)))
    # ==== end ===========================================

    BackupApp().run()
