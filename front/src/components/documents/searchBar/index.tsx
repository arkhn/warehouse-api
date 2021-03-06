import TextField from '@material-ui/core/TextField';
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import Alert from '@material-ui/lab/Alert';
import SearchIcon from '@material-ui/icons/Search';
import Paper from '@material-ui/core/Paper';
import IconButton from '@material-ui/core/IconButton';
import CircularProgress from '@material-ui/core/CircularProgress';
import React, { useCallback, useState } from 'react';
import axios from 'axios';

import { FHIR_API_URL } from '../../../constants';
import { DocumentLink } from '../../../types';

import './style.scss';

interface Props {
  onUpdate: (urls: DocumentLink[]) => void;
}

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    paperForm: {
      margin: '0% 20%',
      padding: '2px 4px',
      display: 'flex',
      alignItems: 'center',
    },
    iconButton: {
      padding: 10,
    },
    alertError: {
      margin: '30px 0px',
    },
  })
);

const SearchBar = ({ onUpdate }: Props): React.ReactElement => {
  const classes = useStyles();

  const [searchText, setSearchText] = useState('');
  const [apiErrors, setApiErrors] = useState([] as string[]);
  const [isLoading, setIsLoading] = useState(false);

  const executeDocumentSearch = useCallback(async () => {
    if (!searchText) return;

    setApiErrors([]);
    onUpdate([]);
    setIsLoading(true);
    let responseBundle: any;
    try {
      const response: any = await axios.get(
        `${FHIR_API_URL}/DocumentReference?$search=${searchText}`
      );
      responseBundle = response.data;
    } catch (err) {
      const errMessage = err.response ? err.response.data : err.message;
      setApiErrors((apiErrors) => [...apiErrors, errMessage]);
    }

    if (responseBundle.total === 0) {
      setApiErrors((apiErrors) => [...apiErrors, 'No document found.']);
    } else {
      onUpdate(
        responseBundle.entry.map((entry: any) => ({
          url: entry.resource.content[0].attachment.url,
          context: entry.resource.description,
        }))
      );
    }
    setIsLoading(false);
  }, [searchText, onUpdate]);

  return (
    <React.Fragment>
      <Paper component="form" elevation={0} className={classes.paperForm}>
        <TextField
          label="Recherche par mot clé"
          placeholder="ex: fumeur, diabete, ..."
          value={searchText}
          fullWidth={true}
          onChange={(event: any) => {
            setSearchText(event.target.value);
          }}
          onKeyPress={(ev) => {
            if (ev.key === 'Enter') {
              ev.preventDefault();
              executeDocumentSearch();
            }
          }}
        />
        <IconButton
          className={classes.iconButton}
          aria-label="search"
          onClick={executeDocumentSearch}
        >
          <SearchIcon />
        </IconButton>
      </Paper>
      {apiErrors.length > 0 &&
        apiErrors.map((apiError) => (
          <Alert severity="error" className={classes.alertError}>
            {`${apiError}`}
          </Alert>
        ))}
      {isLoading && (
        <div className="spinner">
          <CircularProgress />
        </div>
      )}
    </React.Fragment>
  );
};

export default SearchBar;
