import { ISimpleAction } from '../types';

const initialState: any = [
  { parameter: { name: '', expression: '' }, value: '' },
];

export const searchParametersReducer = (
  state = initialState,
  action: ISimpleAction
): any => {
  switch (action.type) {
    case 'UPDATE_PARAMETER': {
      state[action.payload.index] = {
        parameter: action.payload.parameter || { name: '', expression: '' },
        value: action.payload.value,
      };
      return [...state];
    }

    case 'ADD_PARAMETER': {
      state = [
        ...state,
        { parameter: { name: '', expression: '' }, value: '' },
      ];
      return [...state];
    }

    case 'DELETE_PARAMETER': {
      state.splice(action.payload.index, 1);
      if (state.length === 0) {
        state = [{ parameter: { name: '', expression: '' }, value: '' }];
      }
      return [...state];
    }

    default:
      return state;
  }
};

export default searchParametersReducer;
