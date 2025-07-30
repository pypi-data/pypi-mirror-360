'''API router for spawning an synth.codeai agent.'''

import threading
import logging
import json # Added for step_data serialization

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from synth_codeai.database.repositories.session_repository import SessionRepository, get_session_repository
from synth_codeai.database.connection import DatabaseManager
from synth_codeai.database.repositories.session_repository import SessionRepositoryManager
from synth_codeai.database.repositories.key_fact_repository import KeyFactRepositoryManager
from synth_codeai.database.repositories.key_snippet_repository import KeySnippetRepositoryManager
from synth_codeai.database.repositories.human_input_repository import HumanInputRepositoryManager, get_human_input_repository
from synth_codeai.database.repositories.research_note_repository import ResearchNoteRepositoryManager
from synth_codeai.database.repositories.related_files_repository import RelatedFilesRepositoryManager
from synth_codeai.database.repositories.trajectory_repository import TrajectoryRepositoryManager
from synth_codeai.database.repositories.work_log_repository import WorkLogRepositoryManager
from synth_codeai.database.repositories.config_repository import ConfigRepositoryManager, get_config_repository
from synth_codeai.database.pydantic_models import SessionModel # Added for broadcasting
from synth_codeai.env_inv_context import EnvInvManager
from synth_codeai.env_inv import EnvDiscovery
from synth_codeai.llm import initialize_llm, get_model_default_temperature
from synth_codeai.server.broadcast_sender import send_broadcast
from synth_codeai.utils.agent_thread_manager import agent_thread_registry, has_received_stop_signal, register_agent, \
    unregister_agent

# Create logger
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(
    prefix="/v1/spawn-agent",
    tags=["agent"],
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Agent spawn error"},
    },
)

class SpawnAgentRequest(BaseModel):
    '''
    Pydantic model for agent spawn requests.

    This model provides validation for spawning a new agent.

    Attributes:
        message: The message or task for the agent to process
        research_only: Whether to use research-only mode (default: False)
    '''
    message: str = Field(
        description="The message or task for the agent to process"
    )
    research_only: bool = Field(
        default=False,
        description="Whether to use research-only mode"
    )

class SpawnAgentResponse(BaseModel):
    '''
    Pydantic model for agent spawn responses.

    This model defines the response format for the spawn-agent endpoint.

    Attributes:
        session_id: The ID of the created session
    '''
    session_id: int = Field(
        description="The ID of the created session"
    )

