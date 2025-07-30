import os
from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.String import String
import shutil
from robot.running.context import EXECUTION_CONTEXTS
class ScreenshotListener:
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, screenshot_dir=None):
        self.builtin = BuiltIn()
        self.ScreenshotNumber = 0
        self.testcompleted = False
        self.screenshot_dir=screenshot_dir
        self.rootdir=screenshot_dir
        self.library=''
        self.SeleniumKeywords=['Click Element','click element','Input Text','input text','Press Keys','press keys','Get Text','get text','Get Element Attribute','get element attribute','Page Should Contain','page should contain','Page Should Not Contain','page should not contain','Element Should Be Visible','element should be visible','Element Should Not Be Visible','element should not be visible','Close Browser','Click Button','click button','click link','Click Link']
        self.BrowserKeywords=['Click','click','Fill Text','fill text','Get Text','get text','Get Attribute','get attribute','Wait For Element State','wait for element state']
        self.AppiumKeywords=['Click Element','click element','Input Text','input text','Press Keys','press keys','Get Text','get text','Get Element Attribute','get element attribute','Page Should Contain','page should contain','Page Should Not Contain','page should not contain','Element Should Be Visible','element should be visible','Element Should Not Be Visible','element should not be visible','Close Browser','Click Button','click button','click link','Click Link']
        # Allow user to specify a directory, otherwise use a default
        # self.screenshot_dir = screenshot_dir if screenshot_dir else os.path.join(os.getcwd(), "screenshots")

    def start_test(self, name, attrs):
        """
        Called before a test starts.
        Creates a directory for screenshots if it doesn't exist.
        """
        isPathcreated=os.path.exists(self.rootdir)
        if isPathcreated==False:
            os.makedirs(self.rootdir, exist_ok=True)
        # Create a directory for screenshots if it doesn't exist
        test = BuiltIn().get_variable_value('${TEST NAME}', 'NoTestName')
        if test != 'NoTestName':
            subfolder_path = os.path.join(self.rootdir, test)
            os.makedirs(subfolder_path, exist_ok=True)
            # os.makedirs(self.screenshot_dir+'\/'+test, exist_ok=True)
        self.screenshot_dir=subfolder_path
        try:
                selenium = BuiltIn().get_library_instance('SeleniumLibrary')
                self.library = 'SeleniumLibrary'
                # return 'SeleniumLibrary'
        except RuntimeError:
            pass
        try:
            Browser = BuiltIn().get_library_instance('Browser')
            self.library = 'Browser'
            # return 'Browser'
        except RuntimeError:
            pass
        try:
            Appium = BuiltIn().get_library_instance('AppiumLibrary')
            self.library = 'AppiumLibrary'
            # return 'AppiumLibrary'
        except RuntimeError:
            pass
        print(self.library)
        print(f"ScreenshotListener initialized with {self.library}. Screenshots will be saved to: {self.screenshot_dir}")
        
    def start_keyword(self, name, attributes):
        """
        Called before a keyword starts.
        Takes a screenshot and logs its path.
        """
        
        try:
            # Get the current test name to help organize screenshots
            test_name = BuiltIn().get_variable_value("${TEST NAME}", "NoTestName")
            keyword_name=str(name).split('.') # Replace spaces and dots
            kwname = keyword_name[1].replace('_',' ')
            test=BuiltIn().get_variable_value('${TEST NAME}')
            if self.library == 'SeleniumLibrary':
                if kwname in self.SeleniumKeywords and 'Open Browser' not in kwname and self.testcompleted is False and 'Close Browser' not in kwname:   
                    screenshot_name = f"selenium_{self.ScreenshotNumber}.png"
                    screenshot_path=BuiltIn().run_keyword("SeleniumLibrary.Capture Page Screenshot",screenshot_name)
                    filename=os.path.basename(screenshot_path)
                    shutil.move(screenshot_path,self.rootdir+'/'+test+'/'+filename)
                    self.ScreenshotNumber += 1
                if 'Close Browser' in kwname:
                    screenshot_name = f"selenium_{self.ScreenshotNumber}.png"
                    screenshot_path=BuiltIn().run_keyword("SeleniumLibrary.Capture Page Screenshot",screenshot_name)
                    filename=os.path.basename(screenshot_path)
                    shutil.move(screenshot_path,self.rootdir+'/'+test+'/'+filename)
                    # screenshot_path=BuiltIn().run_keyword("SeleniumLibrary.Capture Page Screenshot",self.rootdir+'/'+test+'/'+screenshot_name)
                    self.ScreenshotNumber += 1
            elif self.library == 'Browser':
                if kwname in self.BrowserKeywords and 'New Browser' not in kwname and self.testcompleted is False and 'Close Browser' not in kwname:   
                    screenshot_name = f"browser_{self.ScreenshotNumber}.png"
                    screenshot_path=BuiltIn().run_keyword("Browser.Take Screenshot",screenshot_name)
                    filename=os.path.basename(screenshot_path)
                    shutil.move(screenshot_path,self.rootdir+'/'+test+'/'+filename)
                    self.ScreenshotNumber += 1
                if 'Close Browser' in kwname:
                    screenshot_name = f"browser_{self.ScreenshotNumber}.png"
                    screenshot_path=BuiltIn().run_keyword("Browser.Take Screenshot",screenshot_name)
                    filename=os.path.basename(screenshot_path)
                    shutil.move(screenshot_path,self.rootdir+'/'+test+'/'+filename)
                    # screenshot_path=BuiltIn().run_keyword("SeleniumLibrary.Capture Page Screenshot",self.rootdir+'/'+test+'/'+screenshot_name)
                    self.ScreenshotNumber += 1
            elif self.library == 'AppiumLibrary':
                if kwname in self.AppiumKeywords and 'Open Application' not in kwname and self.testcompleted is False and 'Close Application' not in kwname:   
                    screenshot_name = f"appium_{self.ScreenshotNumber}.png"
                    screenshot_path=BuiltIn().run_keyword("AppiumLibrary.Capture Page Screenshot",screenshot_name)
                    filename=os.path.basename(screenshot_path)
                    shutil.move(screenshot_path,self.rootdir+'/'+test+'/'+filename)
                    self.ScreenshotNumber += 1
                if 'Close Browser' in kwname:
                    screenshot_name = f"appium_{self.ScreenshotNumber}.png"
                    screenshot_path=BuiltIn().run_keyword("AppiumLibrary.Capture Page Screenshot",screenshot_name)
                    filename=os.path.basename(screenshot_path)
                    shutil.move(screenshot_path,self.rootdir+'/'+test+'/'+filename)
                    # screenshot_path=BuiltIn().run_keyword("SeleniumLibrary.Capture Page Screenshot",self.rootdir+'/'+test+'/'+screenshot_name)
                    self.ScreenshotNumber += 1
                

        except Exception as e:
            pass 

    def end_keyword(self, name, attributes):
        """
        Called after a keyword ends.
        Logs the end of the keyword execution.
        """
        try:
            keyword_name=str(name).split('.') # Replace spaces and dots
            kwname = keyword_name[1].replace('_',' ')
            if 'Close Browser' in kwname or 'Close Application' in kwname or 'close application' in kwname:
                self.ScreenshotNumber=0
        except Exception as e:
            pass