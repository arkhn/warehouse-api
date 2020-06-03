import React from 'react';
import {
  Container,
  Paper,
  createStyles,
  Grid,
  TextField,
  Button,
  makeStyles,
  Theme,
} from '@material-ui/core';
import { Face, Fingerprint } from '@material-ui/icons';
import Alert from '@material-ui/lab/Alert';

import useRouter from 'use-react-router';
import gql from 'graphql-tag';
import { useMutation } from '@apollo/react-hooks';

import { TOKEN_STORAGE_KEY } from '../../constants';

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

const LOGIN = gql`
  mutation login($email: String!, $password: String!) {
    login(email: $email, password: $password) {
      token
    }
  }
`;

const Authentication = () => {
  const styles = useStyles();
  const [username, setUsername] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [loginError, setLoginError] = React.useState('');

  const { history } = useRouter();

  const onCompletedLogin = (data: any) => {
    if (data.login.token) {
      const token = data.login.token;
      localStorage.setItem(TOKEN_STORAGE_KEY, token);
      history.push('/');
    }
  };

  const onErrorLogin = (error: any): void => {
    setLoginError(error.message.replace('GraphQL error:', ''));
  };

  const [mutationLogin] = useMutation(LOGIN, {
    onCompleted: onCompletedLogin,
    onError: onErrorLogin,
  });

  const onLogin = () => {
    mutationLogin({
      variables: {
        email: username,
        password: password,
      },
    });
  };

  return (
    <Container component="main" className={styles.root}>
      <Paper className={styles.padding}>
        <div className={styles.margin}>
          <Grid container spacing={8} alignItems="flex-end">
            <Grid item>
              <Face />
            </Grid>
            <Grid item md={true} sm={true} xs={true}>
              <TextField
                id="username"
                label="Username"
                type="email"
                fullWidth
                autoFocus
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </Grid>
          </Grid>
          <Grid container spacing={8} alignItems="flex-end">
            <Grid item>
              <Fingerprint />
            </Grid>
            <Grid item md={true} sm={true} xs={true}>
              <TextField
                id="username"
                label="Password"
                type="password"
                fullWidth
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </Grid>
          </Grid>
          <Grid container justify="center" style={{ marginTop: '10px' }}>
            <Button
              variant="outlined"
              color="primary"
              style={{ textTransform: 'none' }}
              onClick={onLogin}
            >
              Login
            </Button>
          </Grid>
          {loginError && <Alert severity="error"> {`${loginError}`} </Alert>}
        </div>
      </Paper>
    </Container>
  );
};

export default Authentication;
