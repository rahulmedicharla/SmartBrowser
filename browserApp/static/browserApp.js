let recordButton = document.getElementById('recordButton');

var chunks = [];

navigator.mediaDevices.getUserMedia({audio: true})
  .then(function(stream) {
    var mediaRecorder = new MediaRecorder(stream);

    let form = document.getElementById('searchForm')
    let csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]').value;

    recordButton.addEventListener('click', function(event){
        event.preventDefault()
    
        if (recordButton.getAttribute('src') == '../static/microphoneOff.png' && mediaRecorder.state === "inactive"){
            recordButton.setAttribute('src', '../static/microphoneOn.png')
            console.log('start recording')
            mediaRecorder.start();
        }
        else{
            recordButton.setAttribute('src', '../static/microphoneOff.png')
            console.log('end recording')
            mediaRecorder.stop();
        }
    
        console.log('clicked');
    })

    mediaRecorder.ondataavailable = function(event) {
      chunks.push(event.data);
    }

    mediaRecorder.onstop = async function(event) {
      var blob = new Blob(chunks, { 'type' : 'audio/ogg; codecs=opus' });
      var oggFile = new FormData();
      oggFile.append('audio', blob);

      makeLoadingVisible()


      // Create an AudioContext instance
      const audioContext = new AudioContext();

      const fileReader = new FileReader()
      fileReader.onload = async function(){
        const arrayBuffer = this.result

        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

        // Convert the audio buffer to a WAV buffer
        const wavBuffer = encodeWAV(audioBuffer);

        // Create a Blob object from the WAV buffer
        const wavBlob = new Blob([wavBuffer], { type: "audio/wav" });

        // Create a new FormData object to send the WAV file to the server
        const wavFormData = new FormData();
        wavFormData.append("audio", wavBlob, "audio.wav");

        $.ajax({
          url: '/recordAudio/',
          type: 'POST',
          data: wavFormData,
          contentType: false,
          processData: false,
          beforeSend: function(xhr, settings){
              xhr.setRequestHeader("X-CSRFToken", csrfToken)
          },
          success: function(data) {
            window.location.reload()
          },
        });

        chunks = []
      }

      fileReader.readAsArrayBuffer(blob);
    }
  })
  .catch(function(err) {
    console.log("Error: " + err);
  });


  function encodeWAV(audioBuffer) {
    const numChannels = audioBuffer.numberOfChannels;
    const sampleRate = audioBuffer.sampleRate;
    const bitDepth = 16;
    const bytesPerSample = bitDepth / 8;
    const blockAlign = numChannels * bytesPerSample;
    const dataSize = audioBuffer.length * blockAlign;
    const buffer = new ArrayBuffer(44 + dataSize);
    const view = new DataView(buffer);
  
    // RIFF identifier
    writeString(view, 0, 'RIFF');
    // file length minus RIFF identifier length and file description length
    view.setUint32(4, 36 + dataSize, true);
    // RIFF type
    writeString(view, 8, 'WAVE');
    // format chunk identifier
    writeString(view, 12, 'fmt ');
    // format chunk length
    view.setUint32(16, 16, true);
    // sample format (raw)
    view.setUint16(20, 1, true);
    // channel count
    view.setUint16(22, numChannels, true);
    // sample rate
    view.setUint32(24, sampleRate, true);
    // byte rate (sample rate * block align)
    view.setUint32(28, sampleRate * blockAlign, true);
    // block align (channel count * bytes per sample)
    view.setUint16(32, blockAlign, true);
    // bit depth
    view.setUint16(34, bitDepth, true);
    // data chunk identifier
    writeString(view, 36, 'data');
    // data chunk length
    view.setUint32(40, dataSize, true);
  
    // write audio data to buffer
    let offset = 44;
    for (let i = 0; i < audioBuffer.numberOfChannels; i++) {
      const channelData = audioBuffer.getChannelData(i);
      for (let j = 0; j < channelData.length; j++) {
        view.setInt16(offset, channelData[j] * 0x7fff, true);
        offset += bytesPerSample;
      }
    }
  
    return buffer;
  }
  
  function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  }

  function makeLoadingVisible(){
    document.getElementById("loading_gif").removeAttribute('hidden')
  }
  