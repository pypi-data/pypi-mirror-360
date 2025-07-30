from . import Logger
from Omnicon_GenericDDSEngine_Py import Omnicon_GenericDDSEngine_Py as Omnicon


class OmniconEngineHandler:
    def __init__(self, input_files_and_dirs_list: list, is_parse_ROS2_constants: bool, license_file_path: str):

        self.logger = Logger.add_logger(__name__)
        self.engine = None
        self.init_and_run_engine(input_files_and_dirs_list, is_parse_ROS2_constants, license_file_path)

    @staticmethod
    def set_engines_factory_verbosity( logging_verbosity: str):
        verbosity = OmniconEngineHandler.get_engine_log_level(logging_verbosity)

        factory_configuration = Omnicon.FactoryConfiguration()
        factory_configuration.loggerConfiguration.verbosity = verbosity
        Omnicon.GenericDDSEngine.SetFactoryConfiguration(factory_configuration)

    @staticmethod
    def get_engine_log_level( logging_verbosity: str):
        logging_verbosity = logging_verbosity.lower()
        verbosity_dict = {
            "fatal": Omnicon.LogSeverityLevel.fatal,
            "error": Omnicon.LogSeverityLevel.error,
            "warning": Omnicon.LogSeverityLevel.warning,
            "info": Omnicon.LogSeverityLevel.info,
            "debug": Omnicon.LogSeverityLevel.debug,
            "trace": Omnicon.LogSeverityLevel.trace
            }
        if logging_verbosity not in verbosity_dict.keys():
            raise Exception(f"Logging verbosity '{logging_verbosity}' is invalid. "
                            f"Please use 'FATAL'/ 'ERROR'/ 'WARNING'/ 'INFO' or 'DEBUG'")
        return verbosity_dict[logging_verbosity]

    def init_and_run_engine(self, input_files_and_dirs_list: list,
                            is_parse_ROS2_constants: bool, license_file_path: str) -> Omnicon.GenericDDSEngine:
        """
        This creates an engine instance and performs init and run with the desired configurations.
        :param input_files_and_dirs_list: A string that holds the path of the folder that holds the input_pointer files
        """
        # Create an engine instance:
        self.engine = Omnicon.GenericDDSEngine()


        # Create an engine configuration object:
        engine_configuration = Omnicon.EngineConfiguration()
        if bool(license_file_path):
            self.logger.info("Using specified file path")
            engine_configuration.licenseFilePath = license_file_path
        # Set the parameters:
        engine_configuration.threadPoolSize = 3
        # Go over the new list and append it into the configuration file path vector:
        for input_file in input_files_and_dirs_list:
            engine_configuration.ddsConfigurationFilesPath.append(input_file)
        # Perform the introspection:
        engine_configuration.engineOperationMode = \
            Omnicon.EngineOperationMode.TYPE_INTROSPECTION
        engine_configuration.parseROS2Constants = is_parse_ROS2_constants
        # init the engine:
        self.logger.debug("init engine...")

        self.engine.Init(engine_configuration)
        self.logger.info("Engine was init successfully")
        # Run the engine:
        self.engine.Run()
        # When Init() went well, make a log entry:
        self.logger.debug("Engine is now up and running")
        self.check_license_validity()

    def check_license_validity(self):
        prefix = "Omnicon.DDSDocGen"
        version = "_v3.2.2"

        license_info = self.engine.LicenseInfo()
        customer_data = license_info.customer

        # Check if the string starts with the required prefix
        if not customer_data.startswith(prefix) or not customer_data.endswith(version):
            raise Exception("Error LoadAndVerifyLicense. The license file is not compatible with the current version.\n"
                            "Please contact Omnicon for assistance.")


    def shutdown_engine(self):
        try:
            self.logger.debug("Shutting down Omnicon engine")
            if self.engine:
                self.engine.Shutdown()
                del self.engine
                self.engine = None
            self.logger.debug("Engine shutdown is complete")
        except Exception as error:
            self.logger.error("shutdown_introspection_engine exception occurred:", error)
