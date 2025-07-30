import os

class info:
    '''
    The `info` class allows navigating and just accessing text files organized into "info" directory.
    
    This directory contains documents to help with data analysis and ML modeling. It also has custom
    functions, i.e., functions that have a body of code that varies depending on the problem being 
    worked on.

    This class creates a structure of attributes based on directories and files found inside 
    the `texts` folder (or another specified one). Each subdirectory is represented as an attribute 
    containing another instance of `info`, enabling hierarchical navigation.

    Text files can be accessed directly as instance attributes.

    Parameters:
    -----------
    folder : str, optional
        The base directory path containing the text files and subdirectories.
        If not specified, it defaults to the `texts` directory located in the same folder as the module.
    level : int, optional
        The hierarchical level of the instance, used for indentation when listing contents.

    Methods:
    --------
    __getattr__(name)
        Returns the content of the text file `name.txt` inside the instance's directory.
    
    ls()
        Lists the available files and subdirectories in the instance without creating dynamic attributes.
    
    Usage Example:
    ---------------
    Suppose the directory structure is:

    ```
    texts/
    ├── general.txt
    ├── python/
    │   ├── syntax.txt
    │   ├── modules.txt
    ├── data/
        ├── pandas.txt
    ```

    ```python
    info_obj = info()   # Initializes in the 'texts' directory
    print(info_obj.general)  # Returns the content of 'general.txt'
    
    info_obj.python.ls()  # Lists the files inside 'python/'
    print(info_obj.python.syntax)  # Returns the content of 'syntax.txt'
    ```

    Exceptions:
    -----------
    - `AttributeError`: If the user tries to access a non-existent file in the current directory.
    '''

    def __init__(self, folder=None, level=0):
        if folder is None:
            self.folder = os.path.join(os.path.dirname(__file__), "texts")
        else:
            self.folder = folder

        self.level = level

        #List the dir/files in directory
        self._list_dir_content()

    def _list_dir_content(self, just_consult=False):
        #List the dir/files in directory
        if not os.path.exists(self.folder):
            print(f"The file '{self.folder}' was not found.")
            return

        contents = [f for f in os.listdir(self.folder)]

        prefix = '     '*self.level
        prefix = prefix[:-5] + ' └───' if self.level != 0 else prefix

        if contents:
            if (self.level == 0): print('MAIN DIRECTORY NOTES FOR PROGRAMMING HELP:')
            for content in contents:

                relative_path = os.path.join(self.folder, content)
                # path = os.path.join(os.getcwd(), relative_path)

                if os.path.isdir(relative_path):
                    print(prefix + f'📁 {content}' )
                    #if "content" is a folder, define a new attribute for "self" as an new instance of class "info"
                    if not just_consult:
                        setattr(self, content, info( folder=relative_path, level = self.level+1 ))
                else:
                    print(prefix + f'📄 {content}')
        else:
            print(prefix + ' (empty)')

    def __getattr__(self, name):
        file_path = os.path.join(self.folder, f"{name}.txt")
        
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        
        raise AttributeError(f"❌ The text '{name}' was not found in '{self.folder}'.")

    def ls(self):
        #Call of method "_list_dir_content" without the "setattr()" command -> just_consult=True
        self._list_dir_content( just_consult=True )