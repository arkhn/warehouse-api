import TextField from '@material-ui/core/TextField';
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import Alert from '@material-ui/lab/Alert';
import Autocomplete from '@material-ui/lab/Autocomplete';
import Typography from '@material-ui/core/Typography';
import Box from '@material-ui/core/Box';
import CircularProgress from '@material-ui/core/CircularProgress';

import axios from 'axios';
import React, { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';

import AppBar from '../appBar';
import SwitchViews from '../switchViews';
import FhirObject from './fhirObject';
import SearchParameterTable from './searchParameterTable';
import SearchBar from './searchBar';
import { newQuery } from '../../redux/actions';

import { FHIR_API_URL } from '../../constants';

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
    searchBarDropdown: {
      listStyle: 'none',
      margin: 0,
      padding: '8px 0',
      overflow: 'auto',
      maxHeight: '11rem',
    },
  })
);

const Search = (): React.ReactElement => {
  const classes = useStyles();

  const dispatch = useDispatch();

  const [fhirCollections, setFhirCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState('');
  const [fhirBundle, setFhirBundle] = useState({} as any);
  const [apiErrors, setApiErrors] = useState([] as string[]);
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

  const executeFhirQuery = async (fhirUrl: string) => {
    dispatch(newQuery(fhirUrl));
    setApiErrors([]);
    setFhirBundle([]);
    setIsLoading(true);
    let responseBundle: any;
    try {
      const url = new URL(fhirUrl);
      url.search = encodeURIComponent(url.search.substring(1));
      const response: any = await axios.get(url.toString());
      responseBundle = response.data;
    } catch (err) {
      const errMessage = err.response ? err.response.data : err.message;
      setApiErrors([errMessage]);
      setIsLoading(false);
      return;
    }

    if (responseBundle.issue) {
      setApiErrors(responseBundle.issue.map((i: any) => i.diagnostics));
    } else {
      responseBundle.entry.forEach((entry: any) => {
        if (entry.resource.issue) {
          setApiErrors(entry.resource.issue.map((i: any) => i.details));
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
        <SwitchViews />
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
          <SearchBar
            selectedCollection={selectedCollection}
            executeFhirQuery={executeFhirQuery}
          />
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
