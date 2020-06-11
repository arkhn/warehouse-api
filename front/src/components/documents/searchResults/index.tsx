import React from 'react';
import { makeStyles, createStyles, Theme } from '@material-ui/core/styles';
import Link from '@material-ui/core/Link';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';

import { DocumentLink } from '../../../types';

interface Props {
  documentLinks: DocumentLink[];
  onSelect: (url: string) => void;
}

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    linkHover: {
      '&:hover': { cursor: 'pointer' },
    },
  })
);

const DocumentResults = ({
  documentLinks,
  onSelect,
}: Props): React.ReactElement => {
  const classes = useStyles();
  const renderResult = (documentLink: DocumentLink): React.ReactElement => {
    return (
      <ListItem alignItems="flex-start">
        <ListItemText
          primary={
            <Link
              className={classes.linkHover}
              onClick={() => onSelect(documentLink.url)}
            >
              {documentLink.url}
            </Link>
          }
          secondary={documentLink.context}
        />
      </ListItem>
    );
  };

  return <List>{documentLinks.map(renderResult)}</List>;
};

export default DocumentResults;
