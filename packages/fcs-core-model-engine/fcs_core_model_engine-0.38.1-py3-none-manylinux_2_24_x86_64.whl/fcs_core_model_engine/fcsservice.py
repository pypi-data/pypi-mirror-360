
import inspect

from .fcscore import Model
from .geometrybuilder import GeometryBuilder
from .fcslogger import FCSLogger
from .fcsmodelsession import CloudModelCommunicatorBase


# Custom decorator to mark methods as callbacks
def fcs_command(func):
    """
    Decorator to mark a method as a callback.
    """
    func.is_callback = True
    return func

class BackendService(object):
    """
    Template class for hosting specific plugins.
    """

    def __init__(self, user_id: str, model_id: str, service_name: str):
        """
        Constructor.
        """
        self.user_id = user_id
        self.model_id = model_id
        self.service_name = service_name
        self.cloud_model_communicator: CloudModelCommunicatorBase = None
        self.model_builder: Model = None
        self.geometry_builder: GeometryBuilder = None
        self.logger: FCSLogger = None

    def set_existing_services(self, 
                              cloud_model_communicator: CloudModelCommunicatorBase,
                              logger: FCSLogger
                              ) -> None: 
        """
        Set existing services for the backend.
        """
        self.cloud_model_communicator = cloud_model_communicator
        self.model_builder = self.cloud_model_communicator.model_builder
        self.geometry_builder = self.cloud_model_communicator.geometry_builder
        self.logger = logger

    def run_on_startup(self) -> None:
        """
        When the frontend application has finished initializing, this method is called
        to run on startup.
        """
        pass

    def run_on_shutdown(self) -> None:
        """
        When the container was triggered to be closed, then this method is called
        to run a shutdown sequence on the existing data, if needed.
        """
        pass

    def run_command(self, command_name: str, command_args: dict = {}) -> dict | None:
        """
        Execute a command by name with arguments.
        """
        self.logger.set_logging_context(self.service_name)
        result = None

        if command_name not in self.get_available_callbacks():
            self.logger.wrn(f'Request a command name that was not made available: {command_name}.')
            return {'Error': f'Command name unavailable {command_name}'}

        try:
            command_ptr = getattr(self, command_name)
            result = command_ptr(command_args)
        except AttributeError as ex_atrr:
            self.logger.err(f'Probably could not find {command_name}! (Exception: {ex_atrr.args})')
        except Exception as ex:
            self.logger.err(f'Running command {command_name} failed: {ex.args}!')
        finally:
            self.logger.set_logging_context('')

        return result

    def get_available_callbacks(self) -> list:
        """
        Retrieve list of available callback methods.
        """
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        available_callbacks = [name for name, method in methods if hasattr(method, 'is_callback')]
        return available_callbacks