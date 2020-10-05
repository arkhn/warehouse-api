import { ISimpleAction, User } from '../types';
import { HISTORY_SEARCH_SIZE } from '../constants';

const searchParametersInitialState: any = [{ parameter: '', value: '' }];

export const searchParametersReducer = (
  state = searchParametersInitialState,
  action: ISimpleAction
): any => {
  switch (action.type) {
    case 'UPDATE_PARAMETER': {
      state[action.payload.index] = {
        parameter: action.payload.parameter || '',
        value: action.payload.value,
      };
      return [...state];
    }

    case 'ADD_PARAMETER': {
      state = [...state, { parameter: '', value: '' }];
      return [...state];
    }

    case 'DELETE_PARAMETER': {
      state.splice(action.payload.index, 1);
      if (state.length === 0) {
        state = [{ parameter: '', value: '' }];
      }
      return [...state];
    }

    default:
      return state;
  }
};

const searchHistoryInitialState: any = [];

export const searchHistoryReducer = (
  state = searchHistoryInitialState,
  action: ISimpleAction
): any => {
  switch (action.type) {
    case 'NEW_QUERY': {
      // if the history the empty, return the first search
      if (state.length === 0) return [action.payload];

      // if the search is the same as the previous one, do not update the state
      const [lastQuery] = state;
      if (lastQuery === action.payload) return state;

      // otherwise, insert the last search on top of the history queue
      return [action.payload, ...state].slice(0, HISTORY_SEARCH_SIZE);
    }

    default:
      return state;
  }
};

const userInitialState: User = { name: '', email: '' };

export const userReducer = (
  state = userInitialState,
  action: ISimpleAction
): any => {
  switch (action.type) {
    case 'UPDATE_USER': {
      return { ...action.payload };
    }

    case 'LOGOUT': {
      return { ...userInitialState };
    }

    default:
      return state;
  }
};
