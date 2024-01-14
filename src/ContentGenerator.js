import React from 'react';
import ReactMarkdown from 'react-markdown';

function ContentGenerator({ responses, handleRestart, handleStop }) {
  return (
    <div className="ContentGenerator">
      <h2>Generated Content</h2>
      <div className="tabs">
          <div className="tab">
            <h3>Initial Notes</h3>
            <ReactMarkdown>
              {responses.notes && responses.notes.join('\n')}
            </ReactMarkdown>
            {responses.refined_notes && (
              <>
                <h3>Refined Notes</h3>
                <ReactMarkdown>
                  {responses.refined_notes.join('\n')}
                </ReactMarkdown>
              </>
            )}
            {responses.showButton && (
              <>
                <button onClick={handleRestart}>Restart</button>
                <button onClick={handleStop}>Stop</button>
              </>
            )}
          </div>
        {responses.blogPost && (
          <div className="tab">
            <h3>Blog Post</h3>
            <p>{responses.blogPost}</p>
          </div>
        )}
        {responses.twitterThread && (
          <div className="tab">
            <h3>Twitter Thread</h3>
            <p>{responses.twitterThread}</p>
          </div>
        )}
        {responses.instagramPost && (
          <div className="tab">
            <h3>Instagram Post</h3>
            <p>{responses.instagramPost}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default ContentGenerator;
