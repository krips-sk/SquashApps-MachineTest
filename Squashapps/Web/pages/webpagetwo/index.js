import React from 'react';
import Router from 'next/router';
// import Imagge from '../../public/img/downlo.png'
// import "../../public/img";
import $ from 'jquery';



export default class ClaimProcessing extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      errrrcmpy: 0,
      errrrjob: 0,
      upload_img: ""

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
    Router.push('/web_login')
  }

  moveNextPage() {
    try {
      var company = ($('#cmpy_name').val());
      var email = $('#email').val();
      var Job = ($('#Job').val());
      var experience = $('#experience').val();

      if (company != "" && Job != "") {
        Router.push('/web_OTP')
      }
      else if (company != "") {
        this.setState({ errrrcmpy: 1 })

      }
      else if (Job != "") {
        this.setState({ errrrjob: 1 })
      }
      else {
        this.setState({ errrrcmpy: 1, errrrjob: 1 })
      }

    }
    catch (e) {
      console.log(e)
    }
  }
  imgHandler=(e)=>{
    const reader = new FileReader();
    reader.onload = () =>{
      if(reader.readyState == 2){
        this.setState({ upload_img: reader.result})
      }
    }
    reader.readAsDataURL(e.target.files[0])
  }
 
  render() {
    return (
      <div className="firstpagebox">
        <div className="cmpyheading">
          <h2>Add your Company details</h2>
        </div>
        <div className="sub">
          <label>Lorum ipsum is simply dummy text of the printing and typesetting industry</label>
        </div>

        <div className="component">
          <div className="labelcss">
            <div className="imgdiv">
              <div className="coverimg" onChange={this.imgHandler} style={{ backgroundImage: `url(${this.state.upload_img ? this.state.upload_img :"https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png" })` }}>
                <input className="uploadfile" type="file" ></input>
              </div>
            </div>
            <label className="uploadlable" style={{ color: "#ed5901" }}>Upload your company logo</label>
          </div>


          <div className="labelcss">
            <label style={{ color: (this.state.errrrcmpy == 1 ? "#ed5901" : "grey") }}>Company name</label>
            <div>
              <input className="inputcss" id="cmpy_name" type="text" style={{ borderColor: (this.state.errrrcmpy == 1 ? "#ed5901" : "") }}></input>
            </div>
          </div>

          <div className="labelcss">
            <label style={{ color: (this.state.errrrname == 1 ? "#ed5901" : "grey") }}>Email ID</label>
            <div>
              <input className="inputcss" id="email" type="email" ></input>
            </div>
          </div>

          <div className="labelcss">
            <label style={{ color: (this.state.errrrjob == 1 ? "#ed5901" : "grey") }}>Job title</label>
            <div>
              <input className="inputcss" id="Job" type="text" style={{ borderColor: (this.state.errrrjob == 1 ? "#ed5901" : "") }}></input>
            </div>
          </div>

          <div className="labelcss">
            <label style={{ color: "grey" }}>Year Of Experience</label>
            <div>
              <input className="inputcss" id="experience" type="text" ></input>
            </div>
          </div>



          <div className="labelcss">
            <input style={{ verticalAlign: "middle" }} type="checkbox"></input>
            <label className="termscss">I accept the <span style={{ color: "#ed5901" }}>Terms and Conditions</span></label>
          </div>
          <div className="labelcss">
            <button className="backbutton" onClick={() => this.moveprePage()}>Back</button>
            <button className="OTPbutton" onClick={() => this.moveNextPage()}>Send OTP</button>
          </div>
        </div>
      </div>
    )
  }

}