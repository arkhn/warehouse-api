import React, { useState } from 'react';
import { makeStyles, Theme, createStyles } from '@material-ui/core/styles';
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import ReactJson from 'react-json-view';

export interface Props {
  fhirJson: any;
}

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      width: '100%',
    },
    heading: {
      fontSize: theme.typography.pxToRem(15),
      flexBasis: '33.33%',
      flexShrink: 0,
    },
    secondaryHeading: {
      fontSize: theme.typography.pxToRem(15),
      color: theme.palette.text.secondary,
    },
  })
);

const FhirObject = ({ fhirJson }: Props): React.ReactElement => {
  const classes = useStyles();

  const [isExpanded, setExpanded] = useState(false);

  return (
    <ExpansionPanel
      expanded={isExpanded}
      onChange={() => setExpanded(!isExpanded)}
    >
      <ExpansionPanelSummary
        expandIcon={<ExpandMoreIcon />}
        aria-controls="panel1bh-content"
        id="panel1bh-header"
      >
        <Typography
          className={classes.heading}
        >{`${fhirJson.resourceType}`}</Typography>
        <Typography className={classes.secondaryHeading}>
          {`Last updated at: ${fhirJson.meta?.lastUpdated || ''}`}
        </Typography>
      </ExpansionPanelSummary>
      <ExpansionPanelDetails>
        <ReactJson src={fhirJson} name={false} />
      </ExpansionPanelDetails>
    </ExpansionPanel>
  );
};

export default FhirObject;
