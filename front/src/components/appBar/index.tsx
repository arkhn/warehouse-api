import React from 'react';
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import ExitToAppIcon from '@material-ui/icons/ExitToApp';
import LibraryBooksIcon from '@material-ui/icons/LibraryBooks';

import { getIdToken, removeTokens } from '../../services/tokenManager';
import { LOGOUT_URL, LOGOUT_REDIRECT_URL } from '../../constants';

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

  const logout = async () => {
    // Hydra logout
    const idToken = getIdToken();
    if (!idToken) throw new Error("Can't logout, id token not found.");
    const logoutUrl = `${LOGOUT_URL}?id_token_hint=${idToken}&post_logout_redirect_uri=${LOGOUT_REDIRECT_URL}`;

    await removeTokens();

    window.location.assign(logoutUrl);
  };

  return (
    <div className={classes.root}>
      <AppBar position="static" style={{ background: '#F9B5ACFF' }}>
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
            target="_blank"
          >
            <LibraryBooksIcon className={classes.icons} />
            {'Doc fhir'}
          </IconButton>
          <IconButton color="inherit" onClick={() => logout()}>
            <ExitToAppIcon className={classes.icons} /> {'Deconnexion'}
          </IconButton>
        </Toolbar>
      </AppBar>
    </div>
  );
};

export default FrontApiBar;
