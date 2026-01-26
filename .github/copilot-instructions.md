# 🏢 Professional Data Analysis System - Copilot Instructions

## Project Overview

This is an **enterprise-grade multi-file data analysis system** that demonstrates professional Python development practices including OOP, caching, Docker containerization, and modern Streamlit best practices.

### Key Features
- ✅ Multi-file analysis (3 Excel files: Payable, Invoices, Performa)
- ✅ SQLite database with SQLAlchemy ORM
- ✅ Automated Excel to CSV and DB migration
- ✅ Professional class-based architecture (DataManager, DataAnalyzer, CacheManager)
- ✅ Redis caching with in-memory fallback
- ✅ Docker containerization with docker-compose
- ✅ Interactive Streamlit dashboard with Plotly visualizations
- ✅ Production-ready error handling and logging
- ✅ Modular, testable, scalable codebase
- ✅ Package management with `uv`

---

## 📁 Project Structure

```
/Users/hamed/Documents/myprojects/JEC/
├── app/                          # Main application package
│   ├── __init__.py               # Package initialization
│   ├── models.py                 # Data models and enums
│   ├── cache.py                  # CacheManager for Redis/In-Memory
│   ├── data_manager.py           # DataManager for file operations
│   ├── analyzer.py               # DataAnalyzer for analysis operations
│   └── streamlit_dashboard.py    # Main Streamlit application
├── data/                         # Data directory
│   ├── Payable.xlsx              # Payable cheques data
│   ├── invoices.xlsx             # Invoices data
│   └── performa.xlsx             # Performa data
├── Dockerfile                    # Docker image definition
├── docker-compose.yml            # Multi-container orchestration
├── pyproject.toml                # Project configuration
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
├── INSTRUCTIONS.md               # Setup instructions
└── .dockerignore                 # Files to exclude from Docker
```

---

## 🏗️ Architecture Overview

### Class Hierarchy

```
CacheManager (app/cache.py)
  ├─ Redis backend (optional)
  └─ In-memory fallback

DataManager (app/data_manager.py)
  ├─ FILE_CONFIGS (FileType → FileConfig mapping)
  ├─ load_file(file_type) → DataFrame
  └─ load_all_files() → Dict[FileType, DataFrame]

DataAnalyzer (app/analyzer.py)
  ├─ analyze(file_type, analysis_type) → AnalysisResult
  ├─ _analyze_daily_breakdown()
  ├─ _analyze_cumulative()
  ├─ _analyze_top_beneficiaries()
  └─ _analyze_summary_stats()
```

### Models (app/models.py)

```python
FileType (Enum):           # Supported files: PAYABLE, INVOICES, PERFORMA
AnalysisType (Enum):       # Analysis types: DAILY_BREAKDOWN, CUMULATIVE, TOP_BENEFICIARIES, SUMMARY_STATS
FileConfig (Dataclass):    # File configuration with path, sheet, columns
AnalysisResult (Dataclass): # Result with file_type, analysis_type, data, timestamp, cache_key
```

---

## 🚀 Running the Application

### Option 1: Docker (Recommended)

```bash
# Build and start with Redis
docker-compose up --build

# Access dashboard at http://localhost:8501
# Redis at localhost:6379
```

### Option 2: Local Development

```bash
# Navigate to project
cd /Users/hamed/Documents/myprojects/JEC

# Install dependencies using uv
uv sync

# Run dashboard
uv run streamlit run app/streamlit_dashboard.py
```

### Option 3: With Redis (Local)

```bash
# Start Redis (requires Redis installed)
redis-server

# In another terminal
source .venv/bin/activate
export REDIS_HOST=localhost
export REDIS_PORT=6379
streamlit run app/streamlit_dashboard.py
```

---

## 📚 Code Examples

### Using DataManager

```python
from app import DataManager, FileType

manager = DataManager()

# Load specific file
df = manager.load_file(FileType.PAYABLE)

# Load all files
all_files = manager.load_all_files()

# Get file info
info = manager.get_file_info(FileType.INVOICES)
print(f"Rows: {info['rows']}, Columns: {info['columns']}")
```

### Using DataAnalyzer

```python
from app import DataAnalyzer, DataManager, FileType, AnalysisType

manager = DataManager()
analyzer = DataAnalyzer(manager)

# Perform analysis
result = analyzer.analyze(FileType.PAYABLE, AnalysisType.SUMMARY_STATS)
print(result.data)

# Get all analyses for a file
all_analyses = analyzer.get_all_analyses(FileType.INVOICES)
```

### Using CacheManager

```python
from app import CacheManager

cache = CacheManager(ttl_seconds=3600)

# Store value
cache.set("my_key", {"data": [1, 2, 3]})

# Retrieve value
value = cache.get("my_key")

# Get cache info
info = cache.get_cache_info()
```

---

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t jec-analysis:latest .
```

### Run Single Container

```bash
docker run -p 8501:8501 jec-analysis:latest
```

### Docker Compose (Recommended)

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Clean up volumes
docker-compose down -v
```

### Environment Variables

```
REDIS_HOST: localhost (default)
REDIS_PORT: 6379 (default)
REDIS_DB: 0 (default)
STREAMLIT_SERVER_PORT: 8501
STREAMLIT_SERVER_ADDRESS: 0.0.0.0
```

---

## 🔧 Configuration

### Adding New File Types

