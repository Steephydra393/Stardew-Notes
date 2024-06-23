$(document).ready(function() { 
    // **Part 1: Quill Editor Setup **
    const openThePopupButton = document.getElementById('openThePopup');
    const popup = document.getElementById('popup');
    const submitButton = document.getElementById('submitText');
    const checkButton = document.getElementById('closePopup');
    const div3 = document.getElementById('div3');
    const categoryDropdown = document.getElementById('bundle');
    const openDeleteAllButton = document.getElementById('openDeleteAllButton')
    const DeleteAllPage = document.getElementById('deleteAll')
    const closeDeleteAllButton = document.getElementById('noDelAll')
    const deleteAllConfirmation = document.getElementById('delAll')
    const resultsContainers = document.getElementsByClassName('season-container');
    const eventListeners = []; // Array to store listeners
    const statusDots = document.querySelectorAll('.status-dot');
    const statusOrder = ['done', 'upgrade', 'none'];
    const yearDiv = document.getElementById('yearDisplay');
    const seasonDiv = document.getElementById('seasonDisplay');

    let quill = new Quill('#quill-editor', { theme: 'bubble' }); 

    statusDots.forEach(dot => {
        const currentStatus = dot.dataset.status;
        dot.style.setProperty('--current-status-color', `var(--${currentStatus}-color)`);
    });

    openDeleteAllButton.addEventListener('click', () => {
    DeleteAllPage.classList.remove('delallhidden');
    })

    closeDeleteAllButton.addEventListener('click', () => {
    DeleteAllPage.classList.add('delallhidden')
    })

    deleteAllConfirmation.addEventListener('click', () => {
    const selectedGuildID = "841474628614488086";
    DeleteAllPage.classList.add('delallhidden')
    deleteAllNotes(selectedGuildID)
    })

    function updateRefreshIcon() {
        const refreshButton = document.getElementById('refreshNotes'); 
        const refreshIcon = refreshButton.querySelector('img'); // Get the <img>

        if (hasError) {
            refreshIcon.src = "icons/sync_problem.svg";
            refreshIcon.alt = "Error - Click to retry";
        } else {
            refreshIcon.src = "icons/sync.svg";
            refreshIcon.alt = "Refresh";
        }
    }

    openThePopupButton.addEventListener('click', () => {
        popup.classList.remove('hidden');
        quill.enable(true); 
    }); 

    submitButton.addEventListener('click', () => {
      const text = quill.root.innerHTML; 
      //const selectedCategory = categoryDropdown.value; 
      const selectedCategory = 'Spring Foraging Bundle'; // TEMP 
      const selectedGuildID = "841474628614488086";
      //console.log(categoryDropdown.value)
      console.log('Spring Foraging Bundle') // TEMP
      sendDataAPI(text, selectedGuildID, selectedCategory); 
      quill.setText('');
      popup.classList.add('hidden');
      quill.enable(false); 
    });

    checkButton.addEventListener('click', () => {
      quill.setText('');
      popup.classList.add('hidden');
      quill.enable(false); 
    });

    function addListeners() {
        for (let i = 0; i < resultsContainers.length; i++) {
          const listener = function(event) { 
            const button = event.target;
            const resultId = button.dataset.resultId;
        
            // Make your API call to delete the result using the resultId
            fetch(`/api/results/${resultId}`, { method: 'DELETE' })
              .then(response => {
                if (response.ok) {
                  // Remove the result element from the DOM if the delete was successful
                  button.parentNode.remove(); 
                } else { // .then(response => {
                  // Handle errors
                  console.error('Error deleting result:', response.status);
                } // } else {
              }) // .then(response => {
              .catch(error => {
                // Handle network errors
                console.error('Error making API call:', error);
              }); // .catch(error => {
            console.log('Event listener added to:', button);
          };
          resultsContainers[i].addEventListener('click', listener);
          
          eventListeners.push(listener); 
        }
    }
    
    function removeListeners() {
        for (let i = 0; i < resultsContainers.length; i++) {
          for (let j = 0; j < eventListeners.length; j++) {
            resultsContainers[i].removeEventListener('click', eventListeners[j]);
          }
        }
        eventListeners.length = 0; // Reset the array
    }

    // **Part 2: Sending Data to the Backend**
    function sendDataAPI(text, guildId="841474628614488086", category="0") { 
        console.log('Sending data to API')
        console.log(guildId, category)
        fetch('http://127.0.0.1:5173/notes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },  
            body: JSON.stringify({ text: text, guild_id: guildId, category: category })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to create note');
            }
            return response.json(); 
        })
        .then(data => console.log('Note created successfully:', data)) 
        .catch(error => console.error('Error creating note:', error));
    } 

    function deleteBundle(bundleName) {
        const guildId = "841474628614488086"; // Get this dynamically, if needed
        const url = `http://127.0.0.1:5173/deleteBundle/${guildId}/${bundleName}`; 
    
        fetch(url, { 
            method: 'DELETE' 
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to delete bundle');
            }
            return response.json(); 
        })
        .then(data => { 
            console.log('Bundle deleted:', data);
            displayNotes(guildId); // Refresh the display
        })
        .catch(error => console.error('Error deleting bundle:', error));
    }
        
    // **Part 3: Fetching and Displaying Note Data**
    function displayNotes(guildId, filter) {
    try {
    const url = `http://127.0.0.1:5173/notes/${guildId || "841474628614488086"}/${filter || "bundle"}`;

    fetch(url)
        .then(response => response.json())
        .then(notesData => {
            div3.innerHTML = ''; // Clear previous notes  

            for (const season in notesData) {
                const seasonBundles = notesData[season]; // collects the notes for the given season

                const seasonDiv = document.createElement('div'); // Creates a div to hold the season and notes
                seasonDiv.classList.add('season-container'); // Adds the class `season-container` to the new div
                
                // Create a season header and div
                const headerDiv = document.createElement('div');
                headerDiv.classList.add('header-container');
                const seasonHeading = document.createElement('h2'); // Creates a new text field of the size h2
                seasonHeading.textContent = season.toUpperCase(); // Makes the text content the uppercase version of the data
                seasonHeading.classList.add('season-header'); // Makes the class of the heading the season-header
                headerDiv.appendChild(seasonHeading);
                seasonDiv.appendChild(headerDiv)

                for (const bundleArray of seasonBundles) {
                    const bundleName = bundleArray[0]['category'];

                    // Create bundle container
                    const bundleContainer = document.createElement('div');
                    bundleContainer.classList.add('bundle-container');
                    
                    // Add delete button 
                    const deleteButton = document.createElement('button');
                    deleteButton.classList.add('bundle-delete-button'); 
                    deleteButton.setAttribute('data-bundle-name', bundleName); // Add data attribute
                    
                    const deleteIcon = document.createElement('object');
                    deleteIcon.data = 'icons/delete_forever.svg';
                    deleteIcon.type = 'image/svg+xml';

                    deleteButton.appendChild(deleteIcon);

                    bundleContainer.appendChild(deleteButton);
                    
                    // Create a heading for the bundle
                    const bundleHeading = document.createElement('h4'); 
                    bundleHeading.classList.add('bundle-heading'); 
                    bundleHeading.textContent = bundleName;
                    bundleContainer.appendChild(bundleHeading);

                    // Add notes to the bundle
                    bundleArray.forEach(note => {
                        const noteBlock = document.createElement('div');
                        noteBlock.classList.add('note-block');

                        const noteDiv = document.createElement('div');
                        noteDiv.classList.add('note')

                        noteDiv.innerHTML = note.text;

                        

                        const noteStatusDiv = document.createElement('div');
                        noteStatusDiv.classList.add('status-bar');

                        const noteStatus = document.createElement("SPAN");
                        noteStatus.classList.add('status-dot');
                        noteStatus.setAttribute('data-status', note.message_status)
                        noteStatus.setAttribute('title', getStatusTitle(note.message_status))
                        
                        noteStatus.addEventListener('click', () => { 
                            const currentStatus = noteStatus.dataset.status;
                            const currentIndex = statusOrder.indexOf(currentStatus);
                            const nextIndex = (currentIndex + 1) % statusOrder.length;
                            const nextStatus = statusOrder[nextIndex];
                  
                            noteStatus.dataset.status = nextStatus;
                            noteStatus.style.setProperty('--current-status-color', `var(--${nextStatus}-color)`);
                            
                            // Call a function to update the status in your backend here.
                            updateNoteStatusInBackend(guildId || "841474628614488086", note.message_id, nextStatus); // Example function
                        });

                        noteStatusDiv.appendChild(noteStatus);

                        noteBlock.appendChild(noteStatusDiv);

                        bundleContainer.appendChild(noteBlock);

                        noteBlock.appendChild(noteDiv);
                    });
                    // Add the bundle container to the season container
                    seasonDiv.appendChild(bundleContainer);
                    
                }
                statusDots.forEach(dot => {
                    dot.addEventListener('click', () => {
                        console.log("Pressed")
                        const currentStatus = dot.dataset.status;
                        const currentIndex = statusOrder.indexOf(currentStatus);
                        const nextIndex = (currentIndex + 1) % statusOrder.length;
                        const nextStatus = statusOrder[nextIndex];
                  
                        // Update CSS variable directly 
                        dot.dataset.status = nextStatus; // Update the status in HTML
                        dot.style.backgroundColor = window.getComputedStyle(dot).getPropertyValue(`--${nextStatus}-color`);
                    });
                  });

                console.log("Display Notes API call successfully painted")
                hasError = false;
                updateRefreshIcon();

                div3.appendChild(seasonDiv); 
            }
        })
        .catch(error => {
            const errorDisplay = document.createElement('div'); // Creates a div to hold the season and notes
            errorDisplay.classList.add('error-display'); // Adds the class `error-display` to the new div
        
            const errorMes = `You dont apear to have any notes, or a strange error has appeared`

            const bundleHeading = document.createElement('h4'); 
            bundleHeading.classList.add('error-display'); 
            bundleHeading.textContent = errorMes;
            errorDisplay.appendChild(bundleHeading);
            
            div3.appendChild(errorDisplay); // Appends the new div to the `div3` element
    
            hasError = true;
            console.error("Error fetching notes:", error);
            updateRefreshIcon(); // Call updateRefreshIcon here on error
        });
    } catch (error) {
        // const errorDisplay = document.createElement('div'); // Creates a div to hold the season and notes
        // errorDisplay.classList.add('error-display'); // Adds the class `error-display` to the new div

        const errorMes = `You dont apear to have any notes, or a strange error has appeared`
        
        const bundleHeading = document.createElement('h4'); 
        bundleHeading.classList.add('error-display'); 
        bundleHeading.textContent = errorMes;
        errorDisplay.appendChild(bundleHeading);

        hasError = true;
        console.error("Error fetching notes:", error);
        updateRefreshIcon(); // Add this line here
    }
    }

    function getStatusTitle(status) {
        switch (status) {
          case 'done': return 'Done';
          case 'upgrade': return 'Upgrade Needed';
          case 'none': return 'No Plans';
          default: return 'Unknown Status';
        }
    }

    function updateNoteStatusInBackend(guild_id, noteId, newStatus) {
        // Use fetch or a similar library to send a request to your backend API
        fetch(`http://127.0.0.1:5173/notes/status/${guild_id}/${noteId}/`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: newStatus })
        })
          .then(response => {
            if (!response.ok) {
              throw new Error('Failed to update note status');
            }
            return response.json();
          })
          .then(data => console.log('Note status updated:', data))
          .catch(error => console.error('Error updating note status:', error));
    }

    function deleteAllNotes(guildId) {
    console.warn("Deleting !ALL NOTES!")
    const url = `http://127.0.0.1:5173/deleteAllNotes/${guildId || "841474628614488086"}`;
    fetch(url, {
        headers: { 'Content-Type': 'application/json' },  
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to delete all notes');
        }
        return response.json(); 
    })
    .then(data => console.log('Notes Deleted successfully:', data)) 
    .catch(error => console.error('Error Deleted notes:', error));
    }

    function displayGuildInfo(guildId) {
        const url = `http://127.0.0.1:5173/guilds/${guildId || "841474628614488086"}`;
      
        fetch(url)
          .then(response => {
            // Check for successful status code (200-299)
            if (!response.ok) {
              throw new Error(`Server error: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
            .then(guildData => {
            console.log("Send");
            yearDiv.innerHTML = '';
            seasonDiv.innerHTML = '';
      
            // Assuming guildData has properties year and season
            const yearDisplay = document.createElement('p');
            yearDisplay.textContent = guildData.year;
            yearDiv.append(yearDisplay);
      
            const seasonDisplay = document.createElement('p');
            seasonDisplay.textContent = guildData.season;
            seasonDiv.append(seasonDisplay);
        })
            .catch(error => {
            yearDiv.innerHTML = '<p>Year </p>';
            seasonDiv.innerHTML = '<p>Season </p>';
      
            const errorDisplay = document.createElement('img');

            errorDisplay.src = "icons/error.svg";
            errorDisplay.alt = "An error has appeared";
            errorDisplay.title = "Error Display";

            console.error("Error fetching Guild:", error); // Log full error details to console
      
            yearDiv.append(errorDisplay);
            seasonDiv.append(errorDisplay.cloneNode(true)); // Clone to show in both divs
        });
    }
      

    const refreshButton = document.getElementById('refreshNotes');
    refreshButton.addEventListener('click', () => {
        refreshButton.classList.remove('rotate-animation');
        setTimeout(() => { 
            refreshButton.classList.add('rotate-animation'); 
        }, 0); // A minimal delay is enough    
        const guildId = "841474628614488086"; // Get actual guild ID
        displayNotes(guildId, 'bundle'); 
        displayGuildInfo(guildId);
    });

    // Initial display of notes
    const guildId = "841474628614488086";
    displayNotes(guildId); 
    displayGuildInfo(guildId);
})