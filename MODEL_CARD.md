# Model Card — AI Phishing Detection System

## 1. Model Overview

This project is a machine-learning-based phishing URL detection system.

The system analyzes URL characteristics and uses a Random Forest classifier to estimate whether a URL resembles a legitimate or phishing URL according to patterns learned from the training dataset.

### Model

- Algorithm: Random Forest Classifier
- Version: V2
- Number of features: 34
- Task: Binary classification
- Class `0`: Legitimate
- Class `1`: Phishing

The final model is stored as:

```text
model/final_model.pkl
```

---

## 2. Intended Use

The model is intended for:

- Educational cybersecurity research
- Phishing URL analysis
- Machine learning experimentation
- Security awareness tools
- Demonstration of URL-based threat detection
- Academic and project portfolio purposes

The model should be treated as a **risk-assessment component**, not as a definitive security authority.

---

## 3. Dataset

The model was trained and evaluated using the **UCI PhiUSIIL Phishing URL Dataset**.

### Dataset Statistics

- Total URLs: 235,370
- Legitimate URLs: 134,850
- Phishing URLs: 100,520
- Unique domains: 175,509
- Missing URLs after preprocessing: 0
- Duplicate URLs after preprocessing: 0

### Label Mapping

```text
0 = Legitimate
1 = Phishing
```

---

## 4. Feature Engineering

The V2 feature extractor generates 34 URL-based features.

These features describe different characteristics of the submitted URL, including:

- URL length
- Hostname length
- Domain length
- Path length
- Query length
- Fragment length
- Dot count
- Hyphen count
- Underscore count
- Slash count
- Query parameter characteristics
- Digit count
- Letter count
- HTTPS usage
- IP address usage
- Subdomain count
- Suspicious security-related words
- Domain entropy
- Path depth
- Punycode usage
- Percent encoding
- Brand similarity
- Digit substitution
- Exact brand matching
- Brand lookalike characteristics

The features are extracted directly from the URL and do not require the application to visit or execute the submitted website.

---

## 5. Model Architecture

The final model uses a Random Forest classifier.

### Configuration

```text
n_estimators = 200
random_state = 42
n_jobs = -1
class_weight = balanced
```

The V2 feature set was developed as an improvement over the original V1 feature set.

The V1 and V2 models were compared using the same domain-aware evaluation methodology.

V2 was selected as the final model because it achieved better recall and F1 score while reducing false negatives on the same evaluation split.

---

## 6. Evaluation Methodology

A **domain-aware holdout evaluation** was used to evaluate the final model.

URLs belonging to the same registered domain were kept within the same train/test group.

This reduces the possibility of the model seeing URLs from the same domain during both training and testing.

### Evaluation Split

```text
Total URLs:        235,370

Training URLs:     191,335
Testing URLs:       44,035

Training domains:  140,407
Testing domains:    35,102

Domain overlap:          0
```

The split was created using:

```text
GroupShuffleSplit
test_size = 0.20
random_state = 42
```

The resulting test set contained URLs from domains that were not present in the training set.

---

## 7. Final Performance

The final V2 Random Forest achieved the following results on the domain-aware holdout set.

| Metric | Result |
|---|---:|
| Accuracy | 99.69% |
| Precision | 99.81% |
| Recall | 99.39% |
| F1 Score | 99.60% |
| False Positives | 33 |
| False Negatives | 105 |

### Confusion Matrix

```text
                  Predicted
                Legit   Phishing

Actual Legit    26915       33
Actual Phishing   105    16982
```

The evaluation contained **zero domain overlap** between the training and testing sets.

### Classification Report

```text
              precision    recall  f1-score   support

  Legitimate       1.00      1.00      1.00     26948
    Phishing       1.00      0.99      1.00     17087

    accuracy                           1.00     44035
   macro avg       1.00      1.00      1.00     44035
weighted avg       1.00      1.00      1.00     44035
```

The displayed classification report rounds the values to two decimal places. The more precise overall metrics are reported above.

---

## 8. Model Comparison

The V2 feature set was compared against the original V1 feature set using the same domain-aware test split.

### V1

```text
Accuracy:  99.55%
Precision: 99.81%
Recall:    99.02%
F1 Score:  99.41%

False Positives: 33
False Negatives: 167
```

### V2

```text
Accuracy:  99.69%
Precision: 99.81%
Recall:    99.39%
F1 Score:  99.60%

False Positives: 33
False Negatives: 105
```

V2 reduced false negatives from **167 to 105**, representing a reduction of 62 false negatives on the same domain-aware test split.

