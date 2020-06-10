import React from 'react';
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import ExitToAppIcon from '@material-ui/icons/ExitToApp';
import LibraryBooksIcon from '@material-ui/icons/LibraryBooks';

import useRouter from 'use-react-router';

import { TOKEN_STORAGE_KEY } from '../../constants';

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      flexGrow: 1,
    },
    menuButton: {
      marginRight: theme.spacing(2),
    },
    title: {
      flexGrow: 1,
    },
    logo: {
      maxWidth: 160,
      marginRight: theme.spacing(1),
    },
    icons: {
      margin: '0px 5px 0px 0px',
    },
  })
);

const FrontApiBar = () => {
  const classes = useStyles();

  const { history } = useRouter();

  const logout = () => {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    history.push('/login');
  };

  return (
    <div className={classes.root}>
      <AppBar position="static" style={{ background: '#10161A' }}>
        <Toolbar>
          <img
            src="arkhn_logo_only_white.svg"
            alt="arkhn"
            className={classes.logo}
          />
          <Typography variant="h6" className={classes.title}>
            Search API
          </Typography>
          <IconButton
            color="inherit"
            href="https://www.hl7.org/fhir/search.html"
          >
            <LibraryBooksIcon className={classes.icons} /> {'Doc'}
          </IconButton>
          <IconButton color="inherit" onClick={() => logout()}>
            <ExitToAppIcon className={classes.icons} /> {'Logout'}
          </IconButton>
        </Toolbar>
      </AppBar>
    </div>
  );
};

export default FrontApiBar;
