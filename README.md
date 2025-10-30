# MangeTaMain - Recipe Recommendation System

A Streamlit-based recipe recommendation system with Docker containerization and preprocessed data distribution via Docker Hub.

## 🌟 Live Demo

**Try the application now!**

[![🚀 Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-Try%20Now-brightgreen?style=for-the-badge)](https://mangetamain-production.up.railway.app/)

Click the button above to access the live application deployed on Railway.


## 📚 Documentation & Tests Coverage
[![Guithub Pages](https://img.shields.io/badge/GitHub%20Pages-View%20Online-blue?style=for-the-badge)](https://mangetamain.github.io/mangetamain/)

[![Sphinx Docs for Application Streamlit](https://img.shields.io/badge/Sphinx%20API%20Docs%20for%20Application%20Streamlit%20-View%20Online-blue?style=for-the-badge)](https://mangetamain.github.io/mangetamain/streamlit/index.html)

[![Sphinx Docs for Module Preprocessing](https://img.shields.io/badge/Sphinx%20API%20Docs%20for%20Preprocessing%20Module%20-View%20Online-blue?style=for-the-badge)](https://mangetamain.github.io/mangetamain/preprocessing/index.html)    

[![Test Coverage](https://img.shields.io/badge/Test%20Coverage-Report-green?style=for-the-badge)](https://mangetamain.github.io/mangetamain/coverage/index.html)

- [Docker Volume Usage](docs/DOCKER_VOLUME_USAGE.md) - Detailed volume management
- [Architecture](docs/ARCHITECTURE.md) - System architecture
- [Tests](docs/TESTS_README.md) - Testing information

## 🚀 Quick Start

### Option 1: Use Prebuilt Data (Recommended)
```bash
docker-compose --profile use-prebuilt up -d
```
- ✅ Pulls preprocessed data from Docker Hub (`andranik777/mangetamain-data:latest`)
- ✅ Instant startup with preprocessed data from Docker Hub
- ✅ App available at http://localhost:8501
- ✅ No waiting time (~1.2GB data downloaded once)

### Option 2: Rebuild Data Locally
```bash
docker-compose --profile rebuild-data up -d
```
- 🔄 Processes raw data locally (~5-10 minutes)
- 🔄 Updates shared volume with fresh preprocessed data
- 🔄 Use when data needs to be updated

### Option 3: Testing Mode
```bash
docker-compose --profile testing up -d
```
- 🧪 Runs automated tests
- 🧪 Generates test reports

## 🛑 Stop Services
```bash
docker-compose down
```


## 🐳 Docker Hub
Preprocessed data is available at: `andranik777/mangetamain-data:latest`


### Railway Configuration
- ✅ **Dedicated Dockerfile**: `Dockerfile.railway` optimized specifically for Railway
- ✅ **Multi-stage build**: Integrates preprocessed data from Docker Hub
- ✅ **Automatic port configuration**: Railway sets `$PORT` variable automatically
- ✅ **Security**: Non-root user and proper healthchecks
- ✅ **Memory optimized**: Streamlit settings tuned for Railway environment

**Note**: `Dockerfile.railway` is Railway-specific. For local development, use `docker-compose.yml`.
