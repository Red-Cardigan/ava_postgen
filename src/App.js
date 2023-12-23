import React, { useState } from 'react';
import axios from 'axios';
import ContentGenerator from './ContentGenerator';

function App() {
  const [prompt, setPrompt] = useState('');
  const [options, setOptions] = useState({
    blogPost: false,
    twitterThread: false,
    instagramPost: false
  });
  const [responses, setResponses] = useState([]);

  const handlePromptChange = (event) => {
    setPrompt(event.target.value);
  };

  const handleOptionChange = (event) => {
    setOptions({ ...options, [event.target.name]: event.target.checked });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post('/api/generate', { prompt, options });
      setResponses(response.data);
    } catch (error) {
      console.error('Error generating content:', error);
    }
  };

  return (
    <div className="App">
      <h1>Content Generator</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Prompt:
          <input type="text" value={prompt} onChange={handlePromptChange} />
        </label>
        <label>
          Blog Post:
          <input type="checkbox" name="blogPost" checked={options.blogPost} onChange={handleOptionChange} />
        </label>
        <label>
          Twitter Thread:
          <input type="checkbox" name="twitterThread" checked={options.twitterThread} onChange={handleOptionChange} />
        </label>
        <label>
          Instagram Post:
          <input type="checkbox" name="instagramPost" checked={options.instagramPost} onChange={handleOptionChange} />
        </label>
        <button type="submit">Generate</button>
      </form>
      <ContentGenerator responses={responses} />
    </div>
  );
}

export default App;
