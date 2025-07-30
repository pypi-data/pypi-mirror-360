
"""
Tests for the Sessions API v1 endpoints.

This module contains tests for the sessions API endpoints in synth_codeai/server/api_v1_sessions.py.
It tests the creation, listing, and retrieval of sessions through the API.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from unittest.mock import patch
import datetime

from synth_codeai.server.api_v1_sessions import router, get_repository
from synth_codeai.database.pydantic_models import SessionModel, TrajectoryModel
from synth_codeai.database.repositories.trajectory_repository import get_trajectory_repository


# Mock session data for testing
@pytest.fixture
def mock_session():
    """Return a mock session for testing."""
    return SessionModel(
        id=1,
        created_at=datetime.datetime(2025, 1, 1, 0, 0, 0),
        updated_at=datetime.datetime(2025, 1, 1, 0, 0, 0),
        start_time=datetime.datetime(2025, 1, 1, 0, 0, 0),
        command_line="synth-codeai test",
        program_version="1.0.0",
        machine_info={"os": "test"},
        status='test_status'
    )


@pytest.fixture
def mock_sessions():
    """Return a list of mock sessions for testing."""
    return [
        SessionModel(
            id=1,
            created_at=datetime.datetime(2025, 1, 1, 0, 0, 0),
            updated_at=datetime.datetime(2025, 1, 1, 0, 0, 0),
            start_time=datetime.datetime(2025, 1, 1, 0, 0, 0),
            command_line="synth-codeai test1",
            program_version="1.0.0",
            machine_info={"os": "test"},
            status='test_status'
        ),
        SessionModel(
            id=2,
            created_at=datetime.datetime(2025, 1, 2, 0, 0, 0),
            updated_at=datetime.datetime(2025, 1, 2, 0, 0, 0),
            start_time=datetime.datetime(2025, 1, 2, 0, 0, 0),
            command_line="synth-codeai test2",
            program_version="1.0.0",
            machine_info={"os": "test"},
            status='test_status'
        )
    ]


@pytest.fixture
def mock_repo(mock_session, mock_sessions):
    """Mock the SessionRepository for testing."""
    repo = MagicMock()
    
    # Mock individual get method
    repo.get.return_value = mock_session
    
    # Note: get_all is deprecated, but kept for backward compatibility
    repo.get_all.return_value = (mock_sessions, len(mock_sessions))
    
    repo.create_session.return_value = mock_session
    return repo


@pytest.fixture
def mock_trajectory():
    """Return a mock trajectory for testing."""
    return TrajectoryModel(
        id=1,
        created_at=datetime.datetime(2025, 1, 1, 0, 0, 0),
        updated_at=datetime.datetime(2025, 1, 1, 0, 0, 0),
        human_input_id=1,
        tool_name="test_tool",
        tool_parameters={"param": "value"},
        tool_result={"result": "success"},
        step_data={"step": "data"},
        record_type="tool_execution",
        current_cost=0.01,
        input_tokens=10,
        output_tokens=20,
        is_error=False,
        session_id=1
    )


@pytest.fixture
def mock_trajectories():
    """Return a list of mock trajectories for testing."""
    return [
        TrajectoryModel(
            id=1,
            created_at=datetime.datetime(2025, 1, 1, 0, 0, 0),
            updated_at=datetime.datetime(2025, 1, 1, 0, 0, 0),
            human_input_id=1,
            tool_name="test_tool_1",
            tool_parameters={"param": "value1"},
            tool_result={"result": "success"},
            step_data={"step": "data1"},
            record_type="tool_execution",
            current_cost=0.01,
            input_tokens=10,
            output_tokens=20,
            is_error=False,
            session_id=1
        ),
        TrajectoryModel(
            id=2,
            created_at=datetime.datetime(2025, 1, 1, 0, 5, 0),
            updated_at=datetime.datetime(2025, 1, 1, 0, 5, 0),
            human_input_id=1,
            tool_name="test_tool_2",
            tool_parameters={"param": "value2"},
            tool_result={"result": "success"},
            step_data={"step": "data2"},
            record_type="tool_execution",
            current_cost=0.02,
            input_tokens=15,
            output_tokens=25,
            is_error=False,
            session_id=1
        )
    ]


@pytest.fixture
def mock_trajectory_repo(mock_trajectories):
    """Mock the TrajectoryRepository for testing."""
    repo = MagicMock()
    repo.get_trajectories_by_session.return_value = mock_trajectories
    return repo


@pytest.fixture
def client(mock_repo, mock_trajectory_repo):
    """Return a TestClient for the API router with dependency overrides."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    
    # Override the dependencies
    app.dependency_overrides[get_repository] = lambda: mock_repo
    app.dependency_overrides[get_trajectory_repository] = lambda: mock_trajectory_repo
    
    return TestClient(app)


