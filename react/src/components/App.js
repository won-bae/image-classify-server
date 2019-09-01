import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Route, Redirect, withRouter, Switch } from 'react-router-dom'

import { Body } from './Styled'
import fetch from "cross-fetch"
import { Form, Button } from 'react-bootstrap'

// const Home = () => <Async load={import('./Home')} />

class App extends React.Component {
  state = {
    images: [],
    resultUrl: null
  };

  constructor(props) {
    super(props);
    this.onFileUpload = this.onFileUpload.bind(this);
    this.onFileSelected = this.onFileSelected.bind(this);
  }

  async onFileUpload(event) {
    event.preventDefault();

    let url = `http://medici01.snu.vision:8000/classify_image/classify/api/`;

    let form = new FormData();
    form.append("image64", JSON.stringify(this.state.images));

    let response = await fetch(url, {
      method: "post",
      body: form
    });
    let jsonResponse = await response.json();

    this.setState({ resultUrl: jsonResponse.url });
  }

  onFileSelected(event) {
    let files = event.target.files;
    for (let i = 0; i < files.length; i++) {
      let reader = new FileReader();
      reader.onload = () => {
        let images = this.state.images;
        images.push(reader.result);
        this.setState({ images: images });
      }
      reader.readAsDataURL(files[i]);
    }
  }

  render() {
    return <Body>
      <Form>
        <Form.Group controlId="images">
          <Form.Label>Upload Images</Form.Label>
          <Form.Control type="file" placeholder="Upload your files" multiple onChange={this.onFileSelected} />
          <Form.Text>
            Upload multiple pictures at once.
          </Form.Text>
        </Form.Group>
        <Button variant="primary" type="submit" onClick={this.onFileUpload}>
          Upload
        </Button>
      </Form>
      { this.state.resultUrl ?
      <div>
        Result available for download: <a href={this.state.resultUrl} target="_blank" download>{this.state.resultUrl}</a>
      </div> : "" }
    </Body>
  }
}


App.propTypes = {
  user: PropTypes.shape({}).isRequired,
}

export default withRouter(connect(state => ({ user: state.user }))(App))
