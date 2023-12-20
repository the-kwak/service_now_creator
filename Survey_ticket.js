const xapi = require('xapi');

const panelId = 'survey_Id';

var ticket_request = true

var meetingsToWatch = ['@zoomcrc.com','@webex.com', '.mskcc@m.webex.com'];
var codec_data = {
      'video'         : false,
      'audio'         : false,
      'clickshare'    : false,
      'laptop'        : false,
      'pc'            : false,
      'disconnecting' : false,
      'username'      : '',
      'feature_req'   : '',
      'date'          : '',
      'time'          : '',
      'cause_type'    : '',
      'meeting_name'  : '',
      'duration'      : '',
      'origin_call'   : '',
      'remote_uri'    : '',
      'requested_uri' : '',
      'meeting_type'  : '',
      'protocol'      : '',
      'IP_Address'    : ''
    };

console.log("Starting up");
codec_data_scrapper();
sleep(70);
//sleep(60).then(() => {console.log(codec_data)});

var original_codec_data = codec_data

function postRequest() {
  var body = codec_data
  var body_JSON=JSON.stringify(body);

  // Server ip http://plvinetcodecsn1.mskcc.org:5000/survey -> 140.163.78.108
  console.log(`results to be sent:\n${body_JSON}`)
  xapi.Command.HttpClient.Post({AllowInsecureHTTPS: 'True', Url:'http://plvinetcodecsn1.mskcc.org:5000/survey', ResultBody:'PlainText' },`${body_JSON}`).then((response) => {
    //console.log(response);
    console.log(response['Body'])
    var response_body_dict = JSON.parse(response['Body'])
    console.log(response_body_dict.ticket)
    
    xapi.command("UserInterface Message Alert Display", {
        Text: 'Ticket has been created'
        , Title: `Ticket number : ${response_body_dict.ticket}`
        , Duration: 300
    });
    /*
    captureResponse = JSON.stringify(response);
    console.log(captureResponse);
    */
  });
  sleep(1000);
  ticket_request = false
  //console.log('In PostRequest')
  //console.log(ticket_request)
  return 0
}

function restore_original(){
  xapi.Command.UserInterface.Extensions.Widget.UnsetValue({ WidgetId: 'msk_username' });
  xapi.Command.UserInterface.Extensions.Widget.UnsetValue({ WidgetId: 'fe_req' });
  xapi.Command.UserInterface.Extensions.Widget.SetValue({ Value: 'off', WidgetId: 'vid_issue_toggle' });
  xapi.Command.UserInterface.Extensions.Widget.SetValue({ Value: 'off', WidgetId: 'audio_issue_toggle' });
  xapi.Command.UserInterface.Extensions.Widget.SetValue({ Value: 'off', WidgetId: 'clickshare_issue_toggle' });
  xapi.Command.UserInterface.Extensions.Widget.SetValue({ Value: 'off', WidgetId: 'laptop_issue_toggle' });
  xapi.Command.UserInterface.Extensions.Widget.SetValue({ Value: 'off', WidgetId: 'pc_issue_toggle' });
  xapi.Command.UserInterface.Extensions.Widget.SetValue({ Value: 'off', WidgetId: 'discon_issue_toggle' });
  codec_data = original_codec_data
};

async function codec_data_scrapper(){

  const system_name = await xapi.Config.SystemUnit.Name.get();
  const system_type = await xapi.Status.SystemUnit.ProductId.get();
  const system_version = await xapi.Status.SystemUnit.Software.DisplayName.get();
  const system_ip = await xapi.Status.Network[1].IPv4.Address.get()
  var http_client = await xapi.Config.HttpClient.Mode.get()
  var insecure_https = await xapi.Config.HttpClient.AllowInsecureHTTPS.get()
  
  

  codec_data['codec_name'] = system_name;
  codec_data['product'] = system_type;
  codec_data['version'] = system_version;
  codec_data['IP_Address' ] = system_ip

  if (insecure_https == 'False'){
    xapi.Config.HttpClient.AllowInsecureHTTPS.set('True');
  }
  //console.log(http_client)
  if (http_client == 'Off'){
    xapi.Config.HttpClient.Mode.set('On');
  }
  return 0
};


function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
};

