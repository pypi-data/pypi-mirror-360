from typing import List, Generic, TypeVar
from .models import TaskPlan, ExecutionWaves
from .worker_manager import WorkerManager

# Define generic type variables
InputT = TypeVar('InputT')
OutputT = TypeVar('OutputT')
StateT = TypeVar('StateT')


class WaveManager(Generic[InputT, OutputT]):
    def __init__(self, worker_manager: WorkerManager[InputT, OutputT]):
        self.worker_manager = worker_manager
    
    def create_execution_waves(self, task_plans: List[TaskPlan]) -> ExecutionWaves:
        """
        Creates execution waves from task plans by organizing tasks by node
        and distributing them across parallel execution waves.
        """
        print(f"task_plans: {task_plans}")
        tasks_per_nodes = self.worker_manager.get_tasks_per_nodes(task_plans)
        print(f"tasks_per_nodes: {tasks_per_nodes}")
        # Check if any tasks were actually assigned to workers
        total_assigned_tasks = sum(len(tasks) for tasks in tasks_per_nodes.values())
        if total_assigned_tasks == 0:
            print(f"❌ ERROR: No tasks assigned to any workers!")
            print(f"❌ ERROR: This usually means worker names don't match task node_allocated values")
            return ExecutionWaves()
        
        more_task_node_name = max(tasks_per_nodes, key=lambda x: len(tasks_per_nodes[x]))
        execution_waves = ExecutionWaves()
        max_tasks = len(tasks_per_nodes[more_task_node_name])
        print(f"max_tasks: {max_tasks}")
        for wave_num in range(max_tasks):
            for node in tasks_per_nodes:
                if len(tasks_per_nodes[node]) > wave_num:
                    task_plan = tasks_per_nodes[node][wave_num]
                    if wave_num not in execution_waves.waves:
                        execution_waves.waves[wave_num] = []
                    execution_waves.waves[wave_num].append(task_plan)
        print(f"execution_waves: {execution_waves}")
        return execution_waves
    
    def is_waves_complete(self, state: StateT) -> bool:
        return state.current_wave == len(state.execution_waves.waves)
    
    def get_current_wave_tasks(self, state: StateT) -> List[TaskPlan]:
        return state.execution_waves.waves[state.current_wave] 