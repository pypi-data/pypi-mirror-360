"""
DACP Workflow Runtime - Declarative workflow execution from workflow.yaml

This module provides a runtime system that reads workflow.yaml files and
orchestrates agent collaboration through agent and task registries.
"""

import logging
import time
import uuid
import yaml
import json
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("dacp.workflow_runtime")


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskExecution:
    """Represents a task execution instance."""
    id: str
    workflow_id: str
    step_id: str
    agent_id: str
    task_name: str
    input_data: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    duration: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "step_id": self.step_id,
            "agent_id": self.agent_id,
            "task_name": self.task_name,
            "input_data": self.input_data,
            "status": self.status.value,
            "output_data": self.output_data,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration": self.duration,
        }


@dataclass
class RegisteredAgent:
    """Represents a registered agent in the registry."""
    id: str
    agent_instance: Any
    spec_file: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: float = field(default_factory=time.time)
    last_activity: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "agent_type": type(self.agent_instance).__name__,
            "spec_file": self.spec_file,
            "metadata": self.metadata,
            "registered_at": self.registered_at,
            "last_activity": self.last_activity,
        }


class AgentRegistry:
    """Registry for managing agent instances."""

    def __init__(self):
        self.agents: Dict[str, RegisteredAgent] = {}

    def register_agent(
        self, 
        agent_id: str, 
        agent_instance: Any, 
        spec_file: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register an agent instance."""
        registered_agent = RegisteredAgent(
            id=agent_id,
            agent_instance=agent_instance,
            spec_file=spec_file,
            metadata=metadata or {}
        )
        
        self.agents[agent_id] = registered_agent
        logger.info(f"🤖 Agent '{agent_id}' registered in registry")

    def get_agent(self, agent_id: str) -> Optional[Any]:
        """Get an agent instance by ID."""
        if agent_id in self.agents:
            self.agents[agent_id].last_activity = time.time()
            return self.agents[agent_id].agent_instance
        return None

    def list_agents(self) -> List[str]:
        """List all registered agent IDs."""
        return list(self.agents.keys())

    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent registration information."""
        if agent_id in self.agents:
            return self.agents[agent_id].to_dict()
        return None

    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"🗑️ Agent '{agent_id}' unregistered from registry")
            return True
        return False


