document.getElementById('runDownload').addEventListener('click', function() {
    window.location.href = "{{ url_for('index.download_responses') }}";
});

function get_agent_response(ball_identifier, agent_name) {
    fetch(`{{ url_for('responses.get_agent_response') }}?ball_identifier=${ball_identifier}&agent_name=${agent_name}`)
    .then(response => response.text())
    .then(html => {
    const modal = document.createElement('div');
    modal.classList.add('modal', 'fade');
    modal.id = 'agentResponseModal';
    modal.tabIndex = -1;
    modal.innerHTML = `
        <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
            <h5 class="modal-title">Agent Response</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
            ${html}
            </div>
            <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
        </div>
        </div>
    `;
    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    modal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal);
    });
    })
    .catch(err => {
    console.error('Error fetching agent response:', err);
    alert('Error fetching agent response. Please try again later.');
    });
}

function setActiveNav(element) {
    var navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(function(navLink) {
        navLink.classList.remove('active');
    });
    element.classList.add('active');
}

function showEdit(element) {
    setActiveNav(element);
    document.getElementById('editSection').style.display = 'block';
    document.getElementById('responsesSection').style.display = 'none';
}

function showResponses(element) {
    setActiveNav(element);
    document.getElementById('editSection').style.display = 'none';
    document.getElementById('responsesSection').style.display = 'block';
}

function refreshResponses() {
    const responsesContainer = document.getElementById('responsesContainer');

    fetch('{{ url_for("get_responses") }}')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.text();
        })
        .then(html => {
            responsesContainer.innerHTML = html;
        })
        .catch(err => {
            responsesContainer.innerHTML = "<p class='text-danger'>Error loading responses. Please try again later.</p>";
            console.error('Error fetching responses:', err);
        });
}

function toggleStatusSpan() {
    const statusSpan = document.getElementById('progressContainer');
    const toggleButton = document.querySelector('button[onclick="toggleStatusSpan()"]');
    if (statusSpan.style.display === 'none') {
        statusSpan.style.display = 'block';
        toggleButton.innerText = 'Hide console output';
    } else {
        statusSpan.style.display = 'none';
        toggleButton.innerText = 'Show console output';
    }
}

function renderPayload(ball_identifier)
{
    window.open(`{{ url_for('responses.get_payload') }}?ball_identifier=${ball_identifier}`, '_blank');

}

function runLocalTest() {
    const runBtn = document.getElementById('runTestsBtn');
    const statusSpan = document.getElementById('testStatusSpan');
    const progressContainer = document.getElementById('progressContainer');
    const maxProcessedEvents = document.getElementById('maxProcessedEvents').value;

    runBtn.disabled = true;
    runBtn.innerText = 'Running...';
    statusSpan.innerText = 'Running tests...';
    progressContainer.innerHTML = '';

    const eventSource = new EventSource(`{{ url_for('responses.run_live_progress') }}?max_processed_events=${maxProcessedEvents}`);

    eventSource.onmessage = function(event) {
        const newLog = document.createElement('pre');
        newLog.textContent = event.data;
        progressContainer.appendChild(newLog);
        progressContainer.scrollTop = progressContainer.scrollHeight;
    };

    eventSource.onerror = function() {
        statusSpan.innerText = 'Tests encountered an error or completed.';
        runBtn.disabled = false;
        runBtn.innerText = 'ReRun';
        eventSource.close();
    };

    eventSource.addEventListener('complete', function() {
        statusSpan.innerText = 'Tests completed successfully.';
        runBtn.disabled = false;
        runBtn.innerText = 'ReRun';
        eventSource.close();
    });
}
