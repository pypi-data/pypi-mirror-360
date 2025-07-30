from setuptools import setup, find_packages
# Read README.md for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name="openmailer",
    version="0.1.9",
    description="Open-source email automation and delivery engine",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Mohamed Sesay",
    author_email="msesay@dee-empire.com",
    url="https://github.com/Devops-Bot-Official/OpenMailer.git",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "jinja2",                     # For templating
        "rich",                       # For terminal UI and progress tables
        "pyyaml",                     # For YAML parsing (if needed)
        "requests",                   # For any HTTP-based fallback or integrations
        "python-dotenv",             # ✅ .env file support
        "hvac",                      # ✅ HashiCorp Vault support
        "boto3",                     # ✅ AWS Secrets Manager
        "azure-identity",           # ✅ Azure Identity authentication
        "azure-keyvault-secrets",   # ✅ Azure Key Vault access
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.7",
)

