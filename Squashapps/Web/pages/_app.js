import App, { Container } from 'next/app';
import React from "react";

// import "../public/scss/styles.scss"
// import "../public/css/nucleo-icons.css";
import 'react-datasheet/lib/react-datasheet.css';
import "../public/css/main.css";
// import "../public/css/ems.css";
// import MyLoading from "../components/MyLoading"
import Router from 'next/router'
import 'react-times/css/material/default.css';
import 'react-times/css/classic/default.css';
import 'rc-time-picker/assets/index.css';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import 'react-image-crop/dist/ReactCrop.css';
import '../pages/web_login/index.js'

class MyApp extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoading:false
    };
    this.ShowLoading.bind(this)
  }
  componentDidMount () {
    this.ShowLoading();   
      Router.push('/web_login')    
  }
  ShowLoading(){
    Router.onRouteChangeStart = () => {
      this.setState({isLoading:true})
    };
    
    Router.onRouteChangeComplete = () => {
       setTimeout(() => {
          this.setState({isLoading:false})
       }, 1000);
    };
    
    Router.onRouteChangeError = () => {
      this.setState({isLoading:false})
    };
  }
  render() {
    const { Component, pageProps} = this.props;
    return (
      <Container>        
        <Component {...pageProps} />
      </Container>
    );
  }
}

export default MyApp