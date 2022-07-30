import json
from decimal import Decimal, DecimalException
from logging import getLogger
from typing import Union

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.response import Response

from ap_anchor_server.models import Customer, StellarId, CustomerType
from ap_anchor_server.serializers import serialize_customer

logger = getLogger(__name__)


class CustomerView(APIView):
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]

    @staticmethod
    def get(request: Request) -> Response:
        db_query_args = {}
        if request.query_params.get("id"):
            db_query_args["id"] = request.query_params.get("id")
            try:
                customer = Customer.objects.get(**db_query_args)
            except ObjectDoesNotExist:
                return Response({"error": "not found"}, status=404)
        elif request.query_params.get("account"):
            db_query_args["account"] = request.query_params.get("account")
            db_query_args["memo"] = request.query_params.get("memo")
            db_query_args["memo_type"] = request.query_params.get("memo_type")
            try:
                customer = (
                    StellarId.objects.select_related("customer")
                    .get(**db_query_args)
                    .customer
                )
            except ObjectDoesNotExist:
                customer = None
        else:
            customer = None
        data = serialize_customer(customer, for_type=request.query_params.get("type"))
        logger.info("GET /customer response:")
        logger.info(json.dumps(data, indent=4))
        return Response(data)

    def put(self, request: Request) -> Response:
        new_stellar_id = False
        if request.data.get("id"):
            try:
                customer = Customer.objects.get(id=request.data.get("id"))
            except ObjectDoesNotExist:
                customer = None
        else:  # account, memo, & memo_type provided
            try:
                customer = (
                    StellarId.objects.select_related("customer")
                    .get(
                        account=request.data.get("account"),
                        memo=request.data.get("memo"),
                        memo_type=request.data.get("memo_type"),
                    )
                    .customer
                )
            except ObjectDoesNotExist:
                customer = None
                new_stellar_id = True
        # might be an existing customer with a different account, memo, & memo_type
        # so try querying for the customer by first & last name
        if (
            customer is None
            and request.data.get("first_name")
            and request.data.get("last_name")
        ):
            try:
                customer = Customer.objects.get(
                    first_name=request.data.get("first_name"),
                    last_name=request.data.get("last_name"),
                )
            except ObjectDoesNotExist:
                pass
        if customer is None:
            customer_or_response = self.create_customer(request)
            if isinstance(customer_or_response, Customer):
                customer = customer_or_response
            else:
                return customer_or_response
        else:
            self.update_customer(customer, new_stellar_id, request)
        data = {"id": str(customer.id)}
        logger.info("PUT /customer response:")
        logger.info(json.dumps(data, indent=4))
        return Response(data)

    @staticmethod
    def create_customer(request: Request) -> Union[Customer, Response]:
        if not (request.data.get("first_name") and request.data.get("last_name")):
            return Response({"error": "'first_name' & 'last_name' are required"}, 400)
        if request.data.get("type"):
            if request.data.get("type") not in [
                CustomerType.SEP31_SENDER,
                CustomerType.SEP31_RECEIVER,
            ]:
                return Response({"error": "unrecognized 'type'"}, 400)
            if request.data.get("type") == CustomerType.SEP31_RECEIVER and not (
                request.data.get("bank_number")
                and request.data.get("bank_account_number")
            ):
                return Response(
                    {
                        "error": (
                            "'bank_number' & 'bank_account_number' are required for type "
                            f"{CustomerType.SEP31_RECEIVER}"
                        )
                    },
                    400,
                )
        customer = Customer(
            first_name=request.data.get("first_name"),
            last_name=request.data.get("last_name"),
        )
        if request.data.get("bank_number"):
            customer.bank_number = request.data.get("bank_number")
        if request.data.get("bank_account_number"):
            customer.bank_account_number = request.data.get("bank_account_number")
        customer.save()
        StellarId.objects.create(
            customer=customer,
            account=request.data.get("account"),
            memo=request.data.get("memo"),
            memo_type=request.data.get("memo_type"),
        )
        return customer

    @staticmethod
    def update_customer(customer: Customer, new_stellar_id: bool, request: Request):
        if request.data.get("first_name"):
            customer.first_name = request.data.get("first_name")
        if request.data.get("last_name"):
            customer.last_name = request.data.get("last_name")
        if request.data.get("bank_number"):
            customer.bank_number = request.data.get("bank_number")
        if request.data.get("bank_account_number"):
            customer.bank_account_number = request.data.get("bank_account_number")
        customer.save()
        if new_stellar_id:
            StellarId.objects.create(
                customer=customer,
                account=request.data.get("account"),
                memo=request.data.get("memo"),
                memo_type=request.data.get("memo_type"),
            )


class FeeView(APIView):
    @staticmethod
    def get(request: Request) -> Response:
        logger.info("GET /fee request:")
        logger.info(json.dumps(dict(request.query_params), indent=4))
        data = {
            "fee": {
                "amount": str(
                    round(
                        Decimal(request.query_params.get("send_amount"))
                        * Decimal(0.01),
                        7,
                    )
                ),
                "asset": request.query_params.get("send_asset"),
            }
        }
        logger.info("GET /fee response:")
        logger.info(json.dumps(data, indent=4))
        return Response(data)
