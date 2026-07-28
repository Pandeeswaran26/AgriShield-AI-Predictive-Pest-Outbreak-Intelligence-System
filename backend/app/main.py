from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.database import Base, engine
from auth.router import router as auth_router

from .schemas import PredictionRequest
from .prediction import predict
from history.models import PredictionHistory
from history.router import router as history_router
from dashboard.router import router as dashboard_router
from recommendation.router import router as recommendation_router
from analytics.router import router as analytics_router
from assistant.router import router as assistant_router
from report.router import router as report_router
from explain.router import router as explain_router
from weather.router import router as weather_router
# Create database tables
Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="AgriShield AI API",
    description="Predictive Pest Outbreak Intelligence System",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Authentication Routes
app.include_router(auth_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to AgriShield AI API",
        "status": "Running"
    }


@app.get("/health")
def health():
    return {
        "status": "Healthy"
    }


from fastapi import HTTPException

@app.post("/predict")
def predict_pest(request: PredictionRequest):
    try:
        return predict(request)
    except Exception as e:
        print("========== ERROR ==========")
        print(e)
        print("===========================")
        raise HTTPException(status_code=400, detail=str(e))

app.include_router(history_router)
app.include_router(dashboard_router)
app.include_router(analytics_router)
app.include_router(recommendation_router)
app.include_router(assistant_router)
app.include_router(report_router)
app.include_router(explain_router)
app.include_router(weather_router)