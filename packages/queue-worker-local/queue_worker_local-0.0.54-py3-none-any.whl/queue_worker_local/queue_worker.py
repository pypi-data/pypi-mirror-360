import argparse
import json
import multiprocessing
import os
import random
import subprocess
import sys
import time
from io import StringIO
from functools import lru_cache

from python_sdk_local.utilities import get_ip_v4, get_ip_v6
from database_infrastructure_local.number_generator import NumberGenerator
from database_mysql_local.utils import get_table_columns
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.MetaLogger import MetaLogger
from logger_local.MetaLogger import Logger
from queue_local.database_queue import DatabaseQueue
from user_context_remote.user_context import UserContext

QUEUE_WORKER_COMPONENT_ID = 159
QUEUE_WORKER_COMPONENT_NAME = 'queue_worker_local_python_package/src/queue_worker.py'
DEVELOPER_EMAIL = 'akiva.s@circ.zone'
logger_object = {'component_id': QUEUE_WORKER_COMPONENT_ID,
                 'component_name': QUEUE_WORKER_COMPONENT_NAME,
                 'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
                 'developer_email': DEVELOPER_EMAIL}

SESSION_LENGTH = 32
DELIMITER = "returned_value: "
SUCCESS_RETURN_CODE = 0
ERROR_RETURN_CODE = -1
installed = []  # to avoid installing the same package multiple times


