import React from 'react';
import {
  Container,
  Paper,
  createStyles,
  Grid,
  Button,
  makeStyles,
  Theme,
} from '@material-ui/core';

import { v4 as uuid } from 'uuid';

import { authClient } from '../../oauth/index';
import { STATE_STORAGE_KEY } from '../../constants';

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      height: 'inherit',
      display: 'flex',
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      marginTop: '100px',
    },
    margin: {
      margin: theme.spacing(2),
    },
    padding: {
      padding: theme.spacing(1),
    },
  })
);

const Authentication = () => {
  const styles = useStyles();

  const startAuthentication = () => {
    const state = uuid();
    localStorage.setItem(STATE_STORAGE_KEY, state);
    const uri = authClient.code.getUri({
      state: state,
    });
    window.location.assign(uri);
  };

  return (
    <Container component="main" className={styles.root}>
      <Paper className={styles.padding}>
        <div className={styles.margin}>
          <Grid container justify="center" style={{ marginTop: '10px' }}>
            <Button
              variant="outlined"
              color="primary"
              style={{ textTransform: 'none' }}
              onClick={startAuthentication}
            >
              Login with Arkhn
            </Button>
          </Grid>
        </div>
      </Paper>
    </Container>
  );
};

export default Authentication;
