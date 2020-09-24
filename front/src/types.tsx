import redux from 'redux';

export interface User {
  name: string;
  email: string;
}

// REDUX
export interface ISimpleAction {
  type: string;
  payload?: any;
}

export type IThunkAction = (
  dispatch: redux.Dispatch<any>,
  getState: any
) => void;

export type IAction = ISimpleAction | IThunkAction | Promise<any>;

export interface IReduxStore {
  searchParameters: ParameterValue[];
  searchHistory: string[];
  user: User;
}

export interface ParameterValue {
  parameter: string;
  value: string;
}

export interface DocumentLink {
  url: string;
  context: string;
}
