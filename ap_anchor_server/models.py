import random

from django.db import models


def positive_big_integer():
    return random.randrange(0, 9223372036854775807)


class CustomerType:
    SEP31_SENDER = "sep31-sender"
    SEP31_RECEIVER = "sep31-receiver"


CUSTOMER_FIELDS = {
    "first_name": {"description": "first name", "type": "string"},
    "last_name": {"description": "last name", "type": "string"},
    "bank_account_number": {
        "description": "United States bank account number",
        "type": "string",
    },
    "bank_number": {
        "description": "United States bank routing number",
        "type": "string",
    },
}


class Customer(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True, default=positive_big_integer)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    bank_account_number = models.CharField(max_length=128)
    bank_number = models.CharField(max_length=128)


class CustomerStatus:
    NEEDS_INFO = "NEEDS_INFO"
    PROCESSING = "PROCESSING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class MemoType:
    TEXT = "text"
    HASH = "hash"
    ID = "id"


class StellarId(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    account = models.CharField(max_length=128)
    memo = models.CharField(max_length=128)
    memo_type = models.CharField(max_length=4)
