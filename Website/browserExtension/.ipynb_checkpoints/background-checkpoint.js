// chrome.action.onClicked.addListener(async (tab) => {
//   if (!tab || !tab.id) return;
//   await chrome.scripting.executeScript({
//     target: { tabId: tab.id },
//     function: togglePanel
//   });
// });

// function togglePanel() {
//   const existing = document.getElementById('jobSaverContainer');
//   if (existing) {
//     existing.remove();
//     return;
//   }

//   // Inject styling dynamically
//   const style = document.createElement('style');
//   style.textContent = `
//     #jobSaverContainer {
//       position: fixed;
//       top: 80px;
//       right: 40px;
//       width: 400px;
//       max-height: 85vh;
//       background-color: #ffffff;
//       border: 1px solid #ddd;
//       border-radius: 10px;
//       box-shadow: 0 8px 16px rgba(0,0,0,0.2);
//       z-index: 999999;
//       overflow-y: auto;
//       padding: 20px;
//       font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
//     }
//     #jobSaverHeader {
//       font-size: 24px;
//       font-weight: 600;
//       margin-bottom: 20px;
//       text-align: center;
//       position: relative;
//     }
//     #jobSaverClose {
//       position: absolute;
//       top: 0;
//       right: 10px;
//       font-size: 28px;
//       cursor: pointer;
//       color: #666;
//     }
//     #jobSaverForm .form-group {
//       margin-bottom: 15px;
//     }
//     #jobSaverForm input,
//     #jobSaverForm select,
//     #jobSaverForm textarea {
//       width: 100%;
//       padding: 10px;
//       font-size: 16px;
//       border: 1px solid #ccc;
//       border-radius: 6px;
//       box-sizing: border-box;
//       margin-bottom: 8px;
//     }
//     #jobSaverForm textarea {
//       min-height: 100px;
//       resize: vertical;
//     }
//     #jobSaverForm button.save-btn {
//       width: 100%;
//       padding: 12px;
//       background-color: #0d6efd;
//       border: none;
//       color: #fff;
//       font-size: 16px;
//       border-radius: 6px;
//       cursor: pointer;
//       transition: background-color 0.3s ease;
//       font-weight: 600;
//     }
//     #jobSaverForm button.save-btn:hover {
//       background-color: #0b5ed7;
//     }
//   `;
//   document.head.appendChild(style);

//   // Create the container
//   const container = document.createElement('div');
//   container.id = 'jobSaverContainer';

//   // Create header with close button
//   const header = document.createElement('div');
//   header.id = 'jobSaverHeader';
//   header.textContent = 'Save Job';

//   const closeBtn = document.createElement('span');
//   closeBtn.id = 'jobSaverClose';
//   closeBtn.innerHTML = '&times;';
//   closeBtn.addEventListener('click', () => {
//     container.remove();
//     style.remove();
//   });
//   header.appendChild(closeBtn);
//   container.appendChild(header);

//   // Create the form
//   const form = document.createElement('form');
//   form.id = 'jobSaverForm';
//   form.innerHTML = `
//     <div class="form-group">
//       <input type="text" id="jsJobTitle" name="title" placeholder="Job Title" required>
//     </div>
//     <div class="form-group">
//       <input type="text" id="jsCompany" name="company" placeholder="Company" required>
//     </div>
//     <div class="form-group">
//       <input type="text" id="jsLocation" name="location" placeholder="Location" required>
//     </div>
//     <div class="form-group">
//       <select id="jsStatus" name="status" required>
//         <option value="">Select Status</option>
//         <option value="Bookmarked">Bookmarked</option>
//         <option value="Applying">Applying</option>
//         <option value="Applied">Applied</option>
//         <option value="Interview">Interview</option>
//         <option value="Negotiation">Negotiation</option>
//         <option value="Offer">Offer</option>
//       </select>
//     </div>
//     <div class="form-group">
//       <textarea id="jsDescription" name="description" placeholder="Job Description"></textarea>
//     </div>
//     <button type="submit" class="save-btn">Save Job</button>
//   `;
//   container.appendChild(form);
//   document.body.appendChild(container);

