import threading
import ast
import logging
from robot.libraries.BuiltIn import BuiltIn
from datetime import datetime


class SimpleRetryCore:
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self):
        self.builtin = BuiltIn()
        self.failed_keyword = None
        self.current_test = None
        self.current_suite = None
        self.continue_event = threading.Event()
        self.retry_success = False
        self.abort_suite = False
        self.gui_controller = None
        self.skip_test = False

        logging.basicConfig(
            filename="retry_debug.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def start_suite(self, data, result):
        self.current_suite = data.name
        logging.info(f"Suite started: {self.current_suite}")

    def start_test(self, data, result):
        self.current_test = data.name
        logging.info(f"Test started: {self.current_test}")

    def end_keyword(self, data, result):
        if self.abort_suite:
            result.status = 'FAIL'
            result.message = 'Suite aborted by user'
            logging.warning("Suite aborted by user.")
            return

        if self.skip_test:
            result.status = 'FAIL'
            result.message = 'Test skipped by user'
            self.skip_test = False
            logging.info("Test skipped by user.")
            return

        if result.status == 'FAIL':
            self.failed_keyword = data
            self._handle_failure(data, result)

    def _handle_failure(self, data, result):
        if self.gui_controller:
            self.gui_controller.show_failure(
                suite=self.current_suite,
                test=self.current_test,
                keyword=data.name,
                message=result.message or "(No failure message)",
                args=data.args
            )
            self.continue_event.clear()
            self.continue_event.wait()

            if self.retry_success:
                result.status = 'PASS'
                result.message = 'Keyword retried and succeeded.'
                self.retry_success = False
                logging.info("Retry succeeded.")

    def retry_keyword(self, kw_name, args):
        try:
            result = self.builtin.run_keyword_and_ignore_error(kw_name, *args)
            logging.info(f"Retry result for {kw_name}: {result}")
            return result
        except Exception as e:
            logging.exception("Exception during retry:")
            return ('FAIL', str(e))

    def parse_arg(self, val):
        if not isinstance(val, str):
            return val

        val = val.strip()
        if not val:
            return val

        lowered = val.lower()
        if lowered in ('none', 'null'):
            return None
        if lowered == 'true':
            return True
        if lowered == 'false':
            return False

        try:
            return ast.literal_eval(val)
        except:
            return val
