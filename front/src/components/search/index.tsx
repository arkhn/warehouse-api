import Button from '@material-ui/core/Button';
import Select from '@material-ui/core/Select';
import TextField from '@material-ui/core/TextField';
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import Alert from '@material-ui/lab/Alert';
import SearchIcon from '@material-ui/icons/Search';

import axios from 'axios';
import React, { useEffect, useState } from 'react';

import FhirObject from './fhirObject';
import AppBar from '../appBar';

import { FHIR_API_URL } from '../../constants';

import './style.scss';

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      '& > *': {
        margin: theme.spacing(1),
        width: '25ch',
      },
      display: 'flex',
    },
  })
);

const Search = (): React.ReactElement => {
  const classes = useStyles();

  const [searchParameters, setSearchParameters] = useState('');
  const [fhirCollections, setFhirCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState('');
  const [fhirBundle, setFhirBundle] = useState({} as any);
  const [apiError, setApiError] = useState(false);

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

  const executeFhirQuery = async () => {
    const fhirUrl = `${FHIR_API_URL}${
      selectedCollection ? '/' + selectedCollection : ''
    }?${searchParameters}`;

    try {
      const response: any = await axios.get(fhirUrl);
      setFhirBundle(response.data);
    } catch (err) {
      const errMessage = err.response ? err.response.data : err.message;
      setApiError(errMessage);
    }
  };

  return (
    <React.Fragment>
      <AppBar />
      <div className="search-view">
        <div className="search-bar">
          <form className={classes.root}>
            <Select
              native
              onChange={(c) => setSelectedCollection(c.target.value as string)}
            >
              <option value="">Search on all collections</option>
              {fhirCollections.map((collection) => (
                <option value={collection}>{`${collection}`}</option>
              ))}
            </Select>
            <TextField
              label="search parameters"
              onChange={(event: React.FormEvent<HTMLElement>) => {
                const target = event.target as HTMLInputElement;
                setSearchParameters(target.value);
              }}
            />
            <Button
              className="search-button"
              variant="contained"
              color="default"
              startIcon={<SearchIcon />}
              onClick={executeFhirQuery}
            />
          </form>
          {apiError && <Alert severity="error"> {`${apiError}`} </Alert>}
        </div>
        {fhirBundle.entry && (
          <div>
            {`Found ${fhirBundle.total} results`}
            {fhirBundle.entry.map((entry: any, index: number) => (
              <FhirObject
                fhirJson={entry.resource}
                title={`result ${index + 1}`}
                key={`result ${index + 1}`}
              />
            ))}
          </div>
        )}
      </div>
    </React.Fragment>
  );
};

export default Search;
