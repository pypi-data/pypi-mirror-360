from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    FATAL = 'FATAL'


class ErrorListHandler:
    __static_error_list: list = []
    __static_current_module: str = "General"

    @classmethod
    def clear_list(cls):
        cls.__static_error_list.clear()
    @classmethod
    def add_entry(cls, severity: LogLevel, user_entry: str):
        entry = f"[{severity.value}] {datetime.now()} - {cls.__static_current_module} - {user_entry}"
        cls.__static_error_list.append(entry)

    @classmethod
    def update_current_module_name(cls, new_module_name: str):
        cls.__static_current_module = new_module_name.upper()

    @classmethod
    def get_current_module(cls)->str:
        return cls.__static_current_module

    @classmethod
    def get_error_list(cls)->str:
        return cls.__static_error_list

