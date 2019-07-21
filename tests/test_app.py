#!/usr/bin/env python3
# coding: utf-8

import os
from unittest.mock import sentinel, call

import pytest

from rerwatcher.app import RerWatcher
from tests.conftest import CONFIG


def test_rerwatcher_load_config(mocker):
    mocker.patch.dict(os.environ, {'API__URL': 'http://test.url'})

    config = RerWatcher.load_config()

    assert config['api']['url'] == 'http://test.url'
    assert config['device']['type'] == 'console'


def test_rerwatcher_workflow(mocker, mock_config):
    sleep = mocker.patch(
        'rerwatcher.app.time.sleep',
        side_effect=[True, KeyboardInterrupt]
    )
    display = mocker.Mock()
    display_builder = mocker.patch(
        'rerwatcher.app.DisplayDeviceFactory.build',
        return_value=display
    )
    api = mocker.patch(
        'rerwatcher.app.TransilienApi',
        **{'return_value.fetch_data.return_value': sentinel.data}
    )
    formatter = mocker.patch(
        'rerwatcher.app.TransilienApiFormatter.format_response',
        return_value=[sentinel.timetable1, sentinel.timetable2]
    )

    app = RerWatcher(None)
    with pytest.raises(KeyboardInterrupt):
        app._app.start()

    display_builder.assert_called_once_with(CONFIG['device'])
    api.assert_called_once_with(CONFIG['api'])
    assert 2 == api().fetch_data.call_count
    expected_formatter_calls = [
        call(response=sentinel.data), call(response=sentinel.data)
    ]
    assert expected_formatter_calls == formatter.call_args_list
    expected_display_calls = [
        call(messages=[sentinel.timetable1, sentinel.timetable2]),
        call(messages=[sentinel.timetable1, sentinel.timetable2]),
    ]
    assert expected_display_calls == display.print.call_args_list
    assert 2 == sleep.call_count
