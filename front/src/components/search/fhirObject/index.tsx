import React, { useState } from 'react';
import ReactJson from 'react-json-view';

export interface Props {
  fhirJson: any;
  title?: string;
}

const FhirObject = ({ fhirJson, title }: Props): React.ReactElement => {
  const [isJsonDisplayed, setIsJsonDisplayed] = useState(false);

  return (
    <div>
      <h2
        className="entry-id"
        onClick={() => setIsJsonDisplayed(!isJsonDisplayed)}
      >
        {`${title || fhirJson.id}`}
      </h2>
      {isJsonDisplayed && (
        <div className="fhir-object-viewer">
          <ReactJson src={fhirJson} name={false} />
        </div>
      )}
    </div>
  );
};

export default FhirObject;
