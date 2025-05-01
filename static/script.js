function handleFormSubmit(event) {
    event.preventDefault();

    Swal.fire({
        title: 'Processing...',
        text: 'Please wait while your file is being anonymized.',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });

    const form = event.target;
    const formData = new FormData(form);

    fetch(form.action, {
        method: "POST",
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error('Processing failed');
        return response.blob();
    })
    .then(blob => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = "anonymized_file.csv";
        document.body.appendChild(a);
        a.click();
        a.remove();

        Swal.fire({
            title: 'Success!',
            text: 'Your anonymized file is ready for download.',
            icon: 'success'
        });

        form.reset();
    })
    .catch(error => {
        Swal.fire('Error', error.message, 'error');
    });
}


function previewHeaders() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        Swal.fire("Error", "Please select a CSV file first.", "error");
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch('/preview_headers', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            Swal.fire("Error", data.error, "error");
        } else {
            const columns = data.columns;

            let html = "<p>Click a column name to add it to Sensitive Columns:</p><ul>";
            columns.forEach(col => {
                html += `<li style='cursor:pointer;color:#007bff;' onclick='addSensitiveColumn("${col}")'>${col}</li>`;
            });
            html += "</ul>";

            Swal.fire({
                title: "Available Columns",
                html: html,
                showConfirmButton: false,
                width: 500
            });
        }
    })
    .catch(err => {
        Swal.fire("Error", err.message, "error");
    });
}

function addSensitiveColumn(columnName) {
    const input = document.querySelector('input[name="sensitive_columns"]');
    let current = input.value.split(",").map(s => s.trim()).filter(Boolean);
    if (!current.includes(columnName)) {
        current.push(columnName);
        input.value = current.join(", ");
    }
}
