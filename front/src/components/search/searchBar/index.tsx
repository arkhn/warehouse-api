import TextField from '@material-ui/core/TextField';
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import Autocomplete from '@material-ui/lab/Autocomplete';
import SearchIcon from '@material-ui/icons/Search';
import Paper from '@material-ui/core/Paper';
import IconButton from '@material-ui/core/IconButton';
import HistoryIcon from '@material-ui/icons/History';

import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';

import { FHIR_API_URL } from '../../../constants';
import { IReduxStore } from '../../../types';

import '../style.scss';

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    paperForm: {
      padding: '2px 4px',
      display: 'flex',
      alignItems: 'center',
      width: '100%',
    },
    iconButton: {
      padding: 10,
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

type Props = {
  selectedCollection: string;
  executeFhirQuery: (query: string) => void;
};

const SearchBar = ({
  selectedCollection,
  executeFhirQuery,
}: Props): React.ReactElement => {
  const classes = useStyles();

  const { searchParameters, searchHistory } = useSelector(
    (state: IReduxStore) => state
  );

  const [fhirUrl, setFhirUrl] = useState('');

  useEffect(() => {
    const searchUrl = searchParameters
      .filter((param) => param.parameter && param.value)
      .map((param) => `${param.parameter}=${param.value}`);
    setFhirUrl(
      `${FHIR_API_URL}${selectedCollection ? '/' + selectedCollection : ''}${
        searchUrl.length > 0 ? '?' + searchUrl.join('&') : ''
      }`
    );
  }, [selectedCollection, searchParameters]);

  return (
    <Paper component="form" elevation={0} className={classes.paperForm}>
      <Autocomplete
        options={searchHistory}
        size="small"
        freeSolo={true}
        fullWidth={true}
        renderInput={(params) => <TextField {...params} />}
        forcePopupIcon={true}
        popupIcon={<HistoryIcon />}
        value={fhirUrl}
        onChange={(_: any, value: string | null) => setFhirUrl(value || '')}
        onInputChange={(_: any, value: string | null) =>
          setFhirUrl(value || '')
        }
        ListboxProps={{
          className: classes.searchBarDropdown,
        }}
        onKeyPress={(ev) => {
          if (ev.key === 'Enter') {
            ev.preventDefault();
            executeFhirQuery(fhirUrl);
          }
        }}
      />
      <IconButton
        className={classes.iconButton}
        aria-label="search"
        onClick={() => executeFhirQuery(fhirUrl)}
      >
        <SearchIcon />
      </IconButton>
    </Paper>
  );
};

export default SearchBar;
