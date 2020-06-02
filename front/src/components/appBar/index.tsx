import React from 'react';
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';

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
          <Button color="inherit" href="https://www.hl7.org/fhir/search.html">
            Documentation
          </Button>
          <Button color="inherit" onClick={() => logout()}>
            Deconnexion
          </Button>
        </Toolbar>
      </AppBar>
    </div>
  );
};

export default FrontApiBar;
