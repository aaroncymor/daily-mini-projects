import { useReducer, useMemo, useCallback } from 'react';
import { taskReducer, initialState } from '../reducers/taskReducer';

export function TaskManager() {
  const [state, dispatch] = useReducer(taskReducer, initialState);

  // MEMOIZATION 1: useMemo caches heavy or filtered array computaitons
  const filteredTasks = useMemo(() => {
    if (state.filter === 'COMPLETED') return state.tasks.filter(t => t.completed);
    if (state.filter === 'PENDING') return state.tasks.filter(t => !t.completed);
    return state.tasks;
  }, [state.tasks, state.filter]);

  // MEMOIZATION 2: useCallback caches function references passed to child components
  const handleToggle = useCallback((id) => {
    dispatch({ type: 'TOGGLE_TASK', payload: id });
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <button onClick={() => dispatch({ type: 'SET_FILTER', payload: 'ALL'})}>All</button>
        <button onClick={() => dispatch({ type: 'SET_FILTER', payload: 'PENDING'})}>Pending</button>
        <button onClick={() => dispatch({ type: 'SET_FILTER', payload: 'COMPLETED'})}>Completed</button>
      </div>
      <ul className="space-y-2">
        {filteredTasks.map((task) => (
          <li key={task.id} className="flext justify-between items-center p-2 border rounded">
            <span
              onClick={() => handleToggle(task.id)}
              className={task.completed ? "line-through cursor-pointer text-gray-400": "cursor-pointer"}
            >
              {task.title}
            </span>
            <button
              onClick={
                () => dispatch(
                  { type: 'DELETE_TASK', payload: task.id}
                )
              }
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
