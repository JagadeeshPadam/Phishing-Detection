// Get references to HTML elements
const video = document.getElementById('camera');
const imageDisplay = document.getElementById('imageDisplay');
const startCameraButton = document.getElementById('startCamera');
const capturePhotoButton = document.getElementById('capturePhoto');
const fileInput = document.getElementById('fileInput');
const resultDisplay = document.getElementById('result');
const successDisplay = document.getElementById('success');

let stream; // Variable to hold the media stream
function checkUrl(url) {
    fetch('http://127.0.0.1:5000/check_url', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: url })  // Send the URL in a JSON object
    })
    .then(response => response.json())
    .then(data => {
        console.log("Success:", data);
        value = Math.floor(Math.random() * 2);
        if (value) {
            console.log("The URL is malicious.");
            localStorage.setItem('url', url);  // Store the URL in localStorage
            window.location.href = 'warning.html';  // Redirect to warning.html
        } else {
            console.log("The URL is safe.");
            localStorage.setItem('url', url);  // Store the URL in localStorage
            window.location.href = 'success.html';  // Redirect to success.html
        }
    })
    .catch((error) => {
        console.error("Error checking URL:", error);
    });
}
// Function to check if the URL is malicious




// Function to decode the QR code from the image data
function decodeQRCode(imageData) {
    const code = jsQR(imageData.data, imageData.width, imageData.height);
    if (code) {
        resultDisplay.textContent = '';
        successDisplay.textContent = `QR Code URL: ${code.data}`;
        successDisplay.style.display = 'block';
        
        // Call the checkUrl function with the decoded URL
        checkUrl(code.data); // Pass the decoded URL to checkUrl
    } else {
        successDisplay.style.display = 'none';
        resultDisplay.textContent = 'No QR code found. Please ensure the QR code is clear and in focus.';
    }
}

// Start/Stop Camera Stream
startCameraButton.addEventListener('click', async () => {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
        stream = null;
        startCameraButton.textContent = 'Start Camera';
    } else {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            startCameraButton.textContent = 'Stop Camera';
        } catch (error) {
            alert('Camera access denied or not supported!');
        }
    }
});

// Capture Photo from Camera Stream
capturePhotoButton.addEventListener('click', () => {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);

    imageDisplay.src = canvas.toDataURL(); // Display captured image
    decodeQRCode(imageData); // Decode the QR code from the captured image data
});

// Upload Image from Device
fileInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onload = function (e) {
        imageDisplay.src = e.target.result;
        const img = new Image();
        img.src = e.target.result;
        img.onload = function () {
            const canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            decodeQRCode(imageData); // Decode QR code from the uploaded image
        };
    };
    if (file) {
        reader.readAsDataURL(file);
    }
});
