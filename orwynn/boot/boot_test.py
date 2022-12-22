import os
from pytest import fixture
from orwynn.app_rc.AppRC import AppRC
from orwynn.base.database.DatabaseKind import DatabaseKind
from orwynn.boot._BootProxy import BootProxy
from orwynn.boot._BootMode import BootMode
from orwynn.base.module.Module import Module

from orwynn.boot._Boot import Boot
from orwynn.boot.UnknownBootModeError import UnknownBootModeError
from orwynn.di.DI import DI
from orwynn.mongo.Mongo import Mongo
from orwynn.util import validation
from tests.std.text import TextConfig


@fixture
def std_boot(std_struct: Module) -> Boot:
    return Boot(
        root_module=std_struct
    )


@fixture
def run_std_boot(std_struct: Module):
    Boot(std_struct)


@fixture
def std_mongo_boot(std_struct: Module) -> Boot:
    os.environ["Orwynn_AppRCDir"] = os.path.join(os.getcwd(), "tests/std")
    return Boot(
        root_module=std_struct,
        databases=[DatabaseKind.MONGO]
    )


@fixture
def set_prod_mode():
    os.environ["Orwynn_Mode"] = "prod"


@fixture
def set_dev_mode():
    os.environ["Orwynn_Mode"] = "dev"


@fixture
def set_test_mode():
    os.environ["Orwynn_Mode"] = "test"


@fixture
def set_std_app_rc_dir():
    os.environ["Orwynn_AppRCDir"] = os.path.join(os.getcwd(), "tests/std")


def test_init_mode_default(std_struct: Module):
    os.environ["Orwynn_Mode"] = ""
    boot: Boot = Boot(
        root_module=std_struct
    )
    assert boot.mode == BootMode.DEV


def test_init_mode_test(std_struct: Module):
    os.environ["Orwynn_Mode"] = "test"
    boot: Boot = Boot(
        root_module=std_struct
    )
    assert boot.mode == BootMode.TEST


def test_init_mode_dev(std_struct: Module):
    os.environ["Orwynn_Mode"] = "dev"
    boot: Boot = Boot(
        root_module=std_struct
    )
    assert boot.mode == BootMode.DEV


def test_init_mode_prod(std_struct: Module):
    os.environ["Orwynn_Mode"] = "prod"
    boot: Boot = Boot(
        root_module=std_struct
    )
    assert boot.mode == BootMode.PROD


def test_init_incorrect_mode(std_struct: Module):
    os.environ["Orwynn_Mode"] = "helloworld"
    validation.expect(Boot, UnknownBootModeError, root_module=std_struct)


def test_init_enable_mongo(std_struct: Module, set_std_app_rc_dir):
    Boot(
        root_module=std_struct,
        databases=[DatabaseKind.MONGO]
    )

    assert Mongo.ie()


def test_nested_configs_prod(
    std_struct: Module,
    set_std_app_rc_dir,
    set_prod_mode
):
    Boot(
        root_module=std_struct
    )
    app_rc: AppRC = BootProxy.ie().app_rc
    text_config: TextConfig = DI.ie().find("TextConfig")

    assert app_rc["Text"]["words_amount"] == text_config.words_amount == 1


def test_nested_configs_dev(
    std_struct: Module,
    set_std_app_rc_dir,
    set_dev_mode
):
    Boot(
        root_module=std_struct
    )
    app_rc: AppRC = BootProxy.ie().app_rc
    text_config: TextConfig = DI.ie().find("TextConfig")

    assert app_rc["Text"]["words_amount"] == text_config.words_amount == 2


def test_nested_configs_test(
    std_struct: Module,
    set_std_app_rc_dir,
    set_test_mode
):
    Boot(
        root_module=std_struct
    )
    app_rc: AppRC = BootProxy.ie().app_rc
    text_config: TextConfig = DI.ie().find("TextConfig")

    assert app_rc["Text"]["words_amount"] == text_config.words_amount == 3
