"""pytest 설정: 테스트 구분 표시(unit, integration)를 등록한다."""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "unit: 외부 도구 없이 도는 테스트")
    config.addinivalue_line("markers", "integration: ffmpeg를 실제로 부르는 테스트")
