import TextField from '@material-ui/core/TextField';
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import Autocomplete from '@material-ui/lab/Autocomplete';
import IconButton from '@material-ui/core/IconButton';
import AddIcon from '@material-ui/icons/Add';
import DeleteIcon from '@material-ui/icons/Delete';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableRow from '@material-ui/core/TableRow';

import React from 'react';
import { useSelector, useDispatch } from 'react-redux';

import { IReduxStore, SearchParameter } from '../../../types';
import {
  addParameter,
  deleteParameter,
  updateParameter,
} from '../../../redux/actions';

import * as bundleSearchParameters from '../../../fhir/search-parameters.json';

const parametersPerType = new Map<string, SearchParameter[]>();

bundleSearchParameters.entry.forEach((entry) => {
  const resource = entry.resource;
  if (resource.type === 'string' && resource.expression) {
    const keys = resource.base || ['__common__'];
    keys.forEach((key) =>
      parametersPerType.set(key, [
        ...(parametersPerType.get(key) || []),
        { name: resource.name, expression: resource.expression },
      ])
    );
  }
});

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    table: {
      minWidth: 700,
      margin: '30px 0px',
      borderSpacing: '0',
    },
    row: {
      borderBottom: 'none',
      paddingTop: '5px',
      paddingBottom: '5px',
    },
  })
);

const RenderRow = ({ index, type }: any) => {
  const classes = useStyles();

  const searchParameters = useSelector(
    (state: IReduxStore) => state.searchParameters
  );
  const dispatch = useDispatch();

  return (
    <TableRow key={index}>
      <TableCell className={classes.row}>
        {index === searchParameters.length - 1 && (
          <IconButton onClick={() => dispatch(addParameter())}>
            <AddIcon />
          </IconButton>
        )}
      </TableCell>
      <TableCell align="right" className={classes.row}>
        <Autocomplete
          options={parametersPerType.get(type) || []}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Search parameter"
              variant="outlined"
            />
          )}
          getOptionLabel={(option) => option.name}
          getOptionSelected={(option, value) => option.name === value.name}
          value={searchParameters[index].parameter}
          onChange={(_: any, newValue: SearchParameter | null) => {
            dispatch(
              updateParameter(index, newValue, searchParameters[index].value)
            );
          }}
        />
      </TableCell>
      <TableCell align="center" className={classes.row}>
        <TextField
          value={searchParameters[index].value}
          onChange={(event: any) => {
            dispatch(
              updateParameter(
                index,
                searchParameters[index].parameter,
                event.target.value
              )
            );
          }}
        />
      </TableCell>
      <TableCell className={classes.row}>
        <IconButton onClick={() => dispatch(deleteParameter(index))}>
          <DeleteIcon />
        </IconButton>
      </TableCell>
    </TableRow>
  );
};

const SearchParameterTable = ({ type }: any) => {
  const classes = useStyles();
  const searchParameters = useSelector(
    (state: IReduxStore) => state.searchParameters
  );

  return (
    <div>
      <Table
        className={classes.table}
        aria-label="customized table"
        key="table"
      >
        <TableBody key="tableBody">
          {Array.from(Array(searchParameters.length).keys()).map((index) => (
            <RenderRow
              index={index}
              value={searchParameters[index].value}
              type={type}
            />
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default SearchParameterTable;
