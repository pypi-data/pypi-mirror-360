const response = await fetch(
  "https://api.github.com/repos/wizley9999/nali/contents/docs/status.json",
  {
    headers: {
      Accept: "application/vnd.github.raw+json",
    },
  }
);

const data = await response.json();

const statusElement = document.getElementById("status");

data.map((item) => {
  if (item.status) {
    statusElement.innerHTML += `
    <div class="flex items-center justify-between px-5 py-4">
      <div class="text-[#172B4D] text-base font-medium">${item.school}</div>
      <div class="text-[#36B37E] text-sm">Operational</div>
    </div>
    `;
  } else {
    statusElement.innerHTML += `
    <div class="px-5">
      <div class="flex items-center justify-between pt-4">
        <div class="text-[#172B4D] text-base font-medium">${item.school}</div>
        <div class="text-[#FF8B00] text-sm">Outage</div>
      </div>

      <div class="text-[#DC362E] text-xs pt-1 pb-4">
        ${item.error}
      </div>
    </div>
    `;
  }
});