//   // Handle form submission
//   form.addEventListener('submit', async (event) => {
//     event.preventDefault();
//     const jobData = {
//       title: document.getElementById('jsJobTitle').value.trim(),
//       company: document.getElementById('jsCompany').value.trim(),
//       location: document.getElementById('jsLocation').value.trim(),
//       status: document.getElementById('jsStatus').value,
//       description: document.getElementById('jsDescription').value.trim()
//     };

//     const params = new URLSearchParams(jobData);

//     try {
//       fetch("http://localhost:5000/add_job", {
//           method: "POST",
//           headers: { "Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json" },
//           body: params.toString()
//         })
//         .then(response => response.json())  // Expect a JSON response
//         .then(result => {
//           if (result.success) {
//             alert("Job saved successfully!");
//             container.remove(); // ✅ Close the popup after successful save
//             style.remove();
//           } else {
//             console.error("Server Response Error:", result);
//             alert(`Error: ${result.message || "Job could not be saved."}`);
//           }
//         })
//         .catch(error => {
//           console.error("Fetch Error:", error);
//           alert("Failed to save job. Check backend connection.");
//         });

//       // Try to parse the response
//       const result = await response.json();

//       if (response.ok && result.success) {
//         alert("Job saved successfully!");
//         container.remove(); // ✅ Close the popup after successful save
//         style.remove();
//       } else {
//         console.error("Server Response Error:", result);
//         alert(`Error: ${result.message || "Job could not be saved."}`);
//       }
//     } catch (error) {
//       console.error("Fetch Error:", error);
//       alert("Failed to save job. Check backend connection.");
//     }
//   });

//   // Make the panel draggable
//   let isDragging = false;
//   let offset = { x: 0, y: 0 };

//   container.addEventListener('mousedown', function(e) {
//     if (e.target === container || e.target === header || e.target === closeBtn) {
//       isDragging = true;
//       offset.x = container.offsetLeft - e.clientX;
//       offset.y = container.offsetTop - e.clientY;
//     }
//   });

//   document.addEventListener('mouseup', function() {
//     isDragging = false;
//   });

//   document.addEventListener('mousemove', function(e) {
//     if (isDragging) {
//       container.style.left = (e.clientX + offset.x) + 'px';
//       container.style.top = (e.clientY + offset.y) + 'px';
//     }
//   });
// }
chrome.action.onClicked.addListener(async (tab) => {
  if (!tab || !tab.id) return;
  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    function: togglePanel
  });
});

