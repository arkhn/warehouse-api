import React from 'react';
import axios from 'axios';
import { combineReducers, createStore, applyMiddleware } from 'redux';
import { Provider } from 'react-redux';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage'; // defaults to localStorage for web
import { PersistGate } from 'redux-persist/integration/react';
import { createLogger } from 'redux-logger';

import Routes from './routes';
import {
  searchParametersReducer,
  searchHistoryReducer,
  userReducer,
} from './redux/reducers';
import { logoutUser } from './redux/actions';

import {
  getAccessToken,
  refreshToken,
  removeTokens,
} from './services/tokenManager';
import { FHIR_API_URL, TOKEN_URL } from './constants';
import { ISimpleAction } from './types';

// AXIOS

const redirectToLogin = () => {
  removeTokens();
  store.dispatch(logoutUser() as ISimpleAction);
};

// Interceptor to add authorization header for each requests to the API
axios.interceptors.request.use((config) => {
  if (config.url?.startsWith(FHIR_API_URL!)) {
    const token = getAccessToken();
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add an interceptor to refresh access token when needed
axios.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    if (
      error.response.status === 401 &&
      originalRequest.url.startsWith(TOKEN_URL)
    ) {
      redirectToLogin();
      return Promise.reject(error);
    }

    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const success = await refreshToken();
      if (!success) {
        redirectToLogin();
        return Promise.reject(error);
      }
      return axios(originalRequest);
    }
    return Promise.reject(error);
  }
);

// REDUX
const middlewares = [
  function thunkMiddleware({ dispatch, getState }: any) {
    return function (next: any) {
      return function (action: any) {
        return typeof action === 'function'
          ? action(dispatch, getState)
          : next(action);
      };
    };
  },
];
if (process.env.NODE_ENV === 'development') {
  // Log redux dispatch only in development
  middlewares.push(createLogger({}));
}

const finalCreateStore = applyMiddleware(...middlewares)(createStore);

const mainReducer = combineReducers({
  searchParameters: searchParametersReducer,
  searchHistory: searchHistoryReducer,
  user: userReducer,
});

const persistConfig = {
  key: 'root',
  storage,
};
const persistedReducer = persistReducer(persistConfig, mainReducer);

const store = finalCreateStore(persistedReducer);

export const persistor = persistStore(store);

export default () => (
  <Provider store={store}>
    <PersistGate loading={null} persistor={persistor}>
      <Routes />
    </PersistGate>
  </Provider>
);