def test_get_session(client, mock_repo, mock_session):
    """Test getting a specific session by ID."""
    response = client.get("/v1/session/1")
    
    assert response.status_code == 200
    assert response.json()["id"] == mock_session.id
    assert response.json()["command_line"] == mock_session.command_line
    mock_repo.get.assert_called_once_with(1)


def test_get_session_not_found(client, mock_repo):
    """Test getting a session that doesn't exist."""
    mock_repo.get.return_value = None
    
    response = client.get("/v1/session/999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
    mock_repo.get.assert_called_once_with(999)


def test_list_sessions(client, mock_repo, mock_sessions):
    """Test listing sessions with pagination."""
    response = client.get("/v1/session?offset=0&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(mock_sessions)
    assert len(data["items"]) == len(mock_sessions)
    assert data["limit"] == 10
    assert data["offset"] == 0
    mock_repo.get_all.assert_called_once_with(offset=0, limit=10)


def test_create_session(client, mock_repo, mock_session):
    """Test creating a new session."""
    response = client.post(
        "/v1/session",
        json={"metadata": {"test": "data"}}
    )
    
    assert response.status_code == 201
    assert response.json()["id"] == mock_session.id
    mock_repo.create_session.assert_called_once_with(metadata={"test": "data"})


def test_create_session_no_body(client, mock_repo, mock_session):
    """Test creating a new session without a request body."""
    response = client.post("/v1/session")
    
    assert response.status_code == 201
    assert response.json()["id"] == mock_session.id
    mock_repo.create_session.assert_called_once_with(metadata=None)


def test_get_session_trajectories(client, mock_repo, mock_trajectory_repo, mock_trajectories):
    """Test getting all trajectories for a specific session."""
    # Ensure the session exists
    mock_repo.get.return_value = SessionModel(
        id=1,
        created_at=datetime.datetime(2025, 1, 1, 0, 0, 0),
        updated_at=datetime.datetime(2025, 1, 1, 0, 0, 0),
        start_time=datetime.datetime(2025, 1, 1, 0, 0, 0),
        command_line="synth-codeai test",
        program_version="1.0.0",
        machine_info={"os": "test"},
        status='test_status'
    )
    
    response = client.get("/v1/session/1/trajectory")
    
    assert response.status_code == 200
    trajectories = response.json()
    assert len(trajectories) == len(mock_trajectories)
    assert trajectories[0]["id"] == mock_trajectories[0].id
    assert trajectories[0]["tool_name"] == mock_trajectories[0].tool_name
    assert trajectories[1]["id"] == mock_trajectories[1].id
    assert trajectories[1]["tool_name"] == mock_trajectories[1].tool_name
    
    # Verify correct method calls
    mock_repo.get.assert_called_once_with(1)
    mock_trajectory_repo.get_trajectories_by_session.assert_called_once_with(1)


def test_get_session_trajectories_not_found(client, mock_repo, mock_trajectory_repo):
    """Test getting trajectories for a session that doesn't exist."""
    # Ensure the session doesn't exist
    mock_repo.get.return_value = None
    
    response = client.get("/v1/session/999/trajectory")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
    mock_repo.get.assert_called_once_with(999)
    # Ensure the trajectory repository is not called
    mock_trajectory_repo.get_trajectories_by_session.assert_not_called()



def test_delete_session_success(client, mock_repo, mock_session):
    mock_repo.get.return_value = mock_session

    with patch("synth_codeai.server.api_v1_sessions.is_agent_running", return_value=True), \
            patch("synth_codeai.server.api_v1_sessions.stop_agent", return_value=True):
        response = client.delete("/v1/session/1")
        assert response.status_code == 204
        mock_repo.get.assert_called_once_with(1)
        mock_repo.update_session_status.assert_called_once_with(1, "halting")


def test_delete_session_not_found(client, mock_repo):
    mock_repo.get.return_value = None
    response = client.delete("/v1/session/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
    mock_repo.get.assert_called_once_with(999)