#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
import io

from aos_prov.utils.common import (
    generate_random_password,
    print_done,
    print_error,
    print_left,
    print_message,
    print_success,
)
from rich.console import Console


def test_print_message(mocker):
    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )

    print_message('test_message', ljust=1)
    assert 'test_message\n' == console_patched.file.getvalue()


def test_print_left(mocker):
    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )

    print_left('test_message')
    assert 'test_message' in console_patched.file.getvalue()


def test_print_done(mocker):
    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )

    print_done()
    assert 'DONE\n' == console_patched.file.getvalue()


def test_print_error(mocker):
    console_patched = mocker.patch(
        'aos_prov.utils.common.error_console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True, stderr=True),
    )

    print_error('test_message')
    assert 'test_message\n' == console_patched.file.getvalue()


def test_print_success(mocker):
    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )

    print_success('test_message')
    assert 'test_message\n' == console_patched.file.getvalue()


def test_generate_random_password():
    assert generate_random_password() != generate_random_password()
