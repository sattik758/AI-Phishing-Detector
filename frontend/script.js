const urlInput = document.getElementById("urlInput");
const scanButton = document.getElementById("scanButton");

const errorMessage = document.getElementById("errorMessage");
const loading = document.getElementById("loading");
const resultCard = document.getElementById("resultCard");

const prediction = document.getElementById("prediction");
const riskLevel = document.getElementById("riskLevel");
const riskBadge = document.getElementById("riskBadge");

const legitimateProbability =
    document.getElementById("legitimateProbability");

const phishingProbability =
    document.getElementById("phishingProbability");

const scannedUrl =
    document.getElementById("scannedUrl");

const resultIcon =
    document.getElementById("resultIcon");

const explanationList =
    document.getElementById("explanationList");

const assessmentNote =
    document.getElementById("assessmentNote");


// =====================================================
// Circular Probability Elements
// =====================================================

const probabilityCircle =
    document.getElementById("probabilityCircle");

const probabilityValue =
    document.getElementById("probabilityValue");

const probabilityLabel =
    document.getElementById("probabilityLabel");


// =====================================================
// Technical Analysis
// =====================================================

const technicalGrid =
    document.getElementById("technicalGrid");


// =====================================================
// Scanner Events
// =====================================================

scanButton.addEventListener("click", scanURL);


// Press ENTER to scan
urlInput.addEventListener("keydown", (event) => {

    if (event.key === "Enter") {

        event.preventDefault();

        scanURL();
    }
});


// =====================================================
// Circular Probability
// =====================================================

function setProbabilityCircle(
    probability,
    label,
    predictionType
) {

    const percentage =
        probability * 100;


    const degrees =
        Math.max(
            0,
            Math.min(
                360,
                percentage * 3.6
            )
        );


    probabilityCircle.style.setProperty(
        "--progress",
        `${degrees}deg`
    );


    probabilityValue.textContent =
        `${percentage.toFixed(2)}%`;


    probabilityLabel.textContent =
        label;


    probabilityCircle.classList.toggle(
        "legitimate",
        predictionType === "LEGITIMATE"
    );
}


// =====================================================
// Risk State
// =====================================================

function setRiskState(risk) {

    const normalizedRisk =
        String(risk).toLowerCase();


    riskBadge.textContent =
        risk;


    riskBadge.className =
        `risk-badge risk-${normalizedRisk}`;
}


// =====================================================
// Technical Analysis
// =====================================================

function populateTechnicalAnalysis(url) {

    technicalGrid.innerHTML = "";


    try {

        const parsed =
            new URL(url);


        const hostname =
            parsed.hostname;


        const pathname =
            parsed.pathname || "/";


        const query =
            parsed.search
                ? "Present"
                : "None";


        const fragment =
            parsed.hash
                ? "Present"
                : "None";


        const credentials =
            parsed.username || parsed.password
                ? "Present"
                : "None";


        const protocol =
            parsed.protocol
                .replace(":", "")
                .toUpperCase();


        const hostnameParts =
            hostname.split(".").filter(Boolean);


        const subdomainCount =
            Math.max(
                0,
                hostnameParts.length - 2
            );


        const digitCount =
            (hostname.match(/\d/g) || []).length;


        const pathDepth =
            pathname
                .split("/")
                .filter(Boolean)
                .length;


        const technicalData = [
            {
                label: "Protocol",
                value: protocol
            },
            {
                label: "Hostname",
                value: hostname
            },
            {
                label: "Hostname Length",
                value: hostname.length
            },
            {
                label: "Subdomains",
                value: subdomainCount
            },
            {
                label: "Digits in Hostname",
                value: digitCount
            },
            {
                label: "Path Depth",
                value: pathDepth
            },
            {
                label: "Query",
                value: query
            },
            {
                label: "Fragment",
                value: fragment
            },
            {
                label: "Credentials",
                value: credentials
            }
        ];


        technicalData.forEach((item) => {

            const card =
                document.createElement("div");

            card.className =
                "technical-item";


            const label =
                document.createElement("span");

            label.textContent =
                item.label;


            const value =
                document.createElement("strong");

            value.textContent =
                item.value;


            card.appendChild(label);
            card.appendChild(value);

            technicalGrid.appendChild(card);
        });


    } catch (error) {

        const message =
            document.createElement("p");

        message.className =
            "technical-error";

        message.textContent =
            "Technical URL details could not be parsed.";

        technicalGrid.appendChild(message);
    }
}


// =====================================================
// Main Scan Function
// =====================================================

async function scanURL() {

    const url =
        urlInput.value.trim();


    // Clear previous messages
    errorMessage.textContent = "";

    resultCard.classList.add("hidden");

    explanationList.innerHTML = "";

    assessmentNote.textContent = "";


    if (!url) {

        errorMessage.textContent =
            "Please enter a URL.";

        urlInput.focus();

        return;
    }


    // =================================================
    // Loading State
    // =================================================

    loading.classList.remove("hidden");

    scanButton.disabled = true;

    scanButton.textContent =
        "Analyzing...";


    try {

        const response =
            await fetch(
                "/api/predict",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        url: url
                    })
                }
            );


        const data =
            await response.json();


        // =================================================
        // API Error
        // =================================================

        if (!response.ok) {

            throw new Error(
                data.error ||
                "Prediction failed."
            );
        }


        // =================================================
        // Prediction
        // =================================================

        if (
            data.prediction === "PHISHING"
        ) {

            prediction.textContent =
                "POTENTIALLY PHISHING";

        } else {

            prediction.textContent =
                "LEGITIMATE";
        }


        // =================================================
        // Risk
        // =================================================

        riskLevel.textContent =
            `Application Risk: ${data.risk}`;


        setRiskState(data.risk);


        // =================================================
        // Probabilities
        // =================================================

        const legitimatePercent =
            data.legitimate_probability * 100;


        const phishingPercent =
            data.phishing_probability * 100;


        legitimateProbability.textContent =
            `${legitimatePercent.toFixed(2)}%`;


        phishingProbability.textContent =
            `${phishingPercent.toFixed(2)}%`;


        // =================================================
        // Main Circular Probability
        // =================================================

        const mainProbability =
            data.prediction === "PHISHING"
                ? data.phishing_probability
                : data.legitimate_probability;


        const mainLabel =
            data.prediction === "PHISHING"
                ? "Phishing Probability"
                : "Legitimate Probability";


        setProbabilityCircle(
            mainProbability,
            mainLabel,
            data.prediction
        );


        // =================================================
        // Scanned URL
        // =================================================

        scannedUrl.textContent =
            data.url;


        // =================================================
        // Technical Analysis
        // =================================================

        populateTechnicalAnalysis(
            data.url
        );


        // =================================================
        // Model Assessment
        // =================================================

        assessmentNote.textContent =
            data.assessment_note;


        // =================================================
        // Detected Signals
        // =================================================

        explanationList.innerHTML = "";


        data.explanation.forEach(
            (reason) => {

                const li =
                    document.createElement("li");


                li.textContent =
                    reason;


                explanationList.appendChild(li);
            }
        );


        // =================================================
        // Result Icon
        // =================================================

        if (
            data.prediction === "PHISHING"
        ) {

            resultIcon.textContent =
                "🚨";

        } else {

            resultIcon.textContent =
                "🛡️";
        }


        // =================================================
        // Result Card State
        // =================================================

        resultCard.classList.remove(
            "result-phishing",
            "result-legitimate"
        );


        if (
            data.prediction === "PHISHING"
        ) {

            resultCard.classList.add(
                "result-phishing"
            );

        } else {

            resultCard.classList.add(
                "result-legitimate"
            );
        }


        // =================================================
        // Show Result
        // =================================================

        resultCard.classList.remove(
            "hidden"
        );


        // =================================================
        // Scroll to Result
        // =================================================

        setTimeout(() => {

            resultCard.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }, 100);


    } catch (error) {

        console.error(error);


        errorMessage.textContent =
            error.message ||
            "Unable to connect to the server.";

    }


    // =================================================
    // Restore Scanner
    // =================================================

    finally {

        loading.classList.add("hidden");

        scanButton.disabled = false;

        scanButton.textContent =
            "Analyze →";
    }
}