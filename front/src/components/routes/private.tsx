import * as React from 'react';
import { Route } from 'react-router';
import { Redirect } from 'react-router-dom';

import { TOKEN_STORAGE_KEY } from '../../constants';

const PrivateRoute = ({ component: Component, render, ...rest }: any) => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);

  if (!token)
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

  return <Route {...rest} render={(props) => <Component {...props} />} />;
};

export default PrivateRoute;
