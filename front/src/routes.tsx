import * as React from 'react';
import { Route } from 'react-router';
import { BrowserRouter, Switch } from 'react-router-dom';

import PrivateRoute from './components/routes/private';
import Authentication from './components/authentication';
import Search from './components/search';

const Routes = () => (
  <BrowserRouter>
    <Switch>
      <Route path="/login" component={Authentication} />
      <PrivateRoute exact path="/" component={Search} />
    </Switch>
  </BrowserRouter>
);

export default Routes;