//// using on CallSuccessful because I can get remoteURI and determine meeting type
xapi.event.on('CallSuccessful', (event) => {
  
  restore_original();

  if (meetingsToWatch.some(substring=>event.RemoteURI.includes(substring))){
    xapi.command("UserInterface Message Alert Display", {
              Text: 'Please send us some feedback on your meeting in the post meeting survey'
              , Title: 'Meeting Started '
              , Duration:30
    }).catch((error) => { console.error(error); });

    if(event.RemoteURI.includes('@zoomcrc.com')){
      //console.log(`SiP Zoom Call ${event.RemoteURI}`)
      codec_data['meeting_type'] = 'Zoom';
    }
    else if(event.RemoteURI.includes('.mskcc@m.webex.com')){
      //console.log(`SiP Teams Call ${event.RemoteURI}`) 
      codec_data['meeting_type'] = 'Teams';
    }
    else if(event.RemoteURI.includes('@webex.com')){
      //console.log(`SiP Webex Call ${event.RemoteURI}`)  
      codec_data['meeting_type'] = 'Webex';
    }
  }
});

xapi.event.on('CallDisconnect', (event) => {
  if (meetingsToWatch.some(substring=>event.RequestedURI.includes(substring))){
    var newDate = new Date()
    var date = newDate.toLocaleDateString()
    var time = newDate.toLocaleTimeString()
    

    codec_data['date'] = date
    codec_data['time'] = time
    codec_data['cause_type'] = event.CauseType
    codec_data['meeting_name'] = event.DisplayName
    codec_data['duration'] = event.Duration
    codec_data['origin_call'] = event.OriginCallDirection
    codec_data['remote_uri' ] = event.RemoteURI
    codec_data['requested_uri'] = event.RequestedURI
    codec_data['protocol'] = event.Protocol
      
      if(event.Duration > 0){
          xapi.command("UserInterface Message Prompt Display", {
                Title: "How was the meeting experience"
              //, Text: 'Please rate this call'
              , Text: ''
              , FeedbackId: 'callrating'
              , 'Option.1':'The call went well!'
              , 'Option.2':'There were issues'
            }).catch((error) => { console.error(error); });
      }
      else{
          /*
          xapi.command("UserInterface Message Prompt Display", {
                Title: "What went wrong?"
              , Text: 'Hm, no call. What happened?'
              , FeedbackId: 'nocallrating'
              , 'Option.1':'I dialled the wrong number!'
              , 'Option.2':"I don't know"
              , 'Option.3': 'oops, wrong button'
        }).catch((error) => { console.error(error); });
        */
      }
  }
  else{
    //console.log('Not surveying meeting')
  }
});

xapi.event.on('UserInterface Message TextInput Response', (event) => {
    switch(event.FeedbackId){
        case 'callrating':
                sleep(1000).then(() => {
                    xapi.command("UserInterface Message TextInput Display", {
                              Duration: 0
                            , FeedbackId: "feedback_step2"
                            , InputType: "SingleLine"
                            , KeyboardState: "Open"
                            , Placeholder: "Write your contact info here"
                            , SubmitText: "Next"
                            , Text: "Please let us know how we can contact you for a follow up"
                            , Title: "Contact info"
                      }).catch((error) => { console.error(error); });
                });
              break;
        case 'feedback_step2':
            sleep(500).then(() => {
                xapi.command("UserInterface Message Alert Display", {
                    Title: 'Feedback receipt'
                    , Text: 'Thank you for you feedback! Have a great day!'
                    , Duration: 3
                }).catch((error) => { console.error(error); });
            });
            break;
    }
});


xapi.event.on('UserInterface Message Prompt Response', (event) => {
    var displaytitle = '';
    var displaytext = '';
    switch(event.FeedbackId){
        case 'callrating':
            switch(event.OptionId){
                case '1':
                    displaytitle = 'Thank you!';
                    displaytext = 'Hava a great day!';
                    xapi.command("UserInterface Message Alert Display", {Title: displaytitle, Text: displaytext, Duration: 8});
                    break;
                case '2':
                    xapi.Command.UserInterface.Extensions.Panel.Open({ PanelId: 'survey_Id' });
                    break;
                
                default:
                    displaytext = 'Hm, that was an unhandled answer';
            }
            break;

        case 'nocallrating':
            switch(event.OptionId){
                case '1':
                    displaytitle = ':-)';
                    displaytext = 'Ok, maybe we need to make larger buttons..';
                    break;
                case '2':
                    displaytitle = 'Oops';
                    displaytext = 'Ok, do you want to try to debug?';
                    break;
                case '3':
                    displaytitle = ':-(';
                    displaytext = 'Oops, maybe we need a simpler user interface';
                    break;

                default:
                    displaytext = 'Hm, that was an unhandled answer';
            }
            xapi.command("UserInterface Message Alert Display", {
                Title: displaytitle
                , Text: displaytext
                , Duration: 5
            }).catch((error) => { console.error(error); });
    }
});



