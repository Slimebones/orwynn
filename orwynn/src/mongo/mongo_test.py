from orwynn.src import validation
from orwynn.src.mapping.CustomUseOfMappingReservedFieldError import (
    CustomUseOfMappingReservedFieldError,
)
from orwynn.src.mongo.Document import Document
from orwynn.src.mongo.DuplicateKeyError import DuplicateKeyError
from orwynn.src.proxy.BootProxy import BootProxy
from orwynn.src.testing.Client import Client
from orwynn.src.web.http.responses import TestHttpResponse
from tests.std.user import User


def test_user_create(std_mongo_boot, std_http: Client):
    r: TestHttpResponse = std_http.post(
        "/users",
        200,
        json={
            "name": "Mark Watney"
        }
    )
    created_user: User = User.recover(r.json())
    User.find_one({"id": created_user.id})


def test_reserved_mapping_field(std_mongo_boot, std_http: Client):
    class M(Document):
        mongo_filter: int

    validation.expect(M, CustomUseOfMappingReservedFieldError, mongo_filter=1)


def test_same_id_creation(std_mongo_boot, std_http: Client):
    r: TestHttpResponse = std_http.post(
        "/users",
        200,
        json={
            "name": "Mark Watney"
        }
    )
    r2: TestHttpResponse = std_http.post(
        "/users",
        400,
        json={
            "id": r.json()["value"]["id"],
            "name": "Mark Watney"
        }
    )

    validation.validate(
        BootProxy.ie().api_indication.recover(DuplicateKeyError, r2.json()),
        DuplicateKeyError
    )
