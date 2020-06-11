import * as React from 'react';
import { Route } from 'react-router';
import { BrowserRouter, Switch } from 'react-router-dom';

import PrivateRoute from './components/routes/private';
import Authentication from './components/authentication';
import Search from './components/search';
import DocumentSearch from './components/documents';

const Routes = () => (
  <BrowserRouter basename="/front-api">
    <Switch>
      <Route path="/login" component={Authentication} />
      <PrivateRoute exact path="/" component={Search} />
      <PrivateRoute exact path="/documents" component={DocumentSearch} />
    </Switch>
  </BrowserRouter>
);

export default Routes;