/////////////// Code for survey opening check

xapi.event.on('UserInterface Extensions Panel Open', (event) => {
    console.log(event)
    if(event.PanelId == panelId){
      //console.log("inside_loop")
      //console.log(event.PanelId)
      xapi.event.on('UserInterface Extensions Widget Action', (press) => {
        // Toggles use 'on' 'off' for 
        switch(press.WidgetId){
          case 'vid_issue_toggle':
            //console.log('Video issues')
            codec_data['video'] = (press.Value=='on')
            break;

          case 'audio_issue_toggle':
            codec_data['audio'] = (press.Value=='on')
            //console.log('Audio issues')
            break;

          case 'clickshare_issue_toggle':
            codec_data['clickshare'] = (press.Value=='on')
            //console.log('Content issue')
            break;

          case 'laptop_issue_toggle':
            codec_data['laptop'] = (press.Value=='on')
            //console.log('Content issue')
            break;
          case 'pc_issue_toggle':
            codec_data['pc'] = (press.Value=='on')
            //console.log('Content issue')
            break;
          
          case 'discon_issue_toggle':
            codec_data['disconnecting'] = (press.Value=='on')
            break;
          
          case 'ID_Keyboard':
             xapi.command('UserInterface Message TextInput Display', {
                     Title: 'Enter Msk Username',
                     Text: 'Please enter your username to be contacted about the issues',
                     FeedbackId: 'msk_username',
                     Placeholder: 'MSK UserName',
                     //InputType: 'Numeric',
                     KeyboardState: 'Open',
                     SubmitText: 'Accept'
                     });
            break;
                    case 'Feature_keys':
             xapi.command('UserInterface Message TextInput Display', {
                     Title: 'Enter Issue Details',
                     Text: 'Please enter details on the issue',
                     FeedbackId: 'fe_req',
                     Placeholder: 'None',
                     //InputType: 'Numeric',
                     KeyboardState: 'Open',
                     SubmitText: 'Accept'
                     });
            break;
          
          case 'submit_survey':
            console.log(ticket_request)
            console.log("Submit clicked")
            if (codec_data["username"] == false){
                  xapi.command("UserInterface Message Alert Display", {
                  Text: 'Please enter an MSK UserName'
                  , Title: `Enter an Msk UserName`
                  , Duration: 15
                  });
            }
            else if ( !(codec_data['video'] || codec_data['audio'] || codec_data['clickshare'] || codec_data['laptop'] || codec_data['disconnecting'] || codec_data['pc'] )){
                  xapi.command("UserInterface Message Alert Display", {
                  Text: 'Please select the appropriate issue/s'
                  , Title: `No issues selected`
                  , Duration: 15
                  });
            }
            else{
              if (press.Type == 'released' && ticket_request){
                sleep(100).then(() => {xapi.Command.UserInterface.Extensions.Panel.Close();});
                postRequest();
                sleep(5000);
                console.log(ticket_request)
                console.log("After submit pressed")
                ticket_request = true
                console.log(ticket_request)
                restore_original();
                ticket_request = true

              }
            }
          break;
        }
      })
    }
  
});

// Listens to the Users entry from the text field above 
xapi.event.on('UserInterface Message TextInput Response', (event) => {
  if (event.FeedbackId ==  'msk_username'){
    codec_data['username'] = event.Text;
    xapi.command('UserInterface Extensions Widget SetValue', {
	         Value: 'UserName: ' + event.Text,
	         WidgetId: event.FeedbackId
	       });
  }
  if(event.FeedbackId ==  'fe_req'){
    codec_data['feature_req'] = event.Text;
    xapi.command('UserInterface Extensions Widget SetValue', {
	         Value: 'Request: ' + event.Text,
	         WidgetId: event.FeedbackId
	       });
  }
});

