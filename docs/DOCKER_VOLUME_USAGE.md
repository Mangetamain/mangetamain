# Docker Volume Setup for Preprocessed Data

## Overview
This setup allows you to either use preprocessed data from Docker Hub or rebuild it locally.

## Usage

### Option 1: Use Preprocessed Data from Docker Hub (Recommended)
```bash
# Pull and use preprocessed data from Docker Hub
docker-compose --profile use-prebuilt up
```

### Option 2: Rebuild Preprocessed Data Locally
```bash
# Rebuild preprocessing data and update the volume
docker-compose --profile rebuild-data up
```

### Option 3: Run Tests with Preprocessed Data
```bash
# Use preprocessed data and run tests
docker-compose --profile use-prebuilt --profile testing up
```

## Building and Pushing Data Volume (For Maintainers)

### Build the data volume image:
```bash
docker build -f Dockerfile.data -t andranik777/mangetamain-data:latest .
```

### Push to Docker Hub:
```bash
docker push andranik777/mangetamain-data:latest
```

## Volume Management

### View volume contents:
```bash
docker run --rm -v mangetamain_preprocessed_data:/data alpine ls -la /data
```

### Clean up volumes:
```bash
docker volume prune
```

## Architecture
- `andranik777/mangetamain-data:latest` - Docker Hub image containing preprocessed data
- `preprocessed_data` - Docker volume shared between services
- Profiles control which services run:
  - `use-prebuilt` - Downloads data from Docker Hub
  - `rebuild-data` - Rebuilds data locally
  - `testing` - Runs tests