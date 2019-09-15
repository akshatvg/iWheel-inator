const mic = document.querySelector('.mic')
const recordingStatus = document.querySelector('.recording-status')
const samantha = window.speechSynthesis.getVoices().filter(voice => voice.name === 'Samantha')[0]

let isRecording = false;

mic.addEventListener('click', listenForSpeech)

/////////////////////////////////////////////////////////////////



/////////////////////////////////////////////////////////

function clearChatInput() {
  chatInput.value = ''
}

function sendTextChatMessage() {
  let newChat = chatInput.value
  postChatMessage(newChat)
}

function postChatMessage(response) {
  console.log("post chat function");
  res_list = document.getElementById("chat-responses");
  var user = {
    response: response
  };
  var template_one = `
  <ul class="chat">
  <div class="left clearfix"><span class="chat-img pull-left" style="display: inline-block">
  <div class="chat-body clearfix"
  style="display: inline-block;padding:0;margin-bottom: 0px;margin-left: 0px;">
  <div class="header">
  <strong class="primary-font">User</strong>
  </div>
  
  <img src="http://placehold.it/50/55C1E7/fff&text=U" alt="User Avatar" class="img-circle"
      style="margin-right:8px;" />
</span>
  <p>
     {{response}}
  </p><hr>
</div>
</ul>
`;
  var html = Mustache.to_html(template_one, user);
  $('#chat-responses').append(html);
  /*element_val = `
  User: ${response}
  `*/
  //res_list.append(element_val);
  //var temp =[];
  //res_list.innerHTML = template_one;
  //re_list.append(temp);
  var respon_json = {
    "text": response
  }
  $.ajax({
    type: "POST",
    contentType: "application/json;charset=utf-8",
    url: "http://localhost:5000/print/name",
    traditional: "true",
    data: JSON.stringify(respon_json),
    dataType: "json",
    success: function (response) {
      speakResponse(response.response);
      console.log(response.response)
      document.getElementById('tindis').innerHTML = response.response;
      //$('#tindis').append(response.response);
      //displayResponse(response.response);
    }
  });
}

function displayResponse(response) {
  var wheele = {
    response: response
  };
  var template_two = `
    <ul class="chat">
    <div align="right"><span class="chat-img pull-right" style="display: inline-block">
    <div class="chat-body"
    style="display: inline-block;padding:0;margin-bottom: 0px;margin-right: 0px;" align="right">
    <div class="header">
    <strong class="primary-font">iWheel-inator</strong>
    </div>
    <img src="../static/img/icons/favicon.png" alt="iWheel-inator Avatar" class="img-circle"
        style="margin-left:8px;width: 50px;height: 50px;" />
  </span>
    <p>
       {{response}}
    </p><hr>
  </div>
  </ul>
  `;

  var html = Mustache.to_html(template_two, wheele);
  $('#chat-responses').append(html);
  /*let newChat = document.createElement('p')
  newChat.innerText = `iWheel-inator : ${response}`
  chatMessages = document.getElementById("chat-input");
  res_list.append(newChat)*/
}

function speakResponse(response) {
  let utterance = new SpeechSynthesisUtterance(response);
  utterance.voice = samantha
  window.speechSynthesis.speak(utterance)
  displayResponse(response)
}

function listenForSpeech() {
  console.log(isRecording)
  if (isRecording) {
    isRecording = false
    recordingStatus.innerText = 'Ask me anything.'
    return 0;
  }
  isRecording = true
  recordingStatus.innerText = 'Listening for speech'
  var SpeechRecognition = SpeechRecognition || webkitSpeechRecognition
  var SpeechRecognitionEvent = SpeechRecognitionEvent || webkitSpeechRecognitionEvent
  var recognition = new SpeechRecognition()

  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  recognition.start()

  recognition.onspeechstart = function () {
    console.log('Speech has been detected');
  }

  recognition.onresult = function (event) {
    let last = event.results.length - 1;
    let speech = event.results[last][0].transcript;

    postChatMessage(speech)

    console.log('Result received: ' + speech + '.');
    console.log('Confidence: ' + event.results[0][0].confidence);
  }

  recognition.onspeechend = function () {
    recordingStatus.innerText = 'Ask me anything.'
    console.log('Speech has stopped being detected');
  }

  recognition.onerror = function (event) {
    console.log('Error occurred in recognition: ' + event.error);
  }
}

document.querySelector('.chat-bot-button').addEventListener('click', function () {
  console.log('clicked')
  document.querySelector('.chat-bot-modal').classList.toggle('open')
});