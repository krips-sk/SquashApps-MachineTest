import React from 'react';
import Router from 'next/router';
import $ from 'jquery';



export default class ClaimProcessing extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      errrrcmpy: 0,
      errrrjob: 0,


    };

  }

  isNumber(evt) {
    evt = (evt) ? evt : window.event;
    var charCode = (evt.which) ? evt.which : evt.keyCode;
    if ((charCode > 31 && (charCode < 48 || charCode > 57)) && charCode !== 46) {
      evt.preventDefault();;
    } else {
      return true;
    }
  }
  moveprePage() {
    Router.push('/webpagetwo')
  }

  moveNextPage() {
    try {
      alert('OTP Verified Successfully')

    }
    catch (e) {
      console.log(e)
    }
  }

  render() {
    return (
      <div className="firstpagebox" style={{height:" 663px !important"}}>
        <div className="otpheading">
          <h2>Enter Your OTP</h2>
        </div>
        <div className="sub">
          <label className="otplable">For your security, we need to verify your identity. We sent a 5-digit code to name@gmail.com. Please enter it below.</label>
        </div>

        <div className="component p-0">
          <div className="otpcomponent">
            <label>Enter your code</label>
            <div>
              <input className="otpinput" maxlength="1"></input>
              <input className="otpinput" maxlength="1"></input>
              <input className="otpinput" maxlength="1"></input>
              <input className="otpinput" maxlength="1"></input>
              <input className="otpinput" maxlength="1"></input>
            </div>
          </div>

          <div className="labelcss">
            <button className="backbutton" onClick={() => this.moveprePage()}>Back</button>
            <button className="OTPbutton" onClick={() => this.moveNextPage()}>Verify</button>
          </div>
          <div className="footerotp">
            <lable >Didn't recevie your mail? Check your spam and filter for an email from <span style={{ color:"#ed5901"}}>name@domin.com</span></lable>
          </div>
        </div>
      </div>
    )
  }

}