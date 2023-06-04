class CommandObjects:
    class BaseCommand:
        """
        All commands should extend this class
        """
        commandType:str = None # The name of the command
        originalLine:str = None # The line the command came from
        originalLineNumber:int = None # The line number the command came from
        pathToCommand:list = None # A path of keys to get to the this command
        
        def __init__(self, commandType:str, pathToCommand:list, originalLine:str, originalLineNumber:int) -> None:
            """
            Args:
                commandType (str): The name of the command
                pathToCommand (list): A path of keys to get to the this command
                originalLine (str): The line the command came from
                originalLineNumber (int): The line number the command came from
            """
            self.commandType = commandType
            self.pathToCommand = pathToCommand
            self.originalLine = originalLine
            self.originalLineNumber = originalLineNumber
        
        def get_type(self) -> None:
            return self.commandType
        
        def get_original_line(self) -> None:
            return self.originalLine
        
        def get_original_line_number(self) -> None:
            return self.originalLineNumber
        
        def get_path_to_command(self) -> None:
            return self.pathToCommand
        
        def set_updated_path(self, path:list) -> None:
            self.pathToCommand = path
            
        def reformat(self, code:list) -> list:
            """
            Reformats the command and the lines around it\n
            to prepare the code for the assembly processes.\n
            
            Args:
                All the code that is being compiled
            Returns:
            
                All the code with updates
            """
            return code
        
        def follow_path(self, path:list) -> object:
            """
            This gets what is at the end of a path inside this command.

            Args:
                path (list): a list of keys to follow

            Returns:
                The data at the end of the command
            """
            return None

        @staticmethod
        def check_if_command_is_this(self, code:list, pathToCommand:list) -> bool:
            """
            Use this to check if a path points to this type of command.\n
            A sting that has this command in it does not count if \n
            the command is not at start the of the string.\n
            Returns:
                Bool
            """
            return False
        
    class template(BaseCommand):
        """
        This is the template command.\n
        Copy this to make your own commands.
        """
        def __init__(self, code:list, pathToCommand:list, originalLine:str, originalLineNumber:int) -> None:
            """
            Args:
                code (list): All the code that is being compiled
                pathToCommand (list): A path of keys to get to the this command
                originalLine (str): The line the command came from
                originalLineNumber (int): The line number the command came from
            """
            super().__init__(code, 'template', pathToCommand, originalLine, originalLineNumber)
        
        @staticmethod
        def check_if_command_is_this(self, code:list, pathToCommand:list) -> list: # fill this in
            return False
        
        def reformat(code:list) -> list: # fill this in if needed
            return code
        
        def follow_path(self, path:list) -> object: # fill this in
            # if it cant follow the path raise an exception
            return None