def run_agent_thread(
    message: str,
    session_id: int, # Changed to int
    source_config_repo: "ConfigRepository",
    research_only: bool = False,
    **kwargs
):
    '''
    Run a research agent in a separate thread with proper repository initialization.

    Args:
        message: The message or task for the agent to process
        session_id: The ID of the session to associate with this agent (must be int)
        source_config_repo: The source ConfigRepository to copy for this thread
        research_only: Whether to use research-only mode

    Note:
        Values for expert_enabled and web_research_enabled are retrieved from the
        config repository, which stores the values set during server startup.
    '''
    logger = logging.getLogger(__name__)
    # Log entry point information
    logger.info(f"Initializing agent thread for session_id={session_id} (int), research_only={research_only}")

    final_status = 'completed'  # Default final status
    session_repo_instance = None # To hold the repo instance for finally block

    try:
        # Initialize database connection
        db = DatabaseManager()

        env_discovery = EnvDiscovery()
        env_discovery.discover()
        env_data = env_discovery.format_markdown()

        # Get the thread configuration from kwargs
        thread_config = kwargs.get("thread_config", {})

        with DatabaseManager() as db, \
             SessionRepositoryManager(db) as session_repo, \
             KeyFactRepositoryManager(db) as key_fact_repo, \
             KeySnippetRepositoryManager(db) as key_snippet_repo, \
             HumanInputRepositoryManager(db) as human_input_repo, \
             ResearchNoteRepositoryManager(db) as research_note_repo, \
             RelatedFilesRepositoryManager() as related_files_repo, \
             TrajectoryRepositoryManager(db) as trajectory_repo, \
             WorkLogRepositoryManager() as work_log_repo, \
             ConfigRepositoryManager(source_repo=source_config_repo) as config_repo, \
             EnvInvManager(env_data) as env_inv:

            # Log context manager initialization
            logger.debug(f"Context managers initialized for session_id={session_id}")

            session_repo_instance = session_repo # Keep reference for finally block

            # Register broadcast hook for new trajectories
            trajectory_repo.register_create_hook(send_broadcast)

            # Update config repo with values for this thread
            config_repo.set("research_only", research_only)

            # Update config with any thread-specific configurations
            if thread_config:
                config_repo.update(thread_config)

            # ---> Update status to running and broadcast <--- START
            logger.info(f"Updating session {session_id} status to 'running'")
            session_repo.update_session_status(session_id, 'running')
            running_session_model = session_repo.get(session_id)
            if running_session_model:
                send_broadcast({'type': 'session_update', 'payload': running_session_model.model_dump(mode='json')})
                logger.debug(f"Broadcasted session {session_id} status: running")
            else:
                logger.error(f"Could not retrieve session {session_id} after updating status to running.")
            # ---> Update status to running and broadcast <--- END

            # Import here to avoid circular imports
            from synth_codeai.__main__ import run_research_agent

            # Get configuration values from config repository
            provider = config_repo.get("provider", "anthropic")
            model_name = config_repo.get("model", "claude-3-7-sonnet-20250219")
            temperature = kwargs.get("temperature")

            # If temperature is None but model supports it, use the default from model_config
            if temperature is None:
                temperature = get_model_default_temperature(provider, model_name)

            # Get expert_enabled and web_research_enabled from config repository
            expert_enabled = config_repo.get("expert_enabled", True)
            web_research_enabled = config_repo.get("web_research_enabled", False)

            # Initialize model with provider and model name from config
            model = initialize_llm(provider, model_name, temperature=temperature)

            # Set thread_id in config repository too
            thread_id_str = str(session_id) # Keep as string for config
            config_repo.set("thread_id", thread_id_str)
            # Log the retrieved thread_id
            logger.debug(f"Set and retrieved thread_id='{thread_id_str}' from config for session_id={session_id}")

            human_input_id = None # Initialize variable
            try:
                # Log session_id before creation
                logger.debug(f"Creating human input record for session_id={session_id} (int)")
                # Using the repo from the context manager directly
                human_input_record = human_input_repo.create(
                    content=message,
                    source="server",
                    session_id=session_id # Pass integer session_id
                )
                human_input_id = human_input_record.id # Store the ID
                logger.debug(f"Created human input record for session {session_id} with ID {human_input_id}")

                # Create the user query trajectory immediately after human input
                try:
                    if human_input_id is None:
                        logger.warning(f"Attempting to create user_query trajectory for session {session_id} but human_input_id is None. Proceeding anyway.")
                    logger.debug(f"Creating user_query trajectory record for session {session_id}, human_input_id {human_input_id}.")
                    trajectory_repo.create(
                        session_id=session_id,
                        human_input_id=human_input_id,
                        record_type="user_query",
                        step_data={
                            "display_title": "User Query",
                            "query": message,
                        },
                    )

                    logger.info(f"Created user query trajectory for session {session_id}.")
                except Exception as e:
                    logger.exception(f"Error creating user query trajectory for session {session_id}: {e}")

                # --- > BROADCAST SESSION DETAILS UPDATE <--- START
                # Retrieve the full session details *after* human input is added
                # This ensures the display_name is calculated based on the human input.
                updated_session_model = session_repo.get(session_id)
                if updated_session_model:
                    send_broadcast({
                        'type': 'session_details_update', # Use a specific type
                        'payload': updated_session_model.model_dump(mode='json')
                    })
                    logger.info(f"Broadcasted full session details update for session {session_id}")
                else:
                    logger.error(f"Could not retrieve session {session_id} after creating human input for broadcast.")
                # --- > BROADCAST SESSION DETAILS UPDATE <--- END

            except Exception as e:
                # Log error but don't stop the agent thread
                logger.error(f"Failed to create human input record for session {session_id}: {str(e)}")

            # --- > Add Stage Transition Trajectory <--- START
            # This now happens *after* the user_query trajectory
            if human_input_id: # Only proceed if human input was created successfully
                try:
                    logger.debug(f"Creating stage_transition trajectory record for session {session_id}, human_input_id {human_input_id}.")
                    trajectory_repo.create(
                        session_id=session_id,
                        human_input_id=human_input_id,
                        record_type="stage_transition",
                        step_data={"stage": "research_stage", "display_title": "Research Stage"},
                        tool_name=None,
                        tool_parameters=None,
                        tool_result=None,
                        prompt_tokens=None,  # Stage transitions don't involve LLM calls directly
                        response_tokens=None,
                    )
                    logger.info(f"Created research stage transition trajectory for session {session_id}.")
                except Exception as e:
                    logger.exception(f"Error creating stage transition trajectory for session {session_id}: {e}")
            else:
                logger.warning(f"Skipping stage transition trajectory creation for session {session_id} due to missing human_input_id.")
            # --- > Add Stage Transition Trajectory <--- END

            # --- > Agent Execution Logic <--- START
            # Log parameters before calling run_research_agent
            logger.info(f"Starting agent execution for session_id={session_id} with params: "
                        f"base_task_or_query='{message[:50]}...', " # Log first 50 chars
                        f"expert_enabled={expert_enabled}, research_only={research_only}, " 
                        f"web_research_enabled={web_research_enabled}, thread_id='{thread_id_str}'")
            run_research_agent(
                base_task_or_query=message,
                model=model,  # Use the initialized model from config
                expert_enabled=expert_enabled,
                research_only=research_only,
                hil=False,  # No human-in-the-loop for API
                web_research_enabled=web_research_enabled,
                thread_id=thread_id_str, # run_research_agent might expect string thread_id
                session_id=session_id,  # Pass integer session_id
            )
            logger.info(f"Agent execution completed successfully for session {session_id}.")
            # --- > Agent Execution Logic <--- END

    except Exception as e:
        # Use logger.exception to include traceback
        logger.exception(f"Agent thread for session {session_id} encountered an error")
        final_status = 'error'  # Set status to error if exception occurs
    finally:
        # ---> Update status to final state and broadcast <--- START
        if session_repo_instance:

            # Check if we stop due to halt; if so set final_status to 'halted' if not already 'error'
            if final_status != 'error' and has_received_stop_signal(session_id):
                final_status = 'halted'

            # Log before final update
            logger.debug(f"Updating session {session_id} final status to '{final_status}'")
            try:
                session_repo_instance.update_session_status(session_id, final_status)
                final_session_model = session_repo_instance.get(session_id)
                if final_session_model:
                    send_broadcast({'type': 'session_update', 'payload': final_session_model.model_dump(mode='json')})
                    # Log after broadcast confirmation
                    logger.debug(f"Broadcasted session {session_id} final status update: {final_status}")
                else:
                    logger.error(f"Could not retrieve session {session_id} after updating final status.")
            except Exception as final_update_e:
                 logger.error(f"Failed to update/broadcast final status for session {session_id}: {final_update_e}")

            # Unregister the agent thread from the global registry
            unregister_agent(session_id)
        else:
             logger.error(f"Session repository instance not available in finally block for session {session_id}. Cannot update final status.")
        logger.info(f"Agent thread cleanup finished for session {session_id}.")
        # ---> Update status to final state and broadcast <--- END

