let items = [];  // This will hold the list of items
let selectedValues = [];  // This will hold the values selected in each dropdown

// Fetch the list from the backend
fetch('/get_list')
    .then(response => response.json())
    .then(data => {
        items = data;
    });

// Generate dropdowns based on the user input
function generateDropdowns() {
    const count = document.getElementById("dropdown-count").value;
    const container = document.getElementById("dropdown-container");
    container.innerHTML = '';  // Clear existing dropdowns

    for (let i = 0; i < count; i++) {
        const dropdown = document.createElement('select');
        dropdown.id = `dropdown-${i}`;
        dropdown.onchange = updateSelections;

        // Add an empty option as placeholder
        const placeholderOption = document.createElement("option");
        placeholderOption.value = "";
        placeholderOption.textContent = "--Select an item--";
        dropdown.appendChild(placeholderOption);

        // Populate dropdown with search capability
        items.forEach(item => {
            const option = document.createElement("option");
            option.value = item;
            option.textContent = item;
            dropdown.appendChild(option);
        });

        // Append the dropdown to the container
        container.appendChild(dropdown);
    }

    document.getElementById("amount-section").style.display = 'block';
    document.getElementById("submit-btn").style.display = 'none';
}

// Update selected values to avoid repetition
function updateSelections() {
    const count = document.getElementById("dropdown-count").value;
    selectedValues = Array.from({ length: count }, (_, i) => document.getElementById(`dropdown-${i}`).value);

    // Disable selected items in other dropdowns
    for (let i = 0; i < count; i++) {
        const dropdown = document.getElementById(`dropdown-${i}`);
        Array.from(dropdown.options).forEach(option => {
            option.disabled = selectedValues.includes(option.value) && option.value !== dropdown.value;
        });
    }

    if (selectedValues.every(value => value)) {
        document.getElementById("submit-btn").style.display = 'block';
    } else {
        document.getElementById("submit-btn").style.display = 'none';
    }
}

// Submit the data to the backend
function submitData() {
    const amount = document.getElementById("amount").value;
    if (!amount) {
        alert("Please enter an amount.");
        return;
    }

    const data = {
        selectedItems: selectedValues,
        amount: amount
    };

    fetch('/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        alert(result.message);
    });
}
