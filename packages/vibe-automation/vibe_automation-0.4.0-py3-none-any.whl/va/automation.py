from va.store import Store, ExecutionStore

import os
import json


class Workflow:
    name: str

    def __init__(self, workflow_name: str):
        pass

    def get_credential(self, provider: str):
        pass


class WorkflowExecution:
    store: ExecutionStore
    execution_id: str
    input: any

    def __init__(self, store: ExecutionStore, execution_id: str):
        self.store = store
        self.execution_id = execution_id

    def get_input(self):
        if os.environ.get("VA_INPUT"):
            return json.loads(os.environ.get("VA_INPUT"))
        return self.store.get_execution_input(self.execution_id)

    def mark_step_executing(self, step: str):
        self.store.mark_step_executing(self.execution_id, step)

    def mark_step_executed(self, step: str):
        self.store.mark_step_executed(self.execution_id, step)

    def mark_start(self):
        self.store.mark_start(self.execution_id)

    def mark_stop(self):
        self.store.mark_stop(self.execution_id)


class Automation:
    store: Store
    execution_id: str
    workflow: Workflow = None
    execution: WorkflowExecution = None

    def __init__(self, store, workflow_name: str, execution_id: str):
        self.execution_id = execution_id
        self.store = store
        self.workflow = Workflow(workflow_name)
        self.execution = WorkflowExecution(self.store, execution_id)

    _instance = None

    @classmethod
    def get_instance(cls) -> "Automation":
        if cls._instance is None:
            raise RuntimeError(
                "VibeAutomation instance has not been initialized, make sure the workflow function is wrapped in the @workflow decorator."
            )
        return cls._instance

    @classmethod
    def set_instance(cls, instance: "Automation"):
        if cls._instance is not None:
            raise RuntimeError("VibeAutomation instance has already been initialized")
        cls._instance = instance
