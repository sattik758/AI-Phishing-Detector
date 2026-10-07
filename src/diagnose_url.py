from feature_extraction import extract_features


urls = [
    "https://www.fakebook.com",
    "https://www.paypa1.com",
    "https://www.wifipedia.com",
    "http://secure-login.example.com/verify/account"
]


for url in urls:

    print("\n" + "=" * 70)
    print(f"URL: {url}")
    print("=" * 70)

    features = extract_features(url)

    for name, value in features.items():
        print(f"{name:25} : {value}")
        