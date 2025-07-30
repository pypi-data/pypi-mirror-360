import json
import os
from collections.abc import Iterable
from enum import Enum
from database_mysql_local.generic_crud import GenericCRUD
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.MetaLogger import MetaLogger
from user_context_remote.user_context import UserContext


from .our_queue import OurQueue

QUEUE_LOCAL_PYTHON_COMPONENT_ID = 156
QUEUE_LOCAL_PYTHON_COMPONENT_NAME = "queue_local/src/database_queue.py"
DEVELOPER_EMAIL = 'akiva.s@circ.zone'
queue_logger_object = {
    'component_id': QUEUE_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': QUEUE_LOCAL_PYTHON_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': DEVELOPER_EMAIL
}


class QueueStatusEnum(Enum):
    NEW = 0
    RETRIEVED = 1


class DatabaseQueue(OurQueue, GenericCRUD, metaclass=MetaLogger, object=queue_logger_object):
    """A queue that uses a database table as the queue."""

    def __init__(self, *, schema_name: str = "queue", table_name: str = "queue_item_table",
                 view_name: str = "queue_item_view", queue_item_id_column_name: str = "queue_item_id",
                 is_test_data: bool = False) -> None:
        """Initialize the queue.
        Make sure the table has the following columns:
            queue_status_id, action_id, process_id, user_jwt
            created_user_id, updated_user_id
            updated_timestamp, start_timestamp, end_timestamp

        ALTER TABLE `invitation`.`invitation_table`
            ADD COLUMN `queue_status_id` SMALLINT UNSIGNED NULL AFTER `updated_effective_profile_id`,
            ADD COLUMN `action_id` SMALLINT UNSIGNED NULL AFTER `queue_status_id`,
            ADD COLUMN `process_id` MEDIUMINT UNSIGNED NULL AFTER `action_id`,
            ADD COLUMN `user_jwt` VARCHAR(255) NULL AFTER `process_id`;


        Default schema_name = the first part of the table_name, before the first underscore.
        Default view_name = table_name with "_view" instead of "_table"
            (or "_view" added to the end if there is no "_table").
        You can pass a Connector object to use an existing connection, or None to create a new connection.
        """
        if not view_name:
            if table_name.endswith("_table"):
                view_name = table_name.replace("_table", "_view")
            else:
                view_name = table_name + "_view"
        if not schema_name:
            schema_name = table_name.split("_")[0]
        self.queue_item_id_column_name = queue_item_id_column_name
        self.schema_name = schema_name

        GenericCRUD.__init__(self, default_schema_name=schema_name, default_table_name=table_name,
                             default_view_table_name=view_name, default_column_name=queue_item_id_column_name,
                             is_test_data=is_test_data)
        self.user_context = UserContext()

    def push(self, queue_data_dict: dict = None, queue_dict: dict = None) -> int:
        queue_dict = queue_dict or queue_data_dict
        """Pushes a new entry to the queue and returns the new queue id.
        queue_dict consists of columns and values to insert into the queue table."""
        created_user_id = UserContext().get_effective_user_id()

        self._fix_parameters_json(queue_dict)

        queue_dict["queue_status_id"] = QueueStatusEnum.NEW.value

        queue_dict["created_user_id"] = created_user_id

        if self.queue_item_id_column_name in queue_dict:
            column_value = queue_dict[self.queue_item_id_column_name]
            del queue_dict[self.queue_item_id_column_name]
            self.update_by_column_and_value(column_value=column_value, data_dict=queue_dict)
            queue_id = column_value
        else:
            queue_id = self.insert(data_dict=queue_dict)
        return queue_id
        # TODO Can we do this everywhere?  [I will make it auto in the meta logger]

    def push_back(self, queue_item: dict = None, queue_dict: dict = None) -> None:
        """Push a taken queue item back to the queue."""
        queue_dict = queue_item or queue_dict
        queue_dict = {"queue_status_id": QueueStatusEnum.NEW.value,
                      "process_id": None}
        self.update_by_column_and_value(
            column_value=queue_item[self.queue_item_id_column_name],
            data_dict=queue_dict)

    def get(self, *, action_ids: tuple = (), custom_condition: str = "",
            data_dict: dict = None, queue_dict: dict = None) -> dict:
        """
        Returns the first item from the queue (possibly considering specific actions) and marks it as taken.

        :param action_ids: Tuple of action IDs to consider (optional).
        :param custom_condition: Custom condition to add to the WHERE clause (optional).
        :return: Dictionary representing the retrieved queue item.
        """
        queue_dict = data_dict or queue_dict
        action_ids = self._fix_action_ids(action_ids)
        queue_dict = {"process_id": os.getpid()}
        update_where = f"process_id IS NULL " \
                       f"AND (queue_status_id IS NULL OR queue_status_id = {QueueStatusEnum.NEW.value}) " \
                       f"AND NOW() > start_timestamp AND (end_timestamp is NULL or NOW() < end_timestamp) " + \
                       (f"AND action_id IN {action_ids} " if action_ids else "") + \
                       (f"AND {custom_condition}" if custom_condition else "")
        self.update_by_where(where=update_where,
                             order_by=self.queue_item_id_column_name,
                             limit=1, data_dict=queue_dict)

        select_where = f"process_id = {os.getpid()} AND (queue_status_id IS NULL OR queue_status_id = {QueueStatusEnum.NEW.value})"  # noqa: E501

        queue_item = self.select_one_dict_by_where(where=select_where)
        if queue_item:
            update_queue_dict = {"queue_status_id": QueueStatusEnum.RETRIEVED.value,
                                 "user_jwt": self.user_context.get_user_jwt()}
            self.update_by_column_and_value(
                column_value=queue_item[self.queue_item_id_column_name],
                data_dict=update_queue_dict)
            self.logger.info(
                "Entry retrieved and updated from the queue database successfully",  # noqa: E501
                object=queue_item)
        else:
            self.logger.info("The queue is empty")
        return queue_item

    def peek(self, action_ids: tuple = ()) -> dict:
        """Get the first item in the queue without changing it"""
        action_ids = self._fix_action_ids(action_ids)
        where = f"process_id IS NULL AND queue_status_id = {QueueStatusEnum.NEW.value}" + \
                (f" AND action_id IN {action_ids}" if action_ids else "")
        # SELECT * FROM `queue`.`queue_item_view` WHERE process_id IS NULL AND queue_status_id = 0
        # AND action_id IN (1, 2, 3) ORDER BY queue_item_id LIMIT 1
        queue_item = self.select_one_dict_by_where(
            where=where, order_by=self.queue_item_id_column_name)
        return queue_item

    def _fix_action_ids(self, action_ids):
        """Fixes the action_ids argument to fit the SQL syntax (action_id IN action_ids)"""
        if isinstance(action_ids, int):
            action_ids = (action_ids,)
        elif isinstance(action_ids, Iterable):
            action_ids = tuple(action_ids)
        else:
            self.logger.error("get_by_action_ids (queue database) invalid argument",
                              object={"action_ids": action_ids})
            raise ValueError(f"`action_ids` must be a tuple, not `{action_ids}`")
        fix_action_ids_result = \
            action_ids if len(action_ids) != 1 else f"({action_ids[0]})"
        return fix_action_ids_result

    @staticmethod
    def _fix_parameters_json(data_dict: dict = None):
        queue_dict = data_dict
        """Fixes the parameters_json argument to fit the SQL syntax (parameters_json must be a string)"""  # noqa: E501
        for key, value in queue_dict.items():
            if "parameters_json" in key:
                if isinstance(value, str):
                    queue_dict[key] = value.replace("'", '"')
                else:
                    queue_dict[key] = json.dumps(value)
