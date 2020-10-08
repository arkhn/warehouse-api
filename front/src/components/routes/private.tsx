import React, { useCallback, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Route } from 'react-router';
import { Redirect } from 'react-router-dom';
import queryString from 'query-string';
import jwt_decode from 'jwt-decode';

import { createStyles, makeStyles, Theme } from '@material-ui/core';
import CircularProgress from '@material-ui/core/CircularProgress';

import { fetchTokens, removeTokens } from '../../services/tokenManager';
import { updateUser } from '../../redux/actions';
import {
  ACCESS_TOKEN_STORAGE_KEY,
  ID_TOKEN_STORAGE_KEY,
  STATE_STORAGE_KEY,
} from '../../constants';
import { IReduxStore } from '../../types';

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    spinner: {
      textAlign: 'center',
    },
  })
);

const PrivateRoute = ({ component: Component, render, ...rest }: any) => {
  const styles = useStyles();

  const dispatch = useDispatch();
  const user = useSelector((state: IReduxStore) => state.user);

  const params = queryString.parse(window.location.search);

  const accessToken = localStorage.getItem(ACCESS_TOKEN_STORAGE_KEY);
  const storedState = localStorage.getItem(STATE_STORAGE_KEY);
  const stateMatch =
    'code' in params && 'state' in params && params.state === storedState;

  const setLoggedInUser = useCallback(async () => {
    await fetchTokens();

    const idToken = localStorage.getItem(ID_TOKEN_STORAGE_KEY);
    const decodedIdToken: any = jwt_decode(idToken!);

    dispatch(updateUser(decodedIdToken));
  }, [dispatch]);

  useEffect(() => {
    if (stateMatch) {
      setLoggedInUser();
      localStorage.removeItem(STATE_STORAGE_KEY);
    }
  }, [stateMatch, setLoggedInUser]);

  // Redirect to the login page
  if (!user.email && !accessToken) {
    if (stateMatch) {
      // Wait for the code to be exchanged for a token
      return (
        <div className="spinner">
          <CircularProgress className={styles.spinner} />
        </div>
      );
    } else {
      removeTokens();
      return (
        <Route
          render={(props) => (
            <Redirect
              to={{
                pathname: '/login',
                state: { from: props.location },
              }}
            />
          )}
        />
      );
    }
  }

  return <Route {...rest} render={(props) => <Component {...props} />} />;
};

export default PrivateRoute;
