document.addEventListener('DOMContentLoaded', () => {
    initQRScanner();
});

let html5QrcodeScanner = null;
let isScanning = false;

function initQRScanner() {
    const scannerId = "qr-reader";
    const statusText = document.getElementById("scanner-status");
    const spinner = document.getElementById("scanner-spinner");
    const overlay = document.getElementById("scanner-overlay");
    const toggleCameraBtn = document.getElementById("btn-toggle-camera");
    
    // Check if scanner element exists on current page
    if (!document.getElementById(scannerId)) return;
    
    // Toggle camera scanning
    if (toggleCameraBtn) {
        toggleCameraBtn.addEventListener('click', () => {
            if (isScanning) {
                stopScanner();
            } else {
                startScanner();
            }
        });
    }

    // Start scanner automatically on load
    startScanner();

    // Mock Scan Simulator handler
    const mockBtn = document.getElementById('btn-mock-scan');
    const mockInput = document.getElementById('mock-code-input');
    const mockError = document.getElementById('mock-error-message');
    
    if (mockBtn && mockInput) {
        mockBtn.addEventListener('click', () => {
            const mockValue = mockInput.value.trim();
            if (!mockValue) return;
            
            mockError.style.display = 'none';
            sendDecodeRequest(mockValue, mockError);
        });
        
        mockInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                mockBtn.click();
            }
        });
    }
}

function startScanner() {
    const statusText = document.getElementById("scanner-status");
    const spinner = document.getElementById("scanner-spinner");
    const overlay = document.getElementById("scanner-overlay");
    
    if (isScanning) return;
    
    isScanning = true;
    statusText.textContent = "Requesting camera permissions...";
    spinner.style.display = 'block';
    overlay.style.display = 'flex';
    
    // Instantiate Html5Qrcode
    html5QrcodeScanner = new Html5Qrcode("qr-reader");
    
    // Camera configuration
    const config = { fps: 10, qrbox: { width: 220, height: 220 } };
    
    html5QrcodeScanner.start(
        { facingMode: "environment" }, // Target back camera
        config,
        onScanSuccess,
        onScanFailure
    ).then(() => {
        statusText.textContent = "Scanning... Align QR code inside square box.";
        spinner.style.display = 'none';
    }).catch(err => {
        console.error("Camera start error: ", err);
        statusText.textContent = "Camera access failed. Use the Simulator below.";
        spinner.style.display = 'none';
        overlay.style.display = 'none';
        isScanning = false;
    });
}

function stopScanner() {
    const statusText = document.getElementById("scanner-status");
    const overlay = document.getElementById("scanner-overlay");
    
    if (!isScanning || !html5QrcodeScanner) return;
    
    html5QrcodeScanner.stop().then(() => {
        statusText.textContent = "Camera Stopped.";
        overlay.style.display = 'none';
        isScanning = false;
    }).catch(err => {
        console.error("Failed to stop camera: ", err);
    });
}

function onScanSuccess(decodedText, decodedResult) {
    // A QR code has been read successfully
    stopScanner();
    
    const statusText = document.getElementById("scanner-status");
    statusText.textContent = `Scanned Code: ${decodedText}. Processing...`;
    
    const mockError = document.getElementById('mock-error-message');
    sendDecodeRequest(decodedText, mockError);
}

function onScanFailure(error) {
    // Failures happen constantly if code is not fully aligned, we don't alert or print them
}

async function sendDecodeRequest(codeText, errorContainer) {
    try {
        const response = await fetch('/qr/decode', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code: codeText })
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.location.href = data.redirect_url;
        } else {
            if (errorContainer) {
                errorContainer.textContent = data.message;
                errorContainer.style.display = 'block';
            }
            
            const statusText = document.getElementById("scanner-status");
            if (statusText) {
                statusText.textContent = `Lookup Failed: ${data.message}`;
            }
            
            setTimeout(() => {
                if (document.getElementById("qr-reader") && !isScanning) {
                    startScanner();
                    if (errorContainer) errorContainer.style.display = 'none';
                }
            }, 3000);
        }
    } catch (err) {
        console.error("Decode request error: ", err);
        if (errorContainer) {
            errorContainer.textContent = "Server communication failure.";
            errorContainer.style.display = 'block';
        }
    }
}
