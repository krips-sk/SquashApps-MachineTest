import React from 'react';
import '../webpagetwo/index'
import  Router  from 'next/router';
import "../_app"
import $ from 'jquery';



export default class ClaimProcessing extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      errrrname:0,
      errrrcntry:0,
      errrrstate:0,
      errrrphone:0,
      errrrgender:0,

      gender:"",
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

  handle(number){
    if(number==1){
      this.setState({ gender: "Male"})
    }
    else if(number==2){
      this.setState({ gender: "Fe-Male"})
    }
    else if(number==3){
      this.setState({ gender: "Others"})
    }

  }
  moveNextPage(){
    try {
      var fullname= ( $('#full_name').val() );
      var gender= ( this.state.gender!=""? this.state.gender: "" );
      var country= ( $('#Country').val()!=0? ( $('#Country').val()==1?"India":($('#Country').val()==2?"Taiwan":"Others") ):"" );
      var state= ( $('#State').val()!=0? ( $('#State').val()==1?"Tamil Nadu":($('#State').val()==2?"Karnataka":"Others") ):""  );
      var phone= ( $('#Phone').val() );
      if( fullname!="" && gender!="" && phone!=""){        
        Router.push('/webpagetwo')
      }
      else if( fullname!="" && gender!=""){
        this.setState({ errrrphone:1 })

      }
      else if(phone!="" && gender!=""){
        this.setState({ errrrname:1 })
      }
      else if(fullname!="" && phone!="" ) {
        this.setState({ errrrgender:1 })
      }
      else{
        this.setState({ errrrgender:1, errrrname:1, errrrphone:1 })
      }

    }
    catch (e) {
      console.log(e)
    }
  }

  render() {
    return (
      <div className="firstpagebox">
        <div className="heading">
          <h2>Add your personal details</h2>
        </div>
        <div className="sub">
          <label>Lorum ipsum is simply dummy text of the printing and typesetting industry</label>
        </div>

        <div className="component">
          <div className="labelcss">
            <label style={{ color: (this.state.errrrname == 1 ?"#ed5901":"grey") }}>Full name</label>
            <div>
              <input className="inputcss" id="full_name" type="text" style={{ borderColor: (this.state.errrrname == 1 ? "#ed5901" : "") }}></input>
            </div>
          </div>

          <div className="labelcss">
            <label style={{ color: (this.state.errrrgender == 1 ?"#ed5901":"grey") }}>Gender</label>
            <div >
              <button className="gendrcss" onClick={()=>this.handle(1)}  style={{ borderColor: (this.state.errrrgender == 1 ? "#ed5901" : "") }} >Male</button>
              <button className="gendrcss" onClick={()=>this.handle(2)}  style={{ borderColor: (this.state.errrrgender == 1 ? "#ed5901" : "") }} >Fe-Male</button>
              <button className="gendrcss" onClick={()=>this.handle(3)} style={{ borderColor: (this.state.errrrgender == 1 ? "#ed5901" : "") }} >Other</button>
            </div>
          </div>

          <div className="labelcss">
            <label style={{ color: "grey" }}>Country</label>
            <div>
              <select className="inputcss" style={{ borderColor: (this.state.errrrcntry == 1 ? "#ed5901" : "") }}>
                <option id="Country" value="0" > </option>
                <option id="Country" value="1">India</option>
                <option id="Country" value="2"> Taiwan</option>
                <option id="Country" value="3" >Other</option>
              </select>
            </div>
          </div>

          <div className="labelcss">
            <label style={{ color: "grey" }}>State</label>
            <div>
              <select className="inputcss" style={{ borderColor: (this.state.errrrstate == 1 ? "#ed5901" : "") }}>
                <option id="State" value="0"> </option>
                <option id="State" value="1">Tamil Nadu</option>
                <option id="State" value="2">Karnataka</option>
                <option id="State" value="3">Other</option>
              </select>
            </div>
          </div>

          <div className="labelcss">
            <label style={{ color: (this.state.errrrphone == 1 ?"#ed5901":"grey") }}>Phone</label>
            <div> <input className=" inputcss" type="tel" maxLength="10" id="Phone" onKeyPress={(event) => this.isNumber(event)} style={{ borderColor: (this.state.errrrphone == 1 ? "#ed5901" : "") }} ></input></div>
          </div>
          <div className="labelcss">
            <button className="buttoncss" onClick={()=>this.moveNextPage()}>Next</button>
          </div>
        </div>
      </div>
    )
  }

}