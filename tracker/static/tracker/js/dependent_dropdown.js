const form = document.getElementById("transaction-form");
const typeField = document.getElementById("id_type");
const categoryField = document.getElementById("id_category");
const url = form.getAttribute("data-url");

typeField.addEventListener("change", async function () {
  let type = typeField.value;

  try {
    const response = await fetch(`${url}?type=${type}`);

    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }

    const data = await response.json();
    categoryField.innerHTML = '<option value="">Select Category</option>';
    data.forEach((item) => {
      const option = document.createElement("option");
      option.value = item.id;
      option.textContent = item.name;
      categoryField.appendChild(option);
    });
  } catch (error) {
    console.error("Error:", error);
  }
});
