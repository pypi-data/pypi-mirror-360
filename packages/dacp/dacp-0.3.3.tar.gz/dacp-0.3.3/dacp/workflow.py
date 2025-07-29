"""
DACP Workflow Management - Agent-to-agent communication and task routing.

This module provides workflow orchestration capabilities for multi-agent systems,
including task boards, message routing, and automated agent collaboration.
"""

import logging
import time
import uuid
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("dacp.workflow")


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority enumeration."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Task:
    """Represents a task in the workflow system."""
    id: str
    type: str
    data: Dict[str, Any]
    source_agent: str
    target_agent: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: float = field(default_factory=time.time)
    assigned_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "type": self.type,
            "data": self.data,
            "source_agent": self.source_agent,
            "target_agent": self.target_agent,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at,
            "assigned_at": self.assigned_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error": self.error,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
        }


@dataclass
class WorkflowRule:
    """Defines routing rules for agent-to-agent communication."""
    source_task_type: str
    target_agent: str
    target_task_type: str
    condition: Optional[Callable[[Task], bool]] = None
    transform_data: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
    priority: TaskPriority = TaskPriority.NORMAL


class TaskBoard:
    """Central task board for managing agent-to-agent tasks."""

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.agent_queues: Dict[str, List[str]] = {}
        self.completed_tasks: List[str] = []
        self.workflow_rules: List[WorkflowRule] = []

    def add_task(
        self,
        task_type: str,
        data: Dict[str, Any],
        source_agent: str,
        target_agent: Optional[str] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        dependencies: List[str] = None,
    ) -> str:
        """Add a new task to the board."""
        task_id = str(uuid.uuid4())
        
        task = Task(
            id=task_id,
            type=task_type,
            data=data,
            source_agent=source_agent,
            target_agent=target_agent,
            priority=priority,
            dependencies=dependencies or [],
        )

        self.tasks[task_id] = task

        # Add to appropriate agent queue
        if target_agent:
            if target_agent not in self.agent_queues:
                self.agent_queues[target_agent] = []
            self.agent_queues[target_agent].append(task_id)
            task.status = TaskStatus.ASSIGNED
            task.assigned_at = time.time()

        logger.info(f"📋 Task '{task_id}' added: {task_type} from {source_agent} to {target_agent}")
        return task_id

    def get_next_task(self, agent_name: str) -> Optional[Task]:
        """Get the next task for an agent."""
        if agent_name not in self.agent_queues or not self.agent_queues[agent_name]:
            return None

        # Sort by priority and creation time
        queue = self.agent_queues[agent_name]
        available_tasks = []

        for task_id in queue:
            task = self.tasks[task_id]
            if task.status == TaskStatus.ASSIGNED and self._dependencies_satisfied(task):
                available_tasks.append(task)

        if not available_tasks:
            return None

        # Sort by priority (higher first) then by creation time (older first)
        available_tasks.sort(key=lambda t: (-t.priority.value, t.created_at))
        
        next_task = available_tasks[0]
        next_task.status = TaskStatus.IN_PROGRESS

        logger.info(f"📤 Task '{next_task.id}' assigned to agent '{agent_name}'")
        return next_task

    def complete_task(
        self, 
        task_id: str, 
        result: Dict[str, Any], 
        trigger_rules: bool = True
    ) -> None:
        """Mark a task as completed and trigger workflow rules."""
        if task_id not in self.tasks:
            logger.error(f"❌ Task '{task_id}' not found")
            return

        task = self.tasks[task_id]
        task.status = TaskStatus.COMPLETED
        task.completed_at = time.time()
        task.result = result

        # Remove from agent queue
        if task.target_agent and task.target_agent in self.agent_queues:
            if task_id in self.agent_queues[task.target_agent]:
                self.agent_queues[task.target_agent].remove(task_id)

        self.completed_tasks.append(task_id)

        logger.info(f"✅ Task '{task_id}' completed by agent '{task.target_agent}'")

        # Trigger workflow rules if enabled
        if trigger_rules:
            self._trigger_workflow_rules(task)

    def fail_task(self, task_id: str, error: str) -> None:
        """Mark a task as failed."""
        if task_id not in self.tasks:
            logger.error(f"❌ Task '{task_id}' not found")
            return

        task = self.tasks[task_id]
        task.status = TaskStatus.FAILED
        task.completed_at = time.time()
        task.error = error

        # Remove from agent queue
        if task.target_agent and task.target_agent in self.agent_queues:
            if task_id in self.agent_queues[task.target_agent]:
                self.agent_queues[task.target_agent].remove(task_id)

        logger.error(f"❌ Task '{task_id}' failed: {error}")

    def add_workflow_rule(self, rule: WorkflowRule) -> None:
        """Add a workflow rule for automatic task routing."""
        self.workflow_rules.append(rule)
        logger.info(
            f"🔄 Workflow rule added: {rule.source_task_type} → "
            f"{rule.target_agent} ({rule.target_task_type})"
        )

    def _dependencies_satisfied(self, task: Task) -> bool:
        """Check if all task dependencies are satisfied."""
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                return False
            dep_task = self.tasks[dep_id]
            if dep_task.status != TaskStatus.COMPLETED:
                return False
        return True

    def _trigger_workflow_rules(self, completed_task: Task) -> None:
        """Trigger workflow rules based on completed task."""
        for rule in self.workflow_rules:
            if rule.source_task_type == completed_task.type:
                # Check condition if specified
                if rule.condition and not rule.condition(completed_task):
                    continue

                # Transform data if specified
                if rule.transform_data and completed_task.result:
                    new_data = rule.transform_data(completed_task.result)
                else:
                    new_data = completed_task.result or {}

                # Create new task
                new_task_id = self.add_task(
                    task_type=rule.target_task_type,
                    data=new_data,
                    source_agent=completed_task.target_agent or completed_task.source_agent,
                    target_agent=rule.target_agent,
                    priority=rule.priority,
                )

                logger.info(
                    f"🔄 Workflow rule triggered: {completed_task.id} → {new_task_id}"
                )

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status and details."""
        if task_id not in self.tasks:
            return None
        return self.tasks[task_id].to_dict()

    def get_agent_queue_status(self, agent_name: str) -> Dict[str, Any]:
        """Get status of an agent's task queue."""
        if agent_name not in self.agent_queues:
            return {"agent": agent_name, "queue_length": 0, "tasks": []}

        queue = self.agent_queues[agent_name]
        task_details = []

        for task_id in queue:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task_details.append({
                    "id": task_id,
                    "type": task.type,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "created_at": task.created_at,
                })

        return {
            "agent": agent_name,
            "queue_length": len(queue),
            "tasks": task_details,
        }

    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get overall workflow summary."""
        status_counts = {}
        for task in self.tasks.values():
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_tasks": len(self.tasks),
            "status_counts": status_counts,
            "agent_queues": {
                agent: len(queue) for agent, queue in self.agent_queues.items()
            },
            "completed_tasks": len(self.completed_tasks),
            "workflow_rules": len(self.workflow_rules),
        }


class WorkflowOrchestrator:
    """Enhanced orchestrator with workflow and agent-to-agent communication."""

    def __init__(self, orchestrator):
        """Initialize with a base orchestrator."""
        self.orchestrator = orchestrator
        self.task_board = TaskBoard()
        self.auto_processing = False
        self._processing_interval = 1.0  # seconds

    def enable_auto_processing(self, interval: float = 1.0) -> None:
        """Enable automatic task processing."""
        self.auto_processing = True
        self._processing_interval = interval
        logger.info(f"🤖 Auto-processing enabled (interval: {interval}s)")

    def disable_auto_processing(self) -> None:
        """Disable automatic task processing."""
        self.auto_processing = False
        logger.info("⏸️  Auto-processing disabled")

    def submit_task_for_agent(
        self,
        source_agent: str,
        target_agent: str,
        task_type: str,
        task_data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> str:
        """Submit a task from one agent to another."""
        return self.task_board.add_task(
            task_type=task_type,
            data=task_data,
            source_agent=source_agent,
            target_agent=target_agent,
            priority=priority,
        )

    def process_agent_tasks(self, agent_name: str, max_tasks: int = 1) -> List[Dict[str, Any]]:
        """Process available tasks for an agent."""
        if agent_name not in self.orchestrator.agents:
            logger.error(f"❌ Agent '{agent_name}' not registered")
            return []

        results = []
        tasks_processed = 0

        while tasks_processed < max_tasks:
            task = self.task_board.get_next_task(agent_name)
            if not task:
                break

            try:
                # Convert task to agent message format
                # Only include the task type and the actual task data
                message = {
                    "task": task.type,
                    **task.data,
                }

                # Send to agent
                response = self.orchestrator.send_message(agent_name, message)

                if "error" in response:
                    self.task_board.fail_task(task.id, response["error"])
                    results.append({"task_id": task.id, "status": "failed", "error": response["error"]})
                else:
                    self.task_board.complete_task(task.id, response)
                    results.append({"task_id": task.id, "status": "completed", "result": response})

                tasks_processed += 1

            except Exception as e:
                error_msg = f"Task processing failed: {e}"
                self.task_board.fail_task(task.id, error_msg)
                results.append({"task_id": task.id, "status": "failed", "error": error_msg})
                tasks_processed += 1

        return results

    def add_workflow_rule(
        self,
        source_task_type: str,
        target_agent: str,
        target_task_type: str,
        condition: Optional[Callable[[Task], bool]] = None,
        transform_data: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> None:
        """Add a workflow rule for automatic task chaining."""
        rule = WorkflowRule(
            source_task_type=source_task_type,
            target_agent=target_agent,
            target_task_type=target_task_type,
            condition=condition,
            transform_data=transform_data,
            priority=priority,
        )
        self.task_board.add_workflow_rule(rule)

    def get_workflow_status(self) -> Dict[str, Any]:
        """Get comprehensive workflow status."""
        return {
            "orchestrator": {
                "session_id": self.orchestrator.session_id,
                "registered_agents": list(self.orchestrator.agents.keys()),
                "auto_processing": self.auto_processing,
            },
            "task_board": self.task_board.get_workflow_summary(),
            "agent_queues": {
                agent: self.task_board.get_agent_queue_status(agent)
                for agent in self.orchestrator.agents.keys()
            },
        } 