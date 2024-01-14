import React, { useState } from 'react';
import axios from 'axios';
import ContentGenerator from './ContentGenerator';
import { Button, Form, FormGroup, FormControl, FormCheck, Container } from 'react-bootstrap';
import { toast } from 'react-toastify';
import './App.css';
// import { NOTES_1_FT, NOTES_2, TITLE_TAGS_FT, BLOG_FT, INSTAGRAM, TWITTER } from './prompts.js';

function App() {
  const [prompt, setPrompt] = useState('');
  const [source, setSource] = useState(null);
  const [options, setOptions] = useState({
    blogPost: false,
    twitterThread: false,
    instagramPost: false
  });
  // const [responses, setResponses] = useState([]);
  const [response, setResponses] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const handlePromptChange = (event) => {
    setPrompt(event.target.value);
  };

  const handleOptionChange = (event) => {
    setOptions({ ...options, [event.target.name]: event.target.checked });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    if (source) {
      source.close();
  }
  let newSource = new EventSource(`http://127.0.0.1:8000/stream?prompt=${encodeURIComponent(prompt)}`);
  newSource.onmessage = function(event) {
      let data = JSON.parse(event.data);
      if (data.notes || data.refined_notes) {
        // Add a 'showButton' property to the data
        data.showButton = true;
    }
      setResponses(prevResponses => ({...prevResponses, ...data}));
  };
  newSource.onerror = function(err) {
    console.error("EventSource failed:", err);
};
  setSource(newSource);
};

// Close the SSE connection when the component is unmounted
React.useEffect(() => {
  return () => {
      if (source) {
          source.close();
      }
  };
}, [source]);

const handleRestart = () => {
  if (source) {
      source.close();
  }
  let newSource = new EventSource(`http://127.0.0.1:5000/stream?prompt=${encodeURIComponent(prompt)}`);
  newSource.onmessage = function(event) {
      let data = JSON.parse(event.data);
      if (data.notes) {
          data.showButton = true;
      }
      setResponses(prevResponses => prevResponses.concat(data));
  };
  setSource(newSource);
};

const handleStop = () => {
  if (source) {
      source.close();
  }
  setSource(null);
};

      // ############### NEXT ################
      //############### 2 BUTTONS APPEAR BELOW RESPONSE TEXT - RESTART AND STOP ###########
      // SHOW 'REFINING...' TEXT INDICATOR
      //############### AUTOMATICALLY CREATE NEW THREAD MESSAGE(S) IN APP.PY TO REFINE THE POST ###############
      // RETURN REFINED NOTES + SUGGESTED TITLES BELOW FIRST RESPONSE
      //############### PROVIDE FINAL OPTIONS BEFORE CREATING FINAL POST ############
      // CHECKBOXES TO SELECT 1) FAVOURITE TITLE(S), 2) CONTEXT FROM LOCAL POSTGRES DATABASE, 3) AREAS FOR RESEARCH
      // RETURN FINISHED POST WITH TITLE + DESCRIPTION





      //############### POST ON SUBSTACK ########
      // GENERATE IMAGES 
      // GENERATE HTML https://simonwillison.net/2023/Apr/4/substack-observable/
      //############### POST ELSEWHERE ##############

            // Fourth API call
      // let outputOptions = [];
      // if (options.blogPost) outputOptions.push('blog post');
      // if (options.twitterThread) outputOptions.push('Twitter thread');
      // if (options.instagramPost) outputOptions.push('Instagram post');

      // response = await axios.post('http://localhost:5000/api/generate', { 
      //   prompt: BLOG_FT.replace('{title}', titleTagsResponse.title)
      //                   .replace('{description}', titleTagsResponse.description)
      //                   .replace('{tags}', titleTagsResponse.tags)
      //                   .replace('{NOTES_2_response}', NOTES_2_response), 
      //   model: 'gpt-3.5-turbo-1106',
      //   output_options: outputOptions
      // });
      // let finalResponse = response.data;

  return (
    <Container className="App container">
      <h1 className="header">Ava Blog & Social Media Post Generator</h1>
      <Form onSubmit={handleSubmit}>
        <FormGroup>
          <Form.Label><i className="fas fa-blog"></i> Provide Notes On...</Form.Label>
          <FormControl aria-label="Prompt input" type="text" value={prompt} onChange={handlePromptChange} />
        </FormGroup>
        <FormGroup className="form-group custom-checkbox">
          <div>
            <Form.Label><i className="fas fa-blog"></i> Generated Responses = Notes + Selection Below</Form.Label>
          </div>
          <div>
            <Form.Check type="checkbox" label="Blog Post" name="blogPost" checked={options.blogPost} onChange={handleOptionChange} />
            <Form.Check type="checkbox" label="Twitter Thread" name="twitterThread" checked={options.twitterThread} onChange={handleOptionChange} />
            <Form.Check type="checkbox" label="Instagram Post" name="instagramPost" checked={options.instagramPost} onChange={handleOptionChange} />
          </div>
          </FormGroup>
        {isLoading ? <p>Loading...</p> : <Button className="button" variant="primary" type="submit">Generate</Button>}
      </Form>
      <Button variant="success" className="button save-button">
        {/* <CSVLink
          data={csvData}
          filename={`output_${options.blogPost ? 'blog' : ''}${options.twitterThread ? 'twitter' : ''}${options.instagramPost ? 'instagram' : ''}_${new Date().toISOString()}.csv`}
          style={{ color: 'inherit', textDecoration: 'inherit' }} // inherit styles from Button
        >
          Save
        </CSVLink> */}
        Save
      </Button>
      <div className="content">
        <ContentGenerator responses={response} />
      </div>
    </Container>
  );
}

export default App;