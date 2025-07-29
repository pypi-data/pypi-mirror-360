from logging import Logger
from typing import Awaitable, Callable

from aiokafka import ConsumerRebalanceListener, TopicPartition


# @see = https://aiokafka.readthedocs.io/en/stable/api.html#aiokafka.abc.ConsumerRebalanceListener.on_partitions_assigned
class KafkaCallbackRebalancer(ConsumerRebalanceListener):
    def __init__(
        self,
        logger: Logger,
        on_partitions_revoked: Callable[[set[TopicPartition]], Awaitable[None]],
        on_partitions_assigned: Callable[[set[TopicPartition]], Awaitable[None]],
    ):
        self.__logger = logger
        self.__on_partition_revoked = on_partitions_revoked
        self.__on_partition_assigned = on_partitions_assigned
        self.__assigned_partitions: set[TopicPartition] = set()

    async def on_partitions_revoked(self, revoked: set[TopicPartition]) -> None:
        if len(revoked) == 0:
            return None

        self.__logger.info(f"Partitions revoked by the rebalancing process: '{revoked}'")

        await self.__on_partition_revoked(revoked)
        self.__assigned_partitions.difference_update(revoked)

        self.__logger.info(f"Partitions after revoking process: '{self.__assigned_partitions}'")

    async def on_partitions_assigned(self, assigned: set[TopicPartition]) -> None:
        new_partitions_assigned = assigned.difference(self.__assigned_partitions)

        if len(new_partitions_assigned) == 0:
            return None

        self.__logger.info(f"Partitions assigned by the rebalancing process: '{new_partitions_assigned}'")

        await self.__on_partition_assigned(new_partitions_assigned)
        self.__assigned_partitions.update(new_partitions_assigned)

        self.__logger.info(f"Partitions after assigning process: '{self.__assigned_partitions}'")
