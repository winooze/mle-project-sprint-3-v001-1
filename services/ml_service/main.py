"""
FastAPI-приложение для модели оттока. 
Пример запуска из директории mle-project-sprint-3-v001/services/ml_service: 
uvicorn main:app --reload --port 8000 --host 0.0.0.0

Для просмотра докумеdockнтации API и совершения тестовых запросов зайти на http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, Body
try: 
    from fast_api_handler import FastApiHandler
except: 
    from .fast_api_handler import FastApiHandler

# Conditional Prometheus imports and initialization
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    from .prometheus_custom_metrics import main_app_predictions, neg_price_counter 
    PROMETHEUS_ENABLED = True
except ImportError:
    PROMETHEUS_ENABLED = False


# создаём FastAPI-приложение 
app = FastAPI()
# создаём обработчик запросов для API
app.handler = FastApiHandler() 


# инициализируем и запускаем экпортёр метрик 
if PROMETHEUS_ENABLED: 
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app)

@app.get("/")
def read_root(): 
    return {"service": "predict_estate_price"} 

@app.get("/api/healthcheck/")
def get_status():
    return {"status" : "ok"} 

@app.post("/api/score_estate/") 
def get_prediction_for_item(id: str, model_params: dict):
    """Функция для получения предсказания стоимости недвижимости.

    Args:
        id (str): Идентификатор лота.
        model_params (dict): Параметры лота, которые нужно передать в модель.

    Returns:
        dict: Предсказание цены.
    
    Пример запроса:  
        "id": "123",
            "model_params": {
                "is_apartment": false, 
                "studio": false, 
                "has_elevator": true, 
                "building_type_int": 4, 
                "floor": 5, 
                "kitchen_area": 8.0, 
                "living_area": 56.0, 
                "rooms": 2, 
                "total_area": 52.0, 
                "build_year": 2007, 
                "latitude": 55.72347640991211, 
                "longitude": 37.903202056884766, 
                "ceiling_height": 2.740000009536743, 
                "flats_count": 376, 
                "floors_total": 11 
            }
    """
    all_params = {
        "id": id,
        "model_params": model_params
    }
    response = app.handler.handle(all_params)
    price_pred = response['prediction'] 
    if PROMETHEUS_ENABLED: 
        main_app_predictions.observe(price_pred)
        if response['prediction'] < 0: 
            neg_price_counter.inc() 
    return response