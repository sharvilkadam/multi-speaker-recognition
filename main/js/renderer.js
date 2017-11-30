// This file is required by the index.html file and will
// be executed in the renderer process for that window.
// All of the Node.js APIs are available in this process.

const jQuery = require('jquery');
const remote = require('electron').remote;
let request = require('request');


(function ($) {
    // Global variables
    let isListening = false;
    let waveFormContainer = document.getElementById('wave-form');
    let main = $("main");
    let enrollmentForm = $("#enrollment-form");
    let enrolledSpeakers = $("#enrolled-speakers");
    let enrollName = $("#name");
    let enrollSchedule = $("#schedule");
    let waiting = false;
    let history = $('#history');
    let loadingBar = $('#loading-bar');

    // Global microphone variables
    let audioBuffer = [];
    let context = new AudioContext();
    let microphone = null;
    let processor = null;
    let sampleRate = null;

    // Enable Microphone
    navigator.getUserMedia({audio: true}, function (stream) {
        microphone = context.createMediaStreamSource(stream);
        processor = context.createScriptProcessor(4096, 1, 1);
    }, function (e) {
        console.log(e);
    });

    function startRecording() {
        audioBuffer = [];
        microphone.connect(processor);
        processor.connect(context.destination);

        processor.onaudioprocess = function (e) {
            sampleRate = e.inputBuffer.sampleRate;
            audioBuffer.push(e.inputBuffer.getChannelData(0));
        };
    }

    function stopRecording() {
        processor.disconnect();
        microphone.disconnect();
        return processAudioBuffer(audioBuffer);
    }

    function processAudioBuffer(buff) {
        let output = new Array(buff.length);
        for (let i = 0; i < buff.length; ++i) {
            output[i] = Array.prototype.slice.call(buff[i]);
        }
        return output;
    }


    // Load enrolled speakers
    loadSpeakers();

    // Waveform setup
    let siriWave = new SiriWave({
        style: 'ios9',
        container: waveFormContainer,
        width: waveFormContainer.offsetWidth,
        height: waveFormContainer.offsetHeight,
        speed: 0,
    });
    siriWave.start();

    // Setup the buttons
    let recordQueryBtn = $("#record-query-btn");
    let enrollBtn = $("#enroll-btn");
    let recordEnrollBtn = $("#record-enroll-btn");
    let enrollSubmitBtn = $("#enroll-submit-btn");

    recordQueryBtn.click(function (e) {
        e.preventDefault();
        if (!waiting) {
            if (isListening) {
                waiting = true;
                recordQueryBtn.addClass('disabled');
                $(waveFormContainer).addClass('invisible');
                siriWave.setSpeed(0);
                siriWave.setAmplitude(0);
                recordQueryBtn.removeClass("pulse");
                isListening = false;

                let recording = stopRecording();
                let data = {
                    type: 'query',
                    data: {
                        sampleRate: sampleRate,
                        audio: recording,
                    }
                };

                request.post('http://127.0.0.1', {json: true, body: data}, function(err, res, body) {
                    console.log(err, res, body);
                    if (!err && res.statusCode === 200) {
                        console.log(body);
                        history.children().last().remove();
                        let data = body;
                        let speaker = data['speaker'];
                        let query = data['query'];
                        let response = data['response'];
                        history.append('<div class="question white z-depth-2">\n' +
                            '                <div>\n' +
                            '                    <i class="icon blue-grey circle white-text">' + speaker[0] + '</i>\n' +
                            '                    <div class="text">' + query + '</div>\n' +
                            '                </div>\n' +
                            '            </div>');
                        history.append('<div class="answer blue lighten-1 z-depth-2 white-text">\n' +
                            '                <div>\n' +
                            '                    <div class="text">' + response + '</div>\n' +
                            '                </div>\n' +
                            '            </div>');
                    }
                    else {
                        history.children().last().remove();
                        Materialize.toast('Couldn\'t connect to the server', 3000);
                    }

                    recordQueryBtn.removeClass('disabled');
                    waiting = false;
                });

            } else {
                siriWave.setSpeed(0.1);
                siriWave.setAmplitude(1);
                $(waveFormContainer).removeClass('invisible');
                recordQueryBtn.addClass("pulse");
                isListening = true;

                history.append('<div class="question white z-depth-2">\n' +
                    '                <div>\n' +
                    '                    ...\n' +
                    '                </div>\n' +
                    '            </div>');

                startRecording();
            }
        }
    });

    enrollBtn.click(function (e) {
        e.preventDefault();
        if (!isListening) {
            main.addClass("enrolling");
            document.addEventListener('mousedown', overlayClick);
        }
    });

    function overlayClick(e) {
        if (!isListening && !waiting)
            if (e.target.id !== 'enrollment-form' && $(e.target).parents("#enrollment-form").length === 0) {
                e.preventDefault();
                main.removeClass("enrolling");
                document.removeEventListener('mousedown', overlayClick);
            }
    }

    function loadSpeakers() {
        try {
            let speakers = require('./speakers/enroll.json');

            if (jQuery.isEmptyObject(speakers))
                return;

            enrolledSpeakers.empty();
            for (let key in speakers) {
                enrolledSpeakers.append('<div class="speaker white z-depth-2"><i class="icon blue-grey circle white-text">' + key[0] + '</i><div class="name">' + key + '</div></div>');
            }
        }
        catch (e) {
            console.log(e);
            console.log("speakers/enroll.json not found");
        }
    }

    let enrollmentAudio = [];
    recordEnrollBtn.click(function (e) {
        e.preventDefault();
        if (isListening) {
            recordEnrollBtn.removeClass('pulse');
            isListening = false;

            enrollmentAudio = stopRecording();

        } else {
            recordEnrollBtn.addClass('pulse');
            isListening = true;

            startRecording();
        }
    });

    enrollmentForm.submit(function (e) {
        e.preventDefault();

        if (!waiting) {
            waiting = true;
            let name = enrollName.val().trim();
            let schedule = enrollSchedule.val().trim();
            enrollSubmitBtn.addClass('disabled');

            let error = false;

            if (enrollmentAudio.length === 0) {
                Materialize.toast('Please record your audio', 3000);
                error = true;
            }

            if (name.length === 0) {
                Materialize.toast('Please enter a valid name', 3000);
                error = true;
            }

            if (schedule.length === 0) {
                Materialize.toast('Please enter a valid schedule', 3000);
                error = true;
            }

            if (error) {
                waiting = false;
                enrollSubmitBtn.removeClass('disabled');
                return;
            }

            let data = {
                type: 'enroll',
                data: {
                    name,
                    schedule,
                    sampleRate: sampleRate,
                    audio: enrollmentAudio,
                }
            };


            loadingBar.removeClass('invisible');


            request.post('http://127.0.0.1', {json: true, body: data}, function(err, res, body) {
                if (!err && res.statusCode === 200) {
                    console.log(body);
                    loadSpeakers();
                    Materialize.toast(name + ' enrolled', 3000);
                } else {
                    Materialize.toast('Speaker couldn\'t be enrolled. Please try again', 3000);
                }
                waiting = false;
                enrollSubmitBtn.removeClass('disabled');
                loadingBar.addClass('invisible');
            });
        }
    });

    $('#close-btn').click(function () {
        console.log('close clicked');
        let window = remote.getCurrentWindow();
        window.close();
    });

    $('#minimize-btn').click(function () {
        console.log('minimize clicked');
        let window = remote.getCurrentWindow();
        window.minimize();
    });

})(jQuery);