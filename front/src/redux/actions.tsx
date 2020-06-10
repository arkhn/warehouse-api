import { IAction, SearchParameter } from '../types';

export const updateParameter = (
  index: number,
  parameter: SearchParameter | null,
  value: string
): IAction => {
  return {
    type: 'UPDATE_PARAMETER',
    payload: {
      index,
      parameter,
      value,
    },
  };
};

export const addParameter = (): IAction => {
  return {
    type: 'ADD_PARAMETER',
  };
};

export const deleteParameter = (index: number): IAction => {
  return {
    type: 'DELETE_PARAMETER',
    payload: {
      index,
    },
  };
};