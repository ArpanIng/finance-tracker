const form = document.getElementById("category-form");
const nameField = document.getElementById("id_name");
const validationURL = form.getAttribute("data-validation-url");

nameField.addEventListener("input", async function () {
  const categoryName = this.value;

  // Clear existing error messages
  const existingError = nameField.nextElementSibling;
  if (existingError && existingError.classList.contains("invalid-feedback")) {
    existingError.remove();
    nameField.classList.remove("is-invalid");
  }

  if (categoryName) {
    try {
      const response = await fetch(validationURL, {
        method: "POST",
        body: JSON.stringify({ name: categoryName }),
      });

      if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
      }

      const data = await response.json();
      if (data.exists) {
        nameField.classList.add("is-invalid");
        const errDiv = document.createElement("p");
        errDiv.className = "invalid-feedback";
        const strongTag = document.createElement("strong");
        strongTag.innerText = "Category with this Name already exists.";
        errDiv.appendChild(strongTag);
        nameField.after(errDiv);
      } else {
        console.log("no");
      }
      console.log(data);
    } catch (error) {
      console.error("Error:", error);
    }
  }
});
