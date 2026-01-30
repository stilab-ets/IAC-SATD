import json
import os
import subprocess
from pydriller import ModifiedFile
#from tmp_file_code import tmp,terrametrics


class TerraMetricsLoader:
    """
    Loads and analyzes Terraform metrics using an external Java service.

    Attributes:
        mod (ModifiedFile): A PyDriller ModifiedFile object representing the file to analyze.
        positions (dict): A dictionary to store positions of code blocks or metrics.
        resourceFolder (str): The directory where temporary and result files are stored.
        target (str): The path to the output JSON file containing the analysis results.
        service_locator_jar_path (str): The path to the Java JAR file that performs the analysis.
        tmp_blob_path_before_change (str): The path to a temporary file containing the code before changes.
        tmp_blob_path_after_change (str): The path to a temporary file containing the code after changes.
    """

    # def __init__(self, mod: ModifiedFile, pathToLocalEmp=None):
    def __init__(self, pathToLocalEmp=None):
        """
        Initializes the TerraMetricsLoader with a modified file.

        Args: mod (ModifiedFile): The modified file to be analyzed.
        """
        #print(pathToLocalEmp)
        self.positions = {}
        self.resourceFolder = "./"
        self.target = self.resourceFolder + "terrametrics_results.json"
        self.service_locator_jar_path = self.resourceFolder + "/terrametrics_2.0.2.jar"
        self.pathToLocalEmp = pathToLocalEmp
        #self.modelName = modelName
        #self.commit_hash = commit_hash

    def call_service_locator(self):
        """
        Invokes the Java service to analyze the Terraform metrics and captures the output.

        Args:
            before (bool): Flag indicating whether to analyze the content before the change.

        Returns:
            The results from the Java service as a dictionary, or None if an error occurs.
        """
        if self.pathToLocalEmp is None:
            return None

        command, args = self.prepareCommand()

        try:
            res = subprocess.run(command, capture_output=True, text=True, check=True)
            results = self.getJsonObjects(args["target"])
            #self.clean_file(self.target)
            #print(results)
            return results
        except subprocess.CalledProcessError as e:
            error_message = f"Error occurred: {e.stderr}"
            #print(error_message)
            #self.save_error_log(error_message, before, self.modelName)
            return None

    def clean_file(self, file_path: str):
        """
        Clears the content of a specified file.

        Args:
            file_path (str): The path to the file to be cleared.
        """
        with open(file_path, 'w') as file:
            file.truncate(0)

    def getJsonObjects(self, path: str):
        """
        Reads and parses JSON data from a specified file path.

        Args:
            path (str): The path to the JSON file to be read.

        Returns:
            A dictionary containing the parsed JSON data, or None if a decoding error occurs.
        """
        try:
            with open(path, 'r') as file:
                self.positions = json.load(file)
            return self.positions
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
            return None

    def prepareCommand(self):
        """
        Prepares the command to invoke the Java service with the necessary arguments.

        Args:
            before (bool): Flag indicating whether to analyze the content before the change.

        Returns:
            A tuple containing the command list to be executed and the arguments dictionary.
        """

        args = { "file": self.pathToLocalEmp, "target": self.target}

        command = ['java', '-jar', self.service_locator_jar_path]

        for arg, value in args.items():
            command.append(f"--{arg}")
            command.append(value)

        # Include block positions in the analysis
        command.append("-b")

        return command, args

"""
if __name__ == "__main__":
    terrametrics_instance = TerraMetricsLoader(pathToLocalEmp="./tmp.tf")
    terrametrics_instance.call_service_locator() """

