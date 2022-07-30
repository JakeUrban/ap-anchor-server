import json
from logging import getLogger

import requests
from django.core.management import BaseCommand
from django.conf import settings
from kafka import KafkaConsumer

logger = getLogger(__name__)
TRANSACTION_STATUS_CHANGE = "transaction_status_changed"


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("starting streamevents...")
        consumer = KafkaConsumer(
            "all-events",
            bootstrap_servers=[settings.KAFKA_HOST],
            value_deserializer=lambda v: json.loads(v.decode()),
        )
        for message in consumer:
            logger.info("event received:")
            logger.info(json.dumps(message.value, indent=4))
            self.process_event(message.value)

    def process_event(self, message: dict):
        logger.info(f"processing event {message.get('event_id')}")
        if not (
            message.get("type") == TRANSACTION_STATUS_CHANGE
            and message.get("status") == "pending_receiver"
        ):
            return
        self.deliver_funds(message.get("id"))
        response = requests.patch(
            f"http://{settings.PLATFORM_HOST}/transactions",
            json={"records": [{"id": message.get("id"), "status": "completed"}]},
        )
        if response.status_code != 200:
            logger.info(
                f"unexpected response from PATCH /transactions ({response.status_code}):"
            )
            logger.info(json.dumps(response.json()))

    def deliver_funds(self, _transaction_id):
        """
        A stubbed method for initiating the delivery of funds to the recipient.

        If the anchor is able to verify when funds have been received by the
        recipient, the anchor should update the transaction's status to
        `pending_external` after delivery has been initiated but not completed.

        When funds have been received, or if the anchor cannot verify when funds
        have been received, the anchor should update the transaction's status to
        `completed`.
        """
        pass