function togglePanel() {
  const existing = document.getElementById('jobSaverContainer');
  if (existing) {
    existing.remove();
    return;
  }

  // Inject styling dynamically
  const style = document.createElement('style');
  style.textContent = `
    #jobSaverContainer {
      position: fixed;
      top: 80px;
      right: 40px;
      width: 400px;
      max-height: 85vh;
      background-color: #ffffff;
      border: 1px solid #ddd;
      border-radius: 10px;
      box-shadow: 0 8px 16px rgba(0,0,0,0.2);
      z-index: 999999;
      overflow-y: auto;
      padding: 20px;
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }
    #jobSaverHeader {
      font-size: 24px;
      font-weight: 600;
      margin-bottom: 20px;
      text-align: center;
      position: relative;
    }
    #jobSaverClose {
      position: absolute;
      top: 0;
      right: 10px;
      font-size: 28px;
      cursor: pointer;
      color: #666;
    }
    #jobSaverForm .form-group {
      margin-bottom: 15px;
    }
    #jobSaverForm input,
    #jobSaverForm select,
    #jobSaverForm textarea {
      width: 100%;
      padding: 10px;
      font-size: 16px;
      border: 1px solid #ccc;
      border-radius: 6px;
      box-sizing: border-box;
      margin-bottom: 8px;
    }
    #jobSaverForm textarea {
      min-height: 100px;
      resize: vertical;
    }
    #jobSaverForm button.save-btn {
      width: 100%;
      padding: 12px;
      background-color: #0d6efd;
      border: none;
      color: #fff;
      font-size: 16px;
      border-radius: 6px;
      cursor: pointer;
      transition: background-color 0.3s ease;
      font-weight: 600;
    }
    #jobSaverForm button.save-btn:hover {
      background-color: #0b5ed7;
    }
  `;
  document.head.appendChild(style);

  // Create the container
  const container = document.createElement('div');
  container.id = 'jobSaverContainer';

  // Create header with close button
  const header = document.createElement('div');
  header.id = 'jobSaverHeader';
  header.textContent = 'Save Job';

  const closeBtn = document.createElement('span');
  closeBtn.id = 'jobSaverClose';
  closeBtn.innerHTML = '&times;';
  closeBtn.addEventListener('click', () => {
    container.remove();
    style.remove();
  });
  header.appendChild(closeBtn);
  container.appendChild(header);

  // Create the form
  const form = document.createElement('form');
  form.id = 'jobSaverForm';
  form.innerHTML = `
    <div class="form-group">
      <input type="text" id="jsJobTitle" name="title" placeholder="Job Title" required>
    </div>
    <div class="form-group">
      <input type="text" id="jsCompany" name="company" placeholder="Company" required>
    </div>
    <div class="form-group">
      <input type="text" id="jsLocation" name="location" placeholder="Location" required>
    </div>
    <div class="form-group">
      <select id="jsStatus" name="status" required>
        <option value="">Select Status</option>
        <option value="Bookmarked">Bookmarked</option>
        <option value="Applying">Applying</option>
        <option value="Applied">Applied</option>
        <option value="Interview">Interview</option>
        <option value="Negotiation">Negotiation</option>
        <option value="Offer">Offer</option>
      </select>
    </div>
    <div class="form-group">
      <textarea id="jsDescription" name="description" placeholder="Job Description"></textarea>
    </div>
    <button type="submit" class="save-btn">Save Job</button>
  `;
  container.appendChild(form);
  document.body.appendChild(container);

  // Handle form submission
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const jobData = {
      title: document.getElementById('jsJobTitle').value.trim(),
      company: document.getElementById('jsCompany').value.trim(),
      location: document.getElementById('jsLocation').value.trim(),
      status: document.getElementById('jsStatus').value,
      description: document.getElementById('jsDescription').value.trim()
    };

    const params = new URLSearchParams(jobData);

    try {
      const response = await fetch("http://localhost:5000/add_job", {
        method: "POST",
        headers: { 
          "Content-Type": "application/x-www-form-urlencoded", 
          "Accept": "application/json" 
        },
        body: params.toString()
      });

      const result = await response.json();

      if (response.ok && result.success) {
        alert("Job saved successfully!");
        
        // ✅ Use setTimeout to allow UI updates before closing
        setTimeout(() => {
          if (document.getElementById('jobSaverContainer')) {
            document.getElementById('jobSaverContainer').remove();
            style.remove();
          }
        }, 500); // Small delay to ensure visibility before closing
      } else {
        console.error("Server Response Error:", result);
        alert(`Error: ${result.message || "Job could not be saved."}`);
      }
    } catch (error) {
      console.error("Fetch Error:", error);
      alert("Failed to save job. Check backend connection.");
    }
  });

  // Make the panel draggable
  let isDragging = false;
  let offset = { x: 0, y: 0 };

  container.addEventListener('mousedown', function(e) {
    if (e.target === container || e.target === header || e.target === closeBtn) {
      isDragging = true;
      offset.x = container.offsetLeft - e.clientX;
      offset.y = container.offsetTop - e.clientY;
    }
  });

  document.addEventListener('mouseup', function() {
    isDragging = false;
  });

  document.addEventListener('mousemove', function(e) {
    if (isDragging) {
      container.style.left = (e.clientX + offset.x) + 'px';
      container.style.top = (e.clientY + offset.y) + 'px';
    }
  });
}