@router.post(
    "",
    response_model=SpawnAgentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Spawn agent",
    description="Spawn a new synth.codeai agent to process a message or task",
)
async def spawn_agent(
    request: SpawnAgentRequest,
    repo: SessionRepository = Depends(get_session_repository),
) -> SpawnAgentResponse:
    '''
    Spawn a new synth.codeai agent to process a message or task.

    Args:
        request: Request body with message and agent configuration.
        repo: SessionRepository dependency injection

    Returns:
        SpawnAgentResponse: Response with session ID

    Raises:
        HTTPException: With a 500 status code if there's an error spawning the agent
    '''
    try:
        # Get configuration values from config repository
        config_repo = get_config_repository()
        expert_enabled = config_repo.get("expert_enabled", True)
        web_research_enabled = config_repo.get("web_research_enabled", False)
        provider = config_repo.get("provider", "anthropic")
        model_name = config_repo.get("model", "claude-3-7-sonnet-20250219")
        # Get temperature value (or None if not provided)
        temperature = config_repo.get("temperature")

        # If temperature is None, use the model's default temperature
        if temperature is None:
            temperature = get_model_default_temperature(provider, model_name)

        # Create a new session with config values (not request parameters)
        metadata = {
            "agent_type": "research-only" if request.research_only else "research",
            "expert_enabled": expert_enabled,
            "web_research_enabled": web_research_enabled,
            "status": "pending" # Set initial status
        }
        session = repo.create_session(metadata=metadata)
        session_id_int = session.id # Store the integer ID

        # Set the thread_id in the config repository (using string representation)
        config_repo.set("thread_id", str(session_id_int))

        # Get the current config values
        thread_config = {
            "provider": provider,
            "model": model_name,
            "temperature": temperature,
            "expert_enabled": expert_enabled,
            "web_research_enabled": web_research_enabled,
            "thread_id": str(session_id_int),
        }

        # Create stop event for thread termination
        stop_event = threading.Event()

        # Start the agent thread
        thread = threading.Thread(
            target=run_agent_thread,
            args=(
                request.message,
                session_id_int, # Pass the integer ID
                config_repo,
                request.research_only,
            ),
            kwargs={
                "temperature": temperature,
                "thread_config": thread_config,
                "stop_event": stop_event,
            }
        )
        thread.name = str(session_id_int)
        thread.daemon = True  # Thread will terminate when main process exits

        # Register the thread in the global registry
        register_agent(session_id_int, thread, stop_event)

        thread.start()

        # Return the session ID as int
        return SpawnAgentResponse(session_id=session_id_int)
    except Exception as e:
        logger.exception(f"Error spawning agent: {e}") # Use logger.exception for stacktrace
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error spawning agent: {str(e)}",
        )
