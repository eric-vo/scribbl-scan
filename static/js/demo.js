let isDrawing = false;
let lastCoordinates;

document.addEventListener('DOMContentLoaded', () => {
    // Set up the canvas
    const canvas = document.getElementById('drawing-canvas');
    const context = canvas.getContext('2d');
    context.lineCap = 'round';
    context.lineWidth = 3;
    context.strokeStyle = 'white';

    canvas.addEventListener('mousedown', event => {
        isDrawing = true;

        const { x: mouseXInCanvas, y: mouseYInCanvas } = getMousePositionInCanvas(canvas, event)

        // Draw a dot
        updateLastCoordinates(mouseXInCanvas, mouseYInCanvas);
        draw(
            context,
            lastCoordinates.x,
            lastCoordinates.y,
            mouseXInCanvas,
            mouseYInCanvas,
        );
    });

    canvas.addEventListener('mouseover', event => {
        const { x: mouseXInCanvas, y: mouseYInCanvas } = getMousePositionInCanvas(canvas, event)
        updateLastCoordinates(mouseXInCanvas, mouseYInCanvas);
    });

    canvas.addEventListener('mousemove', event => {
        if (!isDrawing) return;

        const { x: mouseXInCanvas, y: mouseYInCanvas } = getMousePositionInCanvas(canvas, event)
        // Draw a line from the last coordinates to the current coordinates
        draw(
            context,
            lastCoordinates.x,
            lastCoordinates.y,
            mouseXInCanvas,
            mouseYInCanvas,
        );
        updateLastCoordinates(mouseXInCanvas, mouseYInCanvas);
    });

    // Stop drawing when the mouse is released
    window.addEventListener('mouseup', () => {
        isDrawing = false;
    });

    const upload = document.querySelector('#upload');
    upload.onchange = () => {
        const image_file = upload.files[0];
        const image = new Image();
        image.src = URL.createObjectURL(image_file);

        image.onload = () => {
            clearCanvas(canvas, context);

            /* Draw the image on the canvas,
            centered and scaled to fit the canvas */
            const scaleMultiplier = 0.8;
            const scale = Math.min(
                canvas.width / image.width * scaleMultiplier,
                canvas.height / image.height * scaleMultiplier,
            );
            const x = (canvas.width / 2) - (image.width / 2) * scale;
            const y = (canvas.height / 2) - (image.height / 2) * scale;

            // Put the image on the canvas
            context.drawImage(
                image, x, y, image.width * scale, image.height * scale
            );
        };
    };

    document.querySelector('#check').onclick = () => {
        const result = document.querySelector('#result');

        fadeInHtml(result, 'Thinking...');

        // Convert the canvas to an image
        const image = canvasToImage(canvas, context);

        // Create a form with the image data
        const formData = new FormData();
        formData.append('image', image.src);
        console.log(image.src);

        // Make an API call to the server
        fetch('/demo', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                // Display the result
                fadeInHtml(result, data.text);
            });
    };

    document.querySelector('#trash').onclick = () => {
        clearCanvas(canvas, context);
        clearFile(upload);
    };
});

function getMousePositionInCanvas(canvas, event) {
    const { clientX, clientY } = event
    const { left, top, width, height } = canvas.getBoundingClientRect()
    const scaleX = canvas.width / width
    const scaleY = canvas.height / height

    return {
        x: (clientX - left) * scaleX,
        y: (clientY - top) * scaleY
    }
}

function canvasToImage(canvas, context) {
    // Get image data from canvas
    const imageData = context.getImageData(
        0, 0, canvas.width, canvas.height
    ).data;

    // Find the left and right edges of the drawing
    let leftEdge = canvas.width;
    let rightEdge = 0;

    // The image array is a 1D array with 4 values per pixel (RGBA)
    for (let x = 0; x < canvas.width; x++) {
        for (let y = 0; y < canvas.height; y++) {
            const index = (y * canvas.width + x) * 4;
            const alpha = imageData[index + 3];

            // If the pixel is not transparent, it's part of the drawing
            if (alpha > 0) {
                if (x < leftEdge) {
                    leftEdge = x;
                }
                if (x > rightEdge) {
                    rightEdge = x;
                }
            }
        }
    }

    // Calculate the width cropped canvas
    const croppedWidth = rightEdge - leftEdge + 1;

    // Create a new canvas to store the cropped image
    const tempCanvas = document.createElement('canvas');
    const tempContext = tempCanvas.getContext('2d');

    // Set the temp canvas to the same size as the cropped image
    tempCanvas.width = croppedWidth;
    tempCanvas.height = canvas.height;

    // Draw the cropped image as a black stroke on a white background
    tempContext.filter = 'invert(1)';
    tempContext.fillStyle = 'black';
    tempContext.fillRect(0, 0, croppedWidth, canvas.height);
    tempContext.drawImage(canvas, -leftEdge, 0);

    // Convert the temp canvas to an image
    const dataUrl = tempCanvas.toDataURL();
    const image = new Image();
    image.src = dataUrl;

    return image;
}

function clearCanvas(canvas, context) {
    context.clearRect(0, 0, canvas.width, canvas.height);
}

function clearFile(fileUpload) {
    fileUpload.value = '';
}

function draw(context, fromX, fromY, toX, toY) {
    // Draw a line from (fromX, fromY) to (toX, toY)
    context.beginPath();
    context.moveTo(fromX, fromY);
    context.lineTo(toX, toY);
    context.stroke();
}

function fadeInHtml(element, html) {
    element.classList.remove('fade');
    element.offsetHeight;
    element.classList.add('fade');
    element.innerHTML = html;
}

function updateLastCoordinates(x, y) {
    lastCoordinates = { x: x, y: y }
}
