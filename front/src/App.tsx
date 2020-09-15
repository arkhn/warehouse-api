import React from 'react';
import axios from 'axios';
import { ApolloProvider } from 'react-apollo';
import { HttpLink, InMemoryCache, ApolloClient } from 'apollo-client-preset';
import { ApolloLink } from 'apollo-link';
import { onError } from 'apollo-link-error';
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
} from './redux/reducers';

import { AUTH_API_URL, TOKEN_STORAGE_KEY } from './constants';

// AXIOS

// Interceptor to add authorization header for each requests
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// APOLLO

// HttpLink
const httpLink = new HttpLink({
  uri: AUTH_API_URL,
  fetch: fetch,
});

const middlewareLink = new ApolloLink((operation, forward) => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);

  operation.setContext({
    headers: {
      Authorization: token ? `Bearer ${token}` : '',
    },
  });

  return forward(operation);
});

const httpLinkAuth = middlewareLink.concat(httpLink);

const errorLink = onError(({ graphQLErrors, networkError }) => {
  if (graphQLErrors)
    graphQLErrors.map(({ message, locations, path }) =>
      console.log(
        `[GraphQL error]: Message: ${message}, Location: ${locations}, Path: ${path}`
      )
    );

  if (networkError) console.log(`[Network error]: ${networkError}`);
});

// Aggregate all links
const links = [];
if (process.env.NODE_ENV === 'development') {
  links.push(errorLink);
}

links.push(httpLinkAuth);

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
});

const persistConfig = {
  key: 'root',
  storage,
};
const persistedReducer = persistReducer(persistConfig, mainReducer);

const store = finalCreateStore(persistedReducer);

export const persistor = persistStore(store);

// Client
export const client = new ApolloClient({
  cache: new InMemoryCache(),
  connectToDevTools: true,
  link: ApolloLink.from(links),
});

export default () => (
  <Provider store={store}>
    <PersistGate loading={null} persistor={persistor}>
      <ApolloProvider client={client}>
        <Routes />
      </ApolloProvider>
    </PersistGate>
  </Provider>
);
