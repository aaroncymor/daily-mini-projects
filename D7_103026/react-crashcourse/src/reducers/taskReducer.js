export const initialState = {
  tasks: [
    { id: 1, title: "Review FastAPI Authentication", completed: true },
    { id: 2, title: "Practice React Hooks", completed: false },
  ],
  filter: "ALL", // "ALL", "COMPLETED", "PENDING"
}

// When state logic involves multiple sub-values or complex transitions,
// useReducer is prefrable over multiple useState calls
export function taskReducer(state, action) {
  switch (action.type) {
    case "ADD_TASK":
      return {
        ...state,
        tasks: [
          ...state.tasks,
          {id: Date.now(), title: action.payload, completed: false}
        ],
      };

    case "TOGGLE_TASK":
      return {
        ...state,
        tasks: state.tasks.map((task) =>
          task.id === action.payload
          ? { ...task, completed: !task.completed }
          : task
        ),
      };

    case "DELETE_TASK":
      return {
        ...state,
        tasks: state.tasks.filter((task) => task.id !== action.payload),
      };

    case "SET_FILTER":
      return {
        ...state,
        filter: action.payload,
      };

    default:
      return state;
  }
}
