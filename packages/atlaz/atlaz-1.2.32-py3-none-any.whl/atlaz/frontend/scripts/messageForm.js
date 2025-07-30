// messageForm.js

const messageForm = document.getElementById('message-form');
const messageInput = document.getElementById('message-input');
const apiKeyInput = document.getElementById('api-key-input');
const llmProviderDropdown = document.getElementById('llm-provider-dropdown');
const llmModelInput = document.getElementById('llm-model-input');

// Elements for explanation display
const explanationSection = document.getElementById('explanation-section');
const explanationText = document.getElementById('explanation-text');
let lastExplanation = "";

// Show loading overlay
function showLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = 'flex';
}

// Hide loading overlay
function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = 'none';
}

// Fetch server version
async function fetchServerVersion() {
    try {
        const response = await fetch('http://127.0.0.1:5050/api/version');
        return (await response.json()).version;
    } catch (error) {
        console.error('Error fetching server version:', error);
        return null;
    }
}

// Fetch saved credentials
async function fetchSavedCredentials() {
    try {
        const response = await fetch('http://127.0.0.1:5050/api/get_credentials');
        return (response.ok ? await response.json() : {
            api_key: '',
            llm_provider: 'openai',
            model_choice: 'gpt-4'
        });
    } catch (error) {
        console.error('Error fetching saved credentials:', error);
        return {
            api_key: '',
            llm_provider: 'openai',
            model_choice: 'gpt-4'
        };
    }
}

// Load inputs from backend
async function loadInputsFromBackend() {
    const credentials = await fetchSavedCredentials();
    apiKeyInput.value = credentials.api_key || '';
    llmProviderDropdown.value = credentials.llm_provider || 'gemini';
    llmModelInput.value = credentials.model_choice || 'gpt-4';
    messageInput.value = localStorage.getItem('instruction') || '';
}

// Submit form handler
messageForm.addEventListener('submit', async function(event) {
    event.preventDefault();
    showLoadingOverlay();

    const messageText = messageInput.value.trim();
    const apiKey = apiKeyInput.value.trim();
    const llmProvider = llmProviderDropdown.value;
    const llmModel = llmModelInput.value.trim();
    const selectedPaths = gatherSelectedPaths();

    if (messageText && llmModel && apiKey) {
        const payload = {
            api_key: apiKey,
            llm_model: llmModel,
            llm_provider: llmProvider,
            message: messageText,
            selected_files: selectedPaths
        };

        // Remember the instruction locally
        localStorage.setItem('instruction', messageText);

        try {
            const response = await fetch('http://127.0.0.1:5050/send_data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();

            if (data.status === 'success') {
                // 1) Display explanation
                explanationSection.open = !!data.explanation;
                explanationText.textContent = data.explanation || '';
                lastExplanation = data.explanation || "";

                // 2) Clear the message input & stored instruction
                messageInput.value = '';
                localStorage.removeItem('instruction');

                // 3) Fetch the newly updated files.json to show the generated files
                fetch('files.json')
                    .then(res => res.json())
                    .then(files => {
                        console.log('Fetched updated files.json:', files);

                        // Here you can call your existing fileViewer logic
                        // or replicate the code that displays 'created' and 'replacing' files.
                        // For example:
                        // renderFiles(files);
                    })
                    .catch(err => {
                        console.error('Error loading files.json:', err);
                    });
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while sending the data.');
        } finally {
            hideLoadingOverlay();
        }
    } else {
        alert('Please enter the API key, LLM model, and a message before sending.');
        hideLoadingOverlay();
    }
});

async function loadExplanationIfExists() {
    try {
        const response = await fetch('explanation.txt');
        // If explanation.txt is missing, fetch will throw on non-OK response
        if (!response.ok) {
            throw new Error('No explanation file found');
        }
        const text = await response.text();
        
        // Grab the elements from the page
        const explanationSection = document.getElementById('explanation-section');
        const explanationText = document.getElementById('explanation-text');
        
        // Inject the file content
        explanationText.textContent = text;
        
        // Optionally expand the collapsible <details> so user can see it immediately
        explanationSection.open = true;

        console.log('Loaded explanation.txt successfully.');
    } catch (err) {
        console.log('Explanation file missing or other error:', err.message);
    }
}

// Initialize inputs on page load
document.addEventListener('DOMContentLoaded', async () => {
    const currentVersion = await fetchServerVersion();
    const storedVersion = localStorage.getItem('serverVersion');

    if (currentVersion) {
        if (storedVersion === currentVersion) {
            await loadInputsFromBackend();
        } else {
            localStorage.removeItem('instruction');
            localStorage.removeItem('lastExplanation');
            localStorage.setItem('serverVersion', currentVersion);
            await loadInputsFromBackend();
        }
    } else {
        await loadInputsFromBackend();
    }

    loadExplanationIfExists();
});