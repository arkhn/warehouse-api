import React, { useEffect, useState } from 'react';
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';

import { Link, useLocation } from 'react-router-dom';

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      margin: '20px 20px',
    },
    tabTitle: {
      minWidth: 0,
    },
  })
);

const SwitchViews = () => {
  const classes = useStyles();

  const { pathname } = useLocation();

  useEffect(() => {
    setSelectedTab(pathname?.substr(1) || 'api');
  }, [pathname]);

  const [selectedTab, setSelectedTab] = useState('api');

  return (
    <div className={classes.root}>
      <Tabs value={selectedTab} textColor="primary" centered>
        <Tab
          className={classes.tabTitle}
          label="API"
          value="api"
          component={Link}
          to={`/`}
        />
        <Tab
          className={classes.tabTitle}
          label="Documents"
          value="documents"
          component={Link}
          to={`/documents`}
        />
      </Tabs>
    </div>
  );
};

export default SwitchViews;
