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
        self.SeleniumKeywords=['Click Element','click element','Input Text','input text','Press Keys','press keys','Get Text','get text','Get Element Attribute','get element attribute','Page Should Contain','page should contain','Page Should Not Contain','page should not contain','Element Should Be Visible','element should be visible','Element Should Not Be Visible','element should not be visible','Close Browser','Click Button','click button','click link','Click Link']
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
        print(f"ScreenshotListener initialized. Screenshots will be saved to: {self.screenshot_dir}")
        
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
            
            if kwname in self.SeleniumKeywords and 'Open Browser' not in kwname and self.testcompleted is False and 'Close Browser' not in kwname:   
                screenshot_name = f"selenium_{self.ScreenshotNumber}.png"
                # screenshot_path = os.path.join(self.screenshot_dir, screenshot_name)
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
            if 'Close Browser' in kwname:
                self.ScreenshotNumber=0
        except Exception as e:
            pass
            
        
