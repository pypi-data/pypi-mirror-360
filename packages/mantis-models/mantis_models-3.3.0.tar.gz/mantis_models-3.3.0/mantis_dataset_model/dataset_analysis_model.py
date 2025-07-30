# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel

"""
Class Model for the results of a dataset analysis
It might be updated, especially for the basic_requirements
"""


class CommandStats(BaseModel):
    """
    Global stats for all the executed attacks in the dataset
    """

    total_found: int  # The total number of command retrieved from the logs for the attack expected
    total_commands: int  # The total number of commands performed according to the redteam's attacks.json (decoded_command field)
    percent_found: float  # The ratio (total_found/total_commands) * 100. Defaulting to 0.0 if total_commands is 0


class CommandPerformed(BaseModel):
    """
    The command and the result if it was found in the dataset
    """

    command: str  # The command performed for the attack
    found: bool  # if the command was found in the dataset's logs
    log_file: Optional[str] = None
    line: Optional[int] = None


class LogMessages(BaseModel):
    error_messages: List[str] = []
    warning_messages: List[str] = []
    success_messages: List[str] = []

    def display(self, logger: Any):

        if len(self.success_messages) > 0:
            logger.success("[+] Success messages:")
            for s in self.success_messages:
                logger.success(f"\t[+] {s}")
        else:
            logger.warning("[+] No success messages")

        if len(self.warning_messages) > 0:
            logger.warning("[!] Warning messages:")
            for w in self.warning_messages:
                logger.warning(f"\t[!] {w}")
        else:
            logger.success("[+] No warning messages")

        if len(self.error_messages) > 0:
            logger.error("[-] Error messages:")
            for e in self.error_messages:
                logger.error(f"\t[-] {e}")
        else:
            logger.success("[+] No error messages")

        logger.info("")

    def add_error(self, e):
        self.error_messages.append(e)

    def add_warning(self, w):
        self.warning_messages.append(w)

    def add_success(self, s):
        self.success_messages.append(s)

    def merge(
        self, report: "LogMessages"
    ):  # Mandatory to import class name from the same class
        self.error_messages = self.error_messages + report.error_messages
        self.warning_messages = self.warning_messages + report.warning_messages
        self.success_messages = self.success_messages + report.success_messages


class CommandAnalysisReport(LogMessages):
    """
    Default Analysis : the Amossys' one
    """

    command_performed: List[CommandPerformed]
    command_stats: CommandStats

    def display(self, logger: Any):
        logger.info("[+] Commands performed")
        for c in self.command_performed:
            if c.found is True:
                logger.success(f"\t[+] Command: {c.command}")
                logger.success(f"\t[+] found in line {c.line} in {c.log_file}")
            else:
                logger.error(f"\t[-] Command not found: {c.command}")
        logger.info("[+] Commands stats")
        logger.info(f"\t[+] {self.command_stats}")

        return super().display(logger)


class DatasetAnalysisResult(BaseModel):
    name: str
    description: str
    date_analysis_result_created: datetime
    command_analysis: CommandAnalysisReport
    reports: Dict[str, LogMessages]

    def display(self, logger: Any):
        logger.info("[+] Analysis Reports: ")
        self.command_analysis.display(logger)
        for k, v in self.reports.items():
            logger.info(f"[+] Result for report '{k}'")
            v.display(logger)