class QueueWorker(DatabaseQueue, metaclass=MetaLogger, object=logger_object):
    """A queue worker that executes tasks from the queue.
    If the given table does not have the required columns, the results will be saved in the logger instead.
    """

    def __init__(self, schema_name: str = "queue", table_name: str = "queue_item_table",
                 view_name: str = "queue_item_view", queue_item_id_column_name: str = "queue_item_id",
                 action_boolean_column: str = "is_queue_action", is_test_data: bool = False) -> None:
        super().__init__(schema_name=schema_name, table_name=table_name, view_name=view_name,
                         queue_item_id_column_name=queue_item_id_column_name, is_test_data=is_test_data)
        self.queue_item_id_column_name = queue_item_id_column_name
        self.all_actions = self.get_all_actions(action_boolean_column)
        self.user = UserContext()
        self.logger = Logger.create_logger(object=logger_object)
        self.save_in_logger = not self._table_has_required_columns(
            table_name=table_name)

    def _get_action_ids(self, action_names: tuple) -> tuple:
        """Get the action IDs from the action names."""
        if not action_names:
            action_ids = ()
        else:
            action_ids = tuple(
                action["action_id"] for action in self.all_actions if action["action_name"] in action_names)
        return action_ids

    def execute(self, action_ids: tuple = (), action_names: tuple = (),
                min_delay_after_execution_ms: float = 0.0,
                max_delay_after_execution_ms: float = 0.0,
                total_missions: int = 1,
                raise_on_error: bool = True,
                push_back_on_error: bool = False,  # is_try_to_resend_on_error (dangerous if will fail again)
                install_packages: bool = True,
                working_directory: str | None = None,
                execution_details: dict = None,
                custom_condition: str = ""
                ) -> bool:
        """Execute tasks from the queue.

        If execution_details is provided, the queue will not be used.
        If provided, execution_details must contain the following columns:
            `column_name`, action_id, function_parameters_json, class_parameters_json"""  # noqa: E501
        self.logger.start(
            f"Executing actions: {action_ids} with action_names: {action_names}, "
            f"total_missions: {total_missions}, raise_on_error: {raise_on_error}, "  # noqa: E501
        )

        if execution_details:
            required_columns = (self.queue_item_id_column_name,
                                "action_id",
                                "function_parameters_json",
                                "class_parameters_json")
            for column in required_columns:
                if column not in execution_details:
                    raise ValueError(f"Missing column {column} in execution_details.\n"  # noqa: E501
                                     f"Required columns: {required_columns}")
        action_ids += self._get_action_ids(action_names)
        if install_packages:
            self._install_packages(action_ids)
        max_delay_after_execution_ms = max(
            max_delay_after_execution_ms,
            min_delay_after_execution_ms)
        successed = True
        last_user_jwt = None
        for mission in range(1, total_missions + 1):
            self.logger.info(f"Mission {mission}/{total_missions}")
            if execution_details:
                queue_item_dict = execution_details
            else:
                queue_item_dict = self.get(
                    action_ids=action_ids, custom_condition=custom_condition)
            if not queue_item_dict:
                self.logger.info(
                    f'The queue does not have more items of action_ids {action_ids}')
                break

            function_parameters = json.loads(
                queue_item_dict["function_parameters_json"] or "{}")
            # class_parameters created-by for example send_schedule()
            class_parameters = json.loads(
                queue_item_dict["class_parameters_json"] or "{}")
            formatted_function_params = ', '.join(
                [f'{key}={repr(value)}' for key, value in function_parameters.items()])

            action = self.get_action(queue_item_dict)
            if working_directory:
                action["folder_name"] = os.path.basename(working_directory)
            filename = action["filename"]
            function_name = action["function_name"]

            if filename.endswith('.py'):
                args = self._get_python_args(
                    action, class_parameters, function_parameters)
            # elif...
            else:
                error_message = f"Unsupported file extension {filename} for action {queue_item_dict['action_id']}"
                raise Exception(error_message)

            current_thread_id = get_thread_id()
            self.logger.info(f"Executing action_id: {queue_item_dict['action_id']}, pid: {os.getpid()}, "
                             f"thread_id: {current_thread_id}, shell script:\n{' '.join(args)}")
            if last_user_jwt != queue_item_dict.get("user_jwt"):
                self.user.login_using_user_jwt(queue_item_dict["user_jwt"])
                last_user_jwt = queue_item_dict["user_jwt"]

            stdout = stderr = returncode = None
            if filename.endswith('.py'):
                try:
                    # we prefer using exec as it is faster
                    stdout, stderr, returncode = self.execute_python_script(
                        args)
                except ModuleNotFoundError:
                    self.logger.warning(f"Failed to execute {function_name}({formatted_function_params}) with exec()"
                                        f" retrying using subprocess.run()")

            if returncode is None:  # retry or not python
                result = subprocess.run(args, capture_output=True,  # stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        text=True, cwd=working_directory)
                returncode = result.returncode
                stdout = result.stdout
                stderr = result.stderr

            self.logger.info(f"Executed action_id: {queue_item_dict['action_id']}, pid: {os.getpid()},"
                             f"thread_id: {current_thread_id}, return code: {returncode}")

            self.logger.info(
                f"stdout: {stdout}\nstderr: {stderr}\nreturn code: {returncode}")

            save_result = self.save_execution_result(
                queue_item_dict, stdout, stderr, returncode)

            if save_result is not None and save_result == 0:
                self.logger.warning(
                    f"Failed to save execution result for action_id: {queue_item_dict['action_id']}, "
                    f"stdout: {stdout}, stderr: {stderr}, return_code: {returncode}"
                )

            if returncode == SUCCESS_RETURN_CODE:
                self.logger.info(
                    f'Successfully executed {function_name}({formatted_function_params})')
            else:
                error_message = f'Error while executing {function_name}({formatted_function_params}):\n{stderr}\n'
                if push_back_on_error:
                    self.push_back(queue_item_dict)
                successed = False
                if raise_on_error:
                    raise Exception(error_message)

            sleep_time = random.uniform(
                min_delay_after_execution_ms / 1000, max_delay_after_execution_ms / 1000)
            if sleep_time > 0 and mission != total_missions:
                self.logger.info(f'Sleeping for {sleep_time} seconds')
                time.sleep(sleep_time)

        self.logger.end(
            f"Finished executing actions: {action_ids} with action_names: {action_names}, "
            f"total_missions: {total_missions}, raise_on_error: {raise_on_error}, "
            f"successed: {successed}, push_back_on_error: {push_back_on_error}, "
        )
        return successed

    def execute_python_script(self, args: list) -> tuple:
        # Save the original stdout and stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        # Create file-like objects to capture output
        stdout_capture = sys.stdout = StringIO()
        stderr_capture = sys.stderr = StringIO()
        try:
            # We are using our scripts, so it is safe to execute them
            exec(args[-1])
            returncode = SUCCESS_RETURN_CODE
        except ModuleNotFoundError as e:
            raise e  # we want to retry using subprocess.run()
        except Exception as e:
            self.logger.exception(
                "An error occurred during execution:", object=e)
            returncode = ERROR_RETURN_CODE
        finally:
            # Restore the original stdout and stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        # Get the captured output
        stdout = stdout_capture.getvalue()
        stderr = stderr_capture.getvalue()
        return stdout, stderr, returncode

    def save_execution_result(self, queue_item_dict: dict, stdout: str, stderr: str, returncode: int):
        """Save the execution result in the database or in the logger."""
        queue_item_id = queue_item_dict[self.queue_item_id_column_name]
        component_id = queue_item_dict.get("component_id")
        if DELIMITER in stdout:
            stdout, returned_value = stdout.split(DELIMITER)
        else:
            returned_value = None
        return_message = "Success" if returncode == SUCCESS_RETURN_CODE else "Error"

        server_ip_v4 = get_ip_v4()
        server_ip_v6 = get_ip_v6()
        thread_id = get_thread_id()

        queue_dict = {"stdout": stdout, "stderr": stderr, "return_code": returncode,
                      "return_message": return_message, "returned_value": returned_value,
                      "server_ip_v4": server_ip_v4, "server_ip_v6": server_ip_v6, "thread_id": thread_id}
        self.logger.info(
            f"Saving execution result for queue_item_id: {queue_item_id}, "
            f"stdout: {stdout}, stderr: {stderr}, return_code: {returncode}, "
            f"return_message: {return_message}, returned_value: {returned_value}, "
            f"server_ip_v4: {server_ip_v4}, server_ip_v6: {server_ip_v6}, thread_id: {thread_id}")

        insert_id = None
        updated_rows = None
        if self.save_in_logger:  # TODO: test
            # TODO: save in another dedicated table, as the logger table is too big and it takes time to search.
            # We save in queue_item_dict to return it to the caller
            queue_dict["session"] = queue_item_dict["session"] = QueueWorker._generate_session()
            queue_dict["component_id"] = component_id
            insert_id = super().insert(schema_name="logger",
                                       table_name="logger_table", data_dict=queue_dict)
            return insert_id
        else:
            updated_rows = super().update_by_column_and_value(
                column_value=queue_item_id, data_dict=queue_dict)
            return updated_rows

    @staticmethod
    # TODO Is it running as soon as we run any code? - It should be between the 1st things we run in any use case. Answer: It's a slow function. Running only if there's a session column.  # noqa
    def _generate_session(length: int = SESSION_LENGTH) -> str:
        # TODO session is alpha numeric, shall we have this generic function in python-sdk? I mean general location such as python-sdk? Is it the same for all entities?  # noqa
        session = NumberGenerator.get_random_identifier(
            schema_name="logger", view_name="logger_view",
            identifier_column_name="session", length=length)
        return session

    @staticmethod
    def _get_python_args(action: dict, class_parameters: dict, function_parameters: dict) -> list:
        """Get the arguments for the python command line."""
        class_parameters = class_parameters or {}  # in case it is None
        function_parameters = function_parameters or {}
        function_name = action["function_name"]
        filename = action["filename"].replace(".py", "")
        folder = (action["folder_name"] + ".") if action["folder_name"] else ""

        function_module = action["function_module"]

        if function_module:
            function_call = f"{function_module}(**{class_parameters}).{function_name}(**{function_parameters})"
        else:
            function_call = f"{function_name}(**{function_parameters})"
        command = f'from {folder}{filename} import {function_module or function_name}\n' + \
            f'result = {function_call}\n' + \
            f'print("{DELIMITER}" + ' + ' str(result or {}), end="")'
        python_args = [sys.executable, '-c', command]
        return python_args

    def get_action(self, queue_item: dict) -> dict:
        """Get the action from the database."""
        try:
            action = next(
                action for action in self.all_actions if action['action_id'] == queue_item['action_id'])
            return action
        except StopIteration:
            raise ValueError(f"No such action_id {queue_item['action_id']}")

    @lru_cache
    def get_all_actions(self, action_boolean_column: str = "is_queue_action") -> list:
        """Get all actions from the database."""
        all_actions = self.select_multi_dict_by_column_and_value(
            schema_name="action", view_table_name="action_view",
            column_name=action_boolean_column, column_value=True)
        return all_actions

    def _install_packages(self, action_ids: tuple) -> None:

        for action in self.all_actions:
            if action["action_id"] not in action_ids or action["package_name"] in installed:
                continue
            filename = action["filename"]
            package_name = action["package_name"]

            if not filename or not package_name:
                continue
            if filename.endswith('.py'):
                try:
                    # hide the output
                    subprocess.check_call(
                        ["pip", "install", "-U", package_name], stdout=subprocess.DEVNULL)
                except subprocess.CalledProcessError as e:
                    self.logger.exception(
                        f"Failed to install {package_name}", object=e)
                    continue
            elif filename.endswith(".ts"):
                subprocess.check_call(["npm", "install", package_name])
                subprocess.check_call(["npm", "update", package_name])
            # elif...
            installed.append(action["package_name"])

    @staticmethod
    # TODO Maybe performance issue, cal we use the table definition generated by Sql2Code?
    def _table_has_required_columns(table_name: str) -> bool:
        required_columns = ("stdout", "stderr", "return_code", "return_message", "returned_value",
                            "server_ip_v4", "server_ip_v6", "thread_id")
        columns = get_table_columns(table_name)
        has_required_columns = all(
            column in columns for column in required_columns)
        return has_required_columns


def execute_queue_worker(action_ids: tuple, action_names: tuple, min_delay_after_execution_ms: float,
                         max_delay_after_execution_ms: float, total_missions: int, is_test_data: bool = False):
    # cannot share it between processes
    queue_worker = QueueWorker(is_test_data=is_test_data)
    queue_worker.execute(action_ids, action_names, min_delay_after_execution_ms,
                         max_delay_after_execution_ms, total_missions)


def get_thread_id():
    """Returns the current thread ID"""
    thread_id = multiprocessing.current_process().ident
    return thread_id


def main():
    """See README.md"""
    parser = argparse.ArgumentParser(description='Queue Worker')

    parser.add_argument('-min_delay_after_execution_ms',
                        type=float, default=0.0)
    parser.add_argument('-max_delay_after_execution_ms',
                        type=float, default=0.0)
    parser.add_argument('-action_ids', type=int, nargs='+',
                        help='List of action IDs', default=())
    parser.add_argument('-action_names', type=str, nargs='+',
                        help='Action names in addition to the action IDs', default=())
    parser.add_argument('-total_missions', type=int, default=1,
                        help='Number of missions to execute')
    parser.add_argument('-raise_on_error', type=bool, default=True,
                        help='Whether to raise an exception on error')
    parser.add_argument('-push_back_on_error', type=bool, default=False,
                        help='Whether to push back the item to the queue when an error occurs')
    parser.add_argument('-processes', type=int, default=1,
                        help='Number of processes to start')
    parser.add_argument('-install_packages', type=bool,
                        default=True, help='Whether to install packages')
    parser.add_argument('-working_directory', type=str, default=os.path.dirname(os.path.abspath(__file__)),
                        help='The working directory of the queue worker')
    parser.add_argument('-is_test_data', type=bool,
                        default=False, help='Whether to use test data')

    args = parser.parse_args()
    if not args.action_ids and not args.action_names:
        print("At least one of the following arguments must be provided: -action_ids, -action_names")
        return
    if any(x is None for x in vars(args).values()):
        print(f"Usage: python {__file__} -min_delay_after_execution_ms 0 -max_delay_after_execution_ms 1 "
              f"-action_ids 1 2 4 -total_missions 100 -processes 1")
        return

    processes = []
    try:
        for _ in range(args.processes):
            # TODO: can we send by name?
            worker_args = (tuple(args.action_ids), tuple(args.action_names), args.min_delay_after_execution_ms,
                           args.max_delay_after_execution_ms, args.total_missions // args.processes, args.is_test_data)
            process = multiprocessing.Process(
                target=execute_queue_worker, args=worker_args)
            processes.append(process)

        # Start the processes
        for process in processes:
            process.start()

        # Wait for all processes to complete
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        print("KeyboardInterrupt received, terminating processes...")
        for process in processes:
            process.terminate()
        print("Processes terminated.")
    except Exception as e:
        print(f"An error occurred: {e}")
        for process in processes:
            process.terminate()
        print("Processes terminated due to error.")
        raise e
    finally:
        for process in processes:
            if process.is_alive():
                process.join()
        print("All processes have completed.")
        print("Queue worker finished execution.")


if __name__ == "__main__":
    main()
