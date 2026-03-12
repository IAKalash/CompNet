from fastapi import FastAPI, HTTPException, Query
from parser import run_parser 
from database import init_db, save_to_db, get_all_from_db, clear_db


init_db()
app = FastAPI(title="GitHub Parser API")

@app.post("/parse")
def trigger_parsing(search_query: str = Query(...), pages: int = Query(1)):
    try:
        data = run_parser(search_query, pages)
        save_to_db(data)
        return {"status": "success", "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_data")
def get_parsed_data():
    return {"status": "success", "data": get_all_from_db()}

@app.delete("/clear")
def clear_all_data():
    try:
        clear_db()
        return {"status": "success", "message": "Таблица успешно очищена."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при очистке: {str(e)}")