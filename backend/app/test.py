from fastapi import FastAPI


app = FastAPI()

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("test:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")

@app.get("/")
def read_root():
    return {"Hello": "World"}