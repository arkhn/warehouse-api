import React from 'react';
import { Document, Page, pdfjs } from 'react-pdf';

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;

interface Props {
  pdfUrl: string;
}

const PdfViewer = ({ pdfUrl }: Props): React.ReactElement => {
  return (
    <div>
      <Document
        file={{
          url: `https://pyrog.arkhn.com/files/${pdfUrl.replace(
            'documents/',
            ''
          )}`,
          httpHeaders: { Accept: 'application/pdf' },
        }}
      >
        <Page pageNumber={1} />
      </Document>
    </div>
  );
};

export default PdfViewer;
