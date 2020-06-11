import React, { useState } from 'react';

import AppBar from '../appBar';
import DocumentResults from './searchResults';
import PdfViewer from './pdfViewer';
import SearchBar from './searchBar';

import { DocumentLink } from '../../types';

import './style.scss';

const DocumentSearch = (): React.ReactElement => {
  const [documentLinks, setDocumentLinks] = useState([] as DocumentLink[]);
  const [selectedPdf, setSelectedPdf] = useState('');

  return (
    <React.Fragment>
      <AppBar />
      <div className="search-documents">
        <SearchBar
          onUpdate={(documentLinks) => {
            setDocumentLinks(documentLinks);
            setSelectedPdf('');
          }}
        />
        <div className="results-div">
          <div className="all-results">
            <DocumentResults
              documentLinks={documentLinks}
              onSelect={setSelectedPdf}
            />
          </div>
          <div className="pdf-preview">
            {selectedPdf && <PdfViewer pdfUrl={selectedPdf} />}
          </div>
        </div>
      </div>
    </React.Fragment>
  );
};

export default DocumentSearch;
