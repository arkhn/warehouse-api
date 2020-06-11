import TextField from '@material-ui/core/TextField';
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import Alert from '@material-ui/lab/Alert';
import Autocomplete from '@material-ui/lab/Autocomplete';
import SearchIcon from '@material-ui/icons/Search';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import Box from '@material-ui/core/Box';
import CircularProgress from '@material-ui/core/CircularProgress';

import axios from 'axios';
import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';

import FhirObject from './fhirObject';
import AppBar from '../appBar';
import SearchParameterTable from './searchParameterTable';

import { FHIR_API_URL } from '../../constants';
import { IReduxStore } from '../../types';

import './style.scss';

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    resourceSelect: {
      margin: '30px 0px',
      width: '60%',
    },
    paperForm: {
      padding: '2px 4px',
      display: 'flex',
      alignItems: 'center',
      width: '100%',
    },
    iconButton: {
      padding: 10,
    },
    alertError: {
      margin: '30px 0px',
    },
    searchButton: {
      float: 'right',
    },
  })
);

const Search = (): React.ReactElement => {
  const classes = useStyles();

  const searchParameters = useSelector(
    (state: IReduxStore) => state.searchParameters
  );

  const [fhirCollections, setFhirCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState('');
  const [fhirBundle, setFhirBundle] = useState({} as any);
  const [apiErrors, setApiErrors] = useState([] as string[]);
  const [fhirUrl, setfFhirUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const getFhirCollections = async () => {
    try {
      const response: any = await axios.get(`${FHIR_API_URL}/list-collections`);
      setFhirCollections(response.data);
    } catch (err) {
      const errMessage = err.response ? err.response.data : err.message;
      console.debug(errMessage);
    }
  };

  useEffect(() => {
    getFhirCollections();
  }, []);

  useEffect(() => {
    const searchUrl = searchParameters
      .map((param) => {
        let { expression } = param.parameter;
        if (!expression || !param.value) return '';
        // Remove |
        expression = expression.split(' |')[0];
        const path = expression.substring(expression.indexOf('.') + 1);
        return `${path}=${param.value}`;
      })
      .filter(Boolean);
    setfFhirUrl(
      `${FHIR_API_URL}${selectedCollection ? '/' + selectedCollection : ''}${
        searchUrl.length > 0 ? '?' + searchUrl.join('&') : ''
      }`
    );
  }, [selectedCollection, searchParameters]);

  const executeFhirQuery = async () => {
    setApiErrors([]);
    setFhirBundle([]);
    setIsLoading(true);
    let responseBundle: any;
    try {
      const response: any = await axios.get(fhirUrl);
      responseBundle = response.data;
    } catch (err) {
      const errMessage = err.response ? err.response.data : err.message;
      setApiErrors((apiErrors) => [...apiErrors, errMessage]);
    }

    if (responseBundle.issue) {
      setApiErrors((apiErrors) => [
        ...apiErrors,
        responseBundle.issue.diagnostic,
      ]);
    } else {
      responseBundle.entry.forEach((entry: any) => {
        if (entry.resource.issue) {
          setApiErrors((apiErrors) => [
            ...apiErrors,
            entry.resource.issue.details,
          ]);
        }
      });
      responseBundle.entry = responseBundle.entry.filter(
        (entry: any) => !entry.resource.issue
      );
      setFhirBundle(responseBundle);
    }
    setIsLoading(false);
  };

  return (
    <React.Fragment>
      <AppBar />
      <div className="search-view">
        <div className="search-bar">
          <Autocomplete
            key="test"
            className={classes.resourceSelect}
            options={[
              { label: 'No type', value: '' },
              ...fhirCollections.map((collection) => ({
                label: collection,
                value: collection,
              })),
            ]}
            getOptionLabel={(option) => option.label}
            getOptionSelected={(option: any, value: any) =>
              option.value === value.value
            }
            renderInput={(params) => (
              <TextField {...params} label="Resource type" variant="outlined" />
            )}
            onChange={(_: any, newValue: any) => {
              setSelectedCollection(newValue?.value || '');
            }}
          />
          <SearchParameterTable type={selectedCollection} />
          {/* <Paper component="form" elevation={0} className={classes.paperForm}>
            <TextField
              value={fhirUrl}
              fullWidth={true}
              onChange={(event: any) => {
                setfFhirUrl(event.target.value);
              }}
              onKeyPress={(ev) => {
                if (ev.key === 'Enter') {
                  ev.preventDefault();
                  executeFhirQuery();
                }
              }}
            />
            <IconButton
              className={classes.iconButton}
              aria-label="search"
              onClick={executeFhirQuery}
            >
              <SearchIcon />
            </IconButton>
          </Paper> */}
          <Button
            className={classes.searchButton}
            aria-label="search"
            variant="contained"
            onClick={executeFhirQuery}
          >
            <SearchIcon />
          </Button>
          {apiErrors.length > 0 &&
            apiErrors.map((apiError) => (
              <Alert severity="error" className={classes.alertError}>
                {`${apiError}`}
              </Alert>
            ))}
        </div>
        {isLoading && (
          <div className="spinner">
            <CircularProgress />
          </div>
        )}
        {fhirBundle.entry && (
          <div>
            <Typography paragraph>
              <Box
                fontWeight="fontWeightLight"
                fontStyle="italic"
                color="text.secondary"
                m={1}
              >
                {`Found ${fhirBundle.total} result(s)`}
              </Box>
            </Typography>
            {fhirBundle.entry.map((entry: any, index: number) => (
              <FhirObject fhirJson={entry.resource} key={index} />
            ))}
          </div>
        )}
      </div>
    </React.Fragment>
  );
};

export default Search;