class TaskRegistry:
    """Registry for managing task executions."""

    def __init__(self):
        self.tasks: Dict[str, TaskExecution] = {}
        self.workflow_tasks: Dict[str, List[str]] = {}  # workflow_id -> task_ids

    def create_task(
        self,
        workflow_id: str,
        step_id: str,
        agent_id: str,
        task_name: str,
        input_data: Dict[str, Any]
    ) -> str:
        """Create a new task execution."""
        task_id = str(uuid.uuid4())
        
        task = TaskExecution(
            id=task_id,
            workflow_id=workflow_id,
            step_id=step_id,
            agent_id=agent_id,
            task_name=task_name,
            input_data=input_data
        )
        
        self.tasks[task_id] = task
        
        # Add to workflow tasks
        if workflow_id not in self.workflow_tasks:
            self.workflow_tasks[workflow_id] = []
        self.workflow_tasks[workflow_id].append(task_id)
        
        logger.info(f"📋 Task '{task_id}' created for agent '{agent_id}' in workflow '{workflow_id}'")
        return task_id

    def get_task(self, task_id: str) -> Optional[TaskExecution]:
        """Get a task by ID."""
        return self.tasks.get(task_id)

    def update_task_status(self, task_id: str, status: TaskStatus, **kwargs) -> bool:
        """Update task status and optional fields."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = status
        
        # Update optional fields
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        # Calculate duration if completed
        if status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and task.started_at:
            task.completed_at = time.time()
            task.duration = task.completed_at - task.started_at
        
        logger.info(f"📊 Task '{task_id}' status updated to {status.value}")
        return True

    def get_workflow_tasks(self, workflow_id: str) -> List[TaskExecution]:
        """Get all tasks for a workflow."""
        task_ids = self.workflow_tasks.get(workflow_id, [])
        return [self.tasks[tid] for tid in task_ids if tid in self.tasks]

    def get_task_summary(self) -> Dict[str, Any]:
        """Get summary of all tasks."""
        status_counts = {}
        for task in self.tasks.values():
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_tasks": len(self.tasks),
            "status_counts": status_counts,
            "workflows": len(self.workflow_tasks)
        }


class WorkflowRuntime:
    """DACP Workflow Runtime - Executes workflows from workflow.yaml"""

    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator
        self.agent_registry = AgentRegistry()
        self.task_registry = TaskRegistry()
        self.workflow_config = {}
        self.active_workflows: Dict[str, Dict[str, Any]] = {}

    def load_workflow_config(self, config_path: str) -> None:
        """Load workflow configuration from YAML file."""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Workflow config file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            self.workflow_config = yaml.safe_load(f)
        
        logger.info(f"📁 Loaded workflow config from {config_path}")
        logger.info(f"📋 Found {len(self.workflow_config.get('workflows', {}))} workflows")

    def register_agent_from_config(self, agent_id: str, agent_instance: Any) -> None:
        """Register an agent instance based on workflow config."""
        # Find agent spec in config
        agent_spec = None
        for agent_config in self.workflow_config.get('agents', []):
            if agent_config['id'] == agent_id:
                agent_spec = agent_config.get('spec')
                break
        
        self.agent_registry.register_agent(
            agent_id=agent_id,
            agent_instance=agent_instance,
            spec_file=agent_spec,
            metadata={"config_based": True}
        )

    def execute_workflow(self, workflow_name: str, initial_input: Dict[str, Any] = None) -> str:
        """Execute a workflow by name."""
        if workflow_name not in self.workflow_config.get('workflows', {}):
            raise ValueError(f"Workflow '{workflow_name}' not found in config")
        
        workflow_def = self.workflow_config['workflows'][workflow_name]
        workflow_id = str(uuid.uuid4())
        
        logger.info(f"🚀 Starting workflow '{workflow_name}' with ID '{workflow_id}'")
        
        # Initialize workflow state
        self.active_workflows[workflow_id] = {
            "name": workflow_name,
            "definition": workflow_def,
            "current_step": 0,
            "context": initial_input or {},
            "started_at": time.time()
        }
        
        # Execute first step
        self._execute_workflow_step(workflow_id, 0)
        
        return workflow_id

    def _execute_workflow_step(self, workflow_id: str, step_index: int) -> None:
        """Execute a specific workflow step."""
        if workflow_id not in self.active_workflows:
            logger.error(f"❌ Workflow '{workflow_id}' not found")
            return
        
        workflow_state = self.active_workflows[workflow_id]
        workflow_def = workflow_state["definition"]
        steps = workflow_def.get("steps", [])
        
        if step_index >= len(steps):
            logger.info(f"🏁 Workflow '{workflow_id}' completed")
            return
        
        step = steps[step_index]
        step_id = f"step_{step_index}"
        
        # Extract step configuration
        agent_id = step.get("agent")
        task_name = step.get("task")
        step_input = step.get("input", {})
        
        # Resolve input data with context
        resolved_input = self._resolve_input_data(step_input, workflow_state["context"])
        
        logger.info(f"📋 Executing step {step_index}: {agent_id}.{task_name}")
        
        # Create task
        task_id = self.task_registry.create_task(
            workflow_id=workflow_id,
            step_id=step_id,
            agent_id=agent_id,
            task_name=task_name,
            input_data=resolved_input
        )
        
        # Execute task
        self._execute_task(task_id, workflow_id, step_index)

    def _execute_task(self, task_id: str, workflow_id: str, step_index: int) -> None:
        """Execute a single task."""
        task = self.task_registry.get_task(task_id)
        if not task:
            logger.error(f"❌ Task '{task_id}' not found")
            return
        
        # Get agent instance
        agent = self.agent_registry.get_agent(task.agent_id)
        if not agent:
            self.task_registry.update_task_status(
                task_id, TaskStatus.FAILED, 
                error=f"Agent '{task.agent_id}' not found"
            )
            return
        
        # Update task status
        self.task_registry.update_task_status(
            task_id, TaskStatus.RUNNING, 
            started_at=time.time()
        )
        
        try:
            # Prepare message for agent
            message = {
                "task": task.task_name,
                **task.input_data
            }
            
            logger.info(f"📨 Sending task '{task.task_name}' to agent '{task.agent_id}'")
            
            # Execute via orchestrator or direct call
            if self.orchestrator:
                result = self.orchestrator.send_message(task.agent_id, message)
            else:
                result = agent.handle_message(message)
            
            # Check for errors
            if isinstance(result, dict) and "error" in result:
                self.task_registry.update_task_status(
                    task_id, TaskStatus.FAILED,
                    error=result["error"]
                )
                logger.error(f"❌ Task '{task_id}' failed: {result['error']}")
                return
            
            # Task completed successfully
            self.task_registry.update_task_status(
                task_id, TaskStatus.COMPLETED,
                output_data=result
            )
            
            logger.info(f"✅ Task '{task_id}' completed successfully")
            
            # Continue workflow
            self._handle_task_completion(task_id, workflow_id, step_index, result)
            
        except Exception as e:
            self.task_registry.update_task_status(
                task_id, TaskStatus.FAILED,
                error=str(e)
            )
            logger.error(f"❌ Task '{task_id}' failed with exception: {e}")

    def _handle_task_completion(self, task_id: str, workflow_id: str, step_index: int, result: Dict[str, Any]) -> None:
        """Handle task completion and route to next step."""
        workflow_state = self.active_workflows[workflow_id]
        workflow_def = workflow_state["definition"]
        steps = workflow_def.get("steps", [])
        
        if step_index >= len(steps):
            return
        
        current_step = steps[step_index]
        
        # Convert result to dictionary if it's a Pydantic model
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump()
            logger.debug(f"🔧 Converted Pydantic model to dict: {result_dict}")
        elif hasattr(result, 'dict'):
            result_dict = result.dict()
            logger.debug(f"🔧 Converted Pydantic model to dict (legacy): {result_dict}")
        else:
            result_dict = result
        
        # Update workflow context with result
        workflow_state["context"].update({"output": result_dict})
        
        # Check for routing
        route_config = current_step.get("route_output_to")
        if route_config:
            # Route to next agent
            next_agent_id = route_config.get("agent")
            next_task_name = route_config.get("task")
            input_mapping = route_config.get("input_mapping", {})
            
            logger.debug(f"🔍 Input mapping: {input_mapping}")
            logger.debug(f"🔍 Available output data: {result_dict}")
            
            # Resolve input mapping
            next_input = self._resolve_input_mapping(input_mapping, result_dict, workflow_state["context"])
            
            logger.info(f"🔄 Routing output to {next_agent_id}.{next_task_name}")
            logger.debug(f"🔍 Resolved input for next task: {next_input}")
            
            # Create and execute next task
            next_task_id = self.task_registry.create_task(
                workflow_id=workflow_id,
                step_id=f"routed_step_{step_index}",
                agent_id=next_agent_id,
                task_name=next_task_name,
                input_data=next_input
            )
            
            self._execute_task(next_task_id, workflow_id, step_index + 1)
        else:
            # Continue to next step
            self._execute_workflow_step(workflow_id, step_index + 1)

    def _resolve_input_data(self, input_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve input data with context variables."""
        resolved = {}
        for key, value in input_config.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Template variable
                var_path = value[2:-2].strip()
                resolved[key] = self._get_nested_value(context, var_path)
            else:
                resolved[key] = value
        return resolved

    def _resolve_input_mapping(self, mapping: Dict[str, str], output: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve input mapping with output and context."""
        resolved = {}
        for target_key, source_template in mapping.items():
            if isinstance(source_template, str) and source_template.startswith("{{") and source_template.endswith("}}"):
                var_path = source_template[2:-2].strip()
                if var_path.startswith("output."):
                    # From current output
                    field_name = var_path[7:]  # Remove "output."
                    resolved[target_key] = output.get(field_name, "")
                else:
                    # From context
                    resolved[target_key] = self._get_nested_value(context, var_path)
            else:
                resolved[target_key] = source_template
        return resolved

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get nested value from dictionary using dot notation."""
        keys = path.split('.')
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow execution status."""
        if workflow_id not in self.active_workflows:
            return None
        
        workflow_state = self.active_workflows[workflow_id]
        tasks = self.task_registry.get_workflow_tasks(workflow_id)
        
        return {
            "workflow_id": workflow_id,
            "name": workflow_state["name"],
            "current_step": workflow_state["current_step"],
            "started_at": workflow_state["started_at"],
            "context": workflow_state["context"],
            "tasks": [task.to_dict() for task in tasks]
        }

    def get_runtime_status(self) -> Dict[str, Any]:
        """Get overall runtime status."""
        return {
            "agents": {
                "registered": len(self.agent_registry.agents),
                "agents": [agent.to_dict() for agent in self.agent_registry.agents.values()]
            },
            "tasks": self.task_registry.get_task_summary(),
            "workflows": {
                "active": len(self.active_workflows),
                "configured": len(self.workflow_config.get('workflows', {}))
            }
        } 