const urlInput = document.getElementById("urlInput");
const scanButton = document.getElementById("scanButton");

const errorMessage = document.getElementById("errorMessage");
const loading = document.getElementById("loading");
const resultCard = document.getElementById("resultCard");

const prediction = document.getElementById("prediction");
const riskLevel = document.getElementById("riskLevel");
const legitimateProbability = document.getElementById("legitimateProbability");
const phishingProbability = document.getElementById("phishingProbability");
const scannedUrl = document.getElementById("scannedUrl");
const resultIcon = document.getElementById("resultIcon");
const explanationList = document.getElementById("explanationList");
const assessmentNote = document.getElementById("assessmentNote");

scanButton.addEventListener("click", scanURL);

async function scanURL() {
    const url = urlInput.value.trim();

    // Clear previous messages
    errorMessage.textContent = "";
    resultCard.classList.add("hidden");
    explanationList.innerHTML = "";

    if (!url) {
        errorMessage.textContent = "Please enter a URL.";
        return;
    }

    // Show loading state
    loading.classList.remove("hidden");
    scanButton.disabled = true;
    scanButton.textContent = "Scanning...";

    try {
        const response = await fetch("http://127.0.0.1:5000/api/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                url: url
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Prediction failed.");
        }

        // Update result
        prediction.textContent = data.prediction;

        riskLevel.textContent = `Risk: ${data.risk}`;

        legitimateProbability.textContent =
            `${(data.legitimate_probability * 100).toFixed(2)}%`;

        phishingProbability.textContent =
            `${(data.phishing_probability * 100).toFixed(2)}%`;

        scannedUrl.textContent = data.url;

        // Update explanation
        explanationList.innerHTML = "";
        assessmentNote.textContent = data.assessment_note;

        data.explanation.forEach((reason) => {
            const li = document.createElement("li");
            li.textContent = reason;
            explanationList.appendChild(li);
        });

        // Update result icon
        if (data.prediction === "PHISHING") {
            resultIcon.textContent = "🚨";
        } else {
            resultIcon.textContent = "🛡️";
        }

        resultCard.classList.remove("hidden");

    } catch (error) {
        console.error(error);

        errorMessage.textContent =
            error.message || "Unable to connect to the server.";
    }

    finally {
        loading.classList.add("hidden");
        scanButton.disabled = false;
        scanButton.textContent = "Scan URL";
    }
}