Therefore, V2 was selected as the final model.

---

## 9. Important Limitations

### 9.1 URL-Only Analysis

The model primarily analyzes URL characteristics.

It does not directly inspect:

- Website HTML
- Page content
- JavaScript behavior
- DNS reputation
- WHOIS information
- TLS certificate reputation
- Redirect chains
- Domain registration age
- External threat-intelligence feeds
- Website behavior after visiting the URL

Therefore, the model cannot provide a complete assessment of website safety.

---

### 9.2 Benchmark Performance Is Not Real-World Accuracy

The reported 99.69% accuracy represents performance on the domain-aware holdout portion of the UCI PhiUSIIL dataset.

It should **not** be interpreted as:

> "The system detects 99.69% of real-world phishing URLs."

Real-world performance may differ because of:

- Unseen domains
- Changes in attacker behavior
- Dataset bias
- Dataset labeling characteristics
- Distribution shift
- New phishing techniques
- URLs that differ significantly from the training data

The model should therefore be considered a benchmarked URL-based classifier rather than a complete real-world phishing detection solution.

---

### 9.3 Dataset Label Characteristics

The dataset contains URLs involving well-known brands and online services.

During dataset auditing, some well-known registered domains were found with phishing labels.

For example, `google.com` appeared as a registered domain in the dataset with phishing labels.

This demonstrates that a domain name and the security classification of an individual URL are not necessarily equivalent.

The project does not manually change dataset labels based on external assumptions. The original dataset labels are preserved for reproducibility and evaluation integrity.

---

### 9.4 Brand Lookalike Detection

The V2 model includes features for:

- Brand similarity
- Digit substitution
- Exact brand matching
- Brand lookalike scoring

These features can provide additional signals for URLs that resemble known brands.

However, they do not guarantee reliable detection of every typosquatting or brand-impersonation attempt.

---

### 9.5 Explainability

The application provides rule-based explanations based on selected URL characteristics.

These explanations are intended to help users understand some of the suspicious signals detected in the URL.

They should not be interpreted as a complete explanation of the Random Forest's internal decision process.

---

### 9.6 Risk Thresholds

The application maps phishing probability to three application-level risk categories:

```text
LOW
MEDIUM
HIGH
```

These thresholds are application-level decisions and have not been independently calibrated as production security decision thresholds.

---

## 10. Responsible Use

This system should be used as a supporting security analysis tool.

A prediction of:

```text
PHISHING
```

does not independently prove that a URL is malicious.

Likewise, a:

```text
LEGITIMATE
```

prediction does not guarantee that a website is safe.

High-risk security decisions should use additional evidence such as:

- Threat intelligence
- Domain reputation
- DNS information
- Certificate information
- Sandbox analysis
- Website content analysis
- Redirect analysis
- Security analyst review

Users should avoid visiting suspicious URLs simply to test the classifier.

---

## 11. Security Considerations

The application performs URL feature extraction without intentionally browsing to or executing the submitted URL.

The Flask API implements basic security headers including:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
```

Input validation is also implemented for:

- Missing URLs
- Empty URLs
- Non-string input
- URLs exceeding the configured length limit

The application therefore performs basic defensive input handling before passing the URL to the prediction pipeline.

---

## 12. Testing

The project includes automated tests covering:

- Feature extraction
- Prediction logic
- API behavior
- Input validation
- Security headers

### Current Test Status

```text
18 tests
18 passed
0 failed
```

The complete test suite was executed using Python's `unittest` discovery mechanism.

---

## 13. Future Improvements

Potential future improvements include:

- Domain reputation integration
- DNS-based features
- WHOIS and domain-age features
- TLS certificate analysis
- Redirect-chain analysis
- External threat-intelligence integration
- HTML/content-based phishing detection
- Better probability calibration
- Larger and more diverse datasets
- Additional external validation datasets
- More robust out-of-distribution evaluation
- Ensemble approaches combining multiple security signals

Future improvements should be evaluated against the current V2 model rather than replacing the baseline without comparison.

---

## 14. Model Status

**Status: Frozen Baseline**

The V2 Random Forest is currently treated as the project's validated baseline model.

The baseline should be preserved for future comparison.

### Final Baseline

```text
Model: Random Forest V2
Features: 34

Accuracy: 99.69%
Precision: 99.81%
Recall: 99.39%
F1 Score: 99.60%

False Positives: 33
False Negatives: 105

Domain overlap: 0
```

Future models should demonstrate measurable improvement using an equivalent or stronger evaluation methodology before replacing this baseline.