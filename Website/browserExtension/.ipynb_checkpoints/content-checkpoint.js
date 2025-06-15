chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "addJob" && message.jobData) {
    addJobToPage(message.jobData);
    sendResponse({ status: "success" });
  }
});

function addJobToPage(job) {
  const jobTable = document.getElementById("jobTableBody");
  if (!jobTable) return;

  const row = jobTable.insertRow();
  row.innerHTML = `
    <td>${job.title}</td>
    <td>${job.company}</td>
    <td>${job.location}</td>
    <td>${job.status}</td>
    <td>${job.description}</td>
    <td>
      <button class="delete-btn">🗑</button>
    </td>
  `;

  row.querySelector(".delete-btn").addEventListener("click", () => {
    row.remove();
  });
}
