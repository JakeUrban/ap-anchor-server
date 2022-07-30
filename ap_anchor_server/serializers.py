from typing import Tuple

from django.db.models import Field

from ap_anchor_server.models import (
    Customer,
    CUSTOMER_FIELDS,
    CustomerType,
    CustomerStatus,
)


def serialize_customer(customer: Customer = None, for_type: str = None):
    if for_type not in [CustomerType.SEP31_SENDER, CustomerType.SEP31_RECEIVER, None]:
        raise ValueError("unexpected 'for_type'")
    if for_type is None:
        for_type = CustomerType.SEP31_RECEIVER
    fields = CUSTOMER_FIELDS.copy()
    model_fields = Customer._meta.get_fields()
    if customer:
        response = serialize_existing_customer(customer, fields, model_fields, for_type)
    else:
        response = serialize_nonexistent_customer(fields, model_fields, for_type)
    return response


def serialize_existing_customer(
    customer: Customer, fields: dict, model_fields: Tuple[Field], for_type: str
) -> dict:
    response = {"fields": {}, "provided_fields": {}, "id": str(customer.id)}
    if for_type == CustomerType.SEP31_SENDER:
        # PUT requires first & last name for all types
        # so those fields must be accepted already
        response["status"] = CustomerStatus.ACCEPTED
    else:
        if customer.bank_number and customer.bank_account_number:
            response["status"] = CustomerStatus.ACCEPTED
        else:
            response["status"] = CustomerStatus.NEEDS_INFO
    for model_field in model_fields:
        if model_field.name not in fields:
            continue
        if getattr(customer, model_field.name, None):
            response["provided_fields"][model_field.name] = fields[model_field.name]
            response["provided_fields"][model_field.name][
                "status"
            ] = CustomerStatus.ACCEPTED
        else:
            response["fields"][model_field.name] = fields[model_field.name]
    return response


def serialize_nonexistent_customer(
    fields: dict, model_fields: Tuple[Field], for_type: str
) -> dict:
    response = {
        "fields": {},
        "provided_fields": {},
        "status": CustomerStatus.NEEDS_INFO,
    }
    if for_type == CustomerType.SEP31_SENDER:
        response["fields"] = {
            "first_name": fields["first_name"],
            "last_name": fields["last_name"],
        }
    else:
        for model_field in model_fields:
            if model_field.name not in fields:
                continue
            response["fields"][model_field.name] = fields[model_field.name]
    return response