1. **Add to FileType enum** (app/models.py):
```python
class FileType(Enum):
    PAYABLE = "Payable"
    INVOICES = "Invoices"
    PERFORMA = "Performa"
    NEW_FILE = "New File"  # Add here
```

2. **Add config** (app/data_manager.py):
```python
FileType.NEW_FILE: FileConfig(
    file_type=FileType.NEW_FILE,
    filepath="data/new_file.xlsx",
    sheet_index=0,
    description="New File Analysis",
)
```

3. **Add analysis** (app/analyzer.py):
```python
# Implement _analyze_* method if needed
```

### Customizing CacheManager

```python
# Use Redis
import redis
redis_client = redis.Redis(host='localhost', port=6379)
cache = CacheManager(redis_client=redis_client, ttl_seconds=7200)

# Use in-memory (default)
cache = CacheManager(ttl_seconds=3600)
```

---

## 🧪 Testing

### Unit Testing Example

```python
import pytest
from app import DataManager, FileType

def test_data_manager_load():
    manager = DataManager()
    df = manager.load_file(FileType.PAYABLE)
    assert df is not None
    assert len(df) > 0
```

### Running Tests

```bash
pytest -v
```

---

## 📊 Analysis Types

### 1. Daily Breakdown
- Groups data by date
- Calculates sum, count, mean per day
- Renders as bar chart

### 2. Cumulative Analysis
- Calculates cumulative sums over time
- Shows trends and growth patterns
- Renders as line chart

### 3. Top Beneficiaries/Categories
- Groups by category column
- Sorts by amount
- Shows top N items
- Renders as horizontal bar chart

### 4. Summary Statistics
- Count of rows and columns
- Memory usage
- Null values
- Numeric statistics (mean, std, min, max)

---

## 🔐 Best Practices Implemented

### ✅ Code Organization
- Modular classes with single responsibility
- Type hints throughout
- Comprehensive docstrings
- Logging at appropriate levels

### ✅ Performance
- Redis caching for frequently accessed analyses
- In-memory fallback for offline scenarios
- Lazy loading of data
- Streamlit caching decorators

### ✅ Error Handling
- Try-except blocks with logging
- Graceful fallbacks
- User-friendly error messages
- No silent failures

### ✅ Security
- No hardcoded credentials
- Environment variables for configuration
- Input validation
- SQL injection prevention (pandas operations)

### ✅ Scalability
- Horizontally scalable with Redis
- Containerized with Docker
- Resource limits in docker-compose
- Memory-efficient data handling

---

## 🚀 Deployment

### Local Deployment
```bash
streamlit run app/streamlit_dashboard.py
```

### Docker Deployment
```bash
docker-compose up -d
```

### Cloud Deployment

#### Streamlit Cloud
```bash
git push origin main  # Deploy to Streamlit Cloud
```

#### AWS ECS
```bash
aws ecr create-repository --repository-name jec-analysis
docker tag jec-analysis:latest <account-id>.dkr.ecr.<region>.amazonaws.com/jec-analysis:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/jec-analysis:latest
```

#### Heroku
```bash
heroku create jec-analysis
git push heroku main
```

---

## 📝 Development Guidelines

### Adding New Features

1. **Add model** if needed (app/models.py)
2. **Extend DataManager** if data loading required (app/data_manager.py)
3. **Extend DataAnalyzer** for new analyses (app/analyzer.py)
4. **Update dashboard** with new UI (app/streamlit_dashboard.py)

### Code Style

- Use type hints: `def func(param: str) -> Dict[str, Any]:`
- Follow PEP 8
- Use logging instead of print statements
- Write docstrings for all classes and methods
- Keep methods under 50 lines when possible

### Testing Checklist

- [ ] Unit tests for new methods
- [ ] Integration tests for workflows
- [ ] Error handling tested
- [ ] Performance validated
- [ ] Docker build successful

---

## 🆘 Troubleshooting

### Redis Connection Error
```
Solution: Start Redis or use in-memory mode
docker-compose up redis
```

### Port Already in Use
```bash
# Kill process on port 8501
lsof -ti:8501 | xargs kill -9
```

### Out of Memory
```bash
# Increase Docker memory limit
docker-compose down
# Increase in docker-compose.yml
```

### Data File Not Found
```bash
# Verify file exists
ls -l data/
```

---

## 📖 References

- [Streamlit Docs](https://docs.streamlit.io/)
- [Pandas Docs](https://pandas.pydata.org/docs/)
- [Redis Python Client](https://redis-py.readthedocs.io/)
- [Docker Docs](https://docs.docker.com/)
- [Python OOP Best Practices](https://realpython.com/inheritance-composition-python/)

---

## 📞 Support

For issues, questions, or contributions:
1. Check existing documentation
2. Review code comments
3. Check logs: `docker-compose logs app`
4. Test components individually

---

## 🎯 Version Info

- **Version**: 2.0.0
- **Python**: 3.9+
- **Latest Update**: January 23, 2026
- **Status**: Production Ready ✅

---

## 🏆 Professional Practices Demonstrated

✅ Enterprise-grade OOP architecture
✅ Design patterns (Singleton, Factory, Repository)
✅ Type safety with type hints
✅ Comprehensive logging
✅ Redis caching integration
✅ Docker containerization
✅ Error handling and validation
✅ Code organization and modularity
✅ Streamlit best practices
✅ Professional documentation
✅ Development guidelines
✅ Testing strategies
✅ Deployment options
✅ Security considerations
✅ Performance optimization
