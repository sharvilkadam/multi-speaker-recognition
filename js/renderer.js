// This file is required by the index.html file and will
// be executed in the renderer process for that window.
// All of the Node.js APIs are available in this process.

window.onload = function (e) {
    let waveFormContainer = document.getElementById('wave-form');
    let siriWave = new SiriWave({
        style: 'ios9',
        container: waveFormContainer,
        width: waveFormContainer.offsetWidth,
        height: waveFormContainer.offsetHeight
    });

    // siriWave.start();
};