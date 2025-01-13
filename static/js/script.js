

const navMenu = document.getElementById('nav-menu'),
      navToggle = document.getElementById('nav-toggle'),
      navClose = document.getElementById('nav-close')

/* Menu show */
if(navToggle){
   navToggle.addEventListener('click', () =>{
      navMenu.classList.add('show-menu')
   })
}

/* Menu hidden */
if(navClose){
    navClose.addEventListener('click', () =>{
       navMenu.classList.remove('show-menu')
    })
 }
uploadForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const fileInput = document.getElementById('imageUpload');
    const language = document.getElementById('language').value;
    const emailNotification = document.getElementById('emailNotification').checked;
    const smsNotification = document.getElementById('smsNotification').checked;
    const pushNotification = document.getElementById('pushNotification').checked;
    
    if (fileInput.files.length === 0 && photoCanvas.classList.contains('hidden')) {
        alert('Please upload an image file or take a photo.');
    } else {
        alert(`Image submitted successfully!\nLanguage: ${language}\nEmail: ${emailNotification}\nSMS: ${smsNotification}\nPush: ${pushNotification}`);

        const formData = new FormData();
        
        if (!photoCanvas.classList.contains('hidden')) {
            // If a photo was captured using the camera, convert it to a Blob and add it to the form data
            photoCanvas.toBlob((blob) => {
                formData.append('file', blob, 'captured_photo.png');
                submitToBackend(formData);
            });
        } else if (fileInput.files.length > 0) {
            // If an image file was uploaded, add it to the form data
            const file = fileInput.files[0];
            formData.append('file', file);
            submitToBackend(formData);
        } else {
            alert('No image selected or captured.');
        }
    }

    function submitToBackend(formData) {
        // Append additional preferences to the form data
        formData.append('language', document.getElementById('language').value);
        formData.append('emailNotification', emailNotification);
        formData.append('smsNotification', smsNotification);
        formData.append('pushNotification', pushNotification);

        // Send the form data to the Flask backend
        fetch('/predict', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'Failed to process the image');
                });
            }
            return response.text(); // Expecting the backend to render `display.html`
        })
        .then(html => {
            document.open();
            document.write(html);
            document.close();
        })
        .catch(error => {
            console.error('Error:', error);
            alert(`An error occurred: ${error.message}`);
        });
    }
});
