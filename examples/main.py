import sqlite3

from config import settings
from data import SQLRepository
from fastapi import FastAPI
from model import GarchModel
from pydantic import BaseModel


# Task 8.4.14, `FitIn` class
class FitIn(BaseModel):
    """Input data for fitting a GARCH model.

    Attributes
    ----------
    ticker : str
        Stock ticker symbol.
    use_new_data : bool
        Whether to use new data for fitting the model.
    n_observations: int
    p: int
    q: int
    """
    ticker: str
    use_new_data: bool
    n_observations: int
    p: int
    q: int


# Task 8.4.14, `FitOut` class
class FitOut(FitIn):
    """Output data after fitting a GARCH model.

    Attributes
    ----------
    success : bool
        Whether the model was successfully fitted.
    message : str
        Message indicating the result of the fitting process.
    """
    success: bool
    message: str


# Task 8.4.18, `PredictIn` class
class PredictIn(BaseModel):
    """Input data for predicting with a GARCH model.

    Attributes
    ----------
    ticker : str
        Stock ticker symbol.
    n_days: int
    """
    ticker: str
    n_days: int


# Task 8.4.18, `PredictOut` class
class PredictOut(PredictIn):
    """Output data after predicting with a GARCH model.
    Attributes
    ----------
    success : bool
        Whether the model was successfully fitted.
    message : str
        Message indicating the result of the fitting process.
    forecast : dict
        Dictionary containing the forecasted values.
    """
    success: bool
    message: str
    forecast: dict


# Task 8.4.15
def build_model(ticker, use_new_data=False):
    # Create DB connection
    connection = sqlite3.connect(settings.db_name)

    # Create `SQLRepository`
    repo = SQLRepository(connection)

    # Create model
    model = GarchModel(ticker, repo, use_new_data)

    # Return model
    return model


# Task 8.4.9
app = FastAPI()


# Task 8.4.11
# `"/hello" path with 200 status code
@app.get("/hello", status_code=200)
def hello():
    """Return dictionary with greeting message."""
    return {"Hello": "World"}


# Task 8.4.16, `"/fit" path, 200 status code
@app.post("/fit", status_code=200, response_model=FitOut)
def fit_model(request: FitIn):
    """Fit model, return confirmation message.

    Parameters
    ----------
    request : FitIn

    Returns
    ------
    dict
        Must conform to `FitOut` class
    """
    # Create `response` dictionary from `request`
    response = request.dict()

    # Create try block to handle exceptions
    try:
        # Build model with `build_model` function
        model = build_model(ticker=request.ticker, use_new_data=request.use_new_data)

        # Wrangle data
        model.wrangle_data(n_observations=request.n_observations)

        # Fit model
        model.fit(request.p, request.q)

        # Save model
        filename = model.dump()

        # Add `"success"` key to `response`
        response['success'] = True

        # Add `"message"` key to `response` with `filename`
        response['message'] = f"Trained and saved {filename}.Metrics: AIC {model.aic}, BIC {model.bic}."


    # Create except block
    except Exception as e:
        # Add `"success"` key to `response`
        response['success'] = False

        # Add `"message"` key to `response` with error message
        response['message'] = str(e)

    # Return response
    return response


# Task 8.4.19 `"/predict" path, 200 status code
@app.post("/predict", status_code=200, response_model=PredictOut)
def get_prediction(request: PredictIn):
    # Create `response` dictionary from `request`
    response = request.dict()
    # Create try block to handle exceptions
    try:
        # Build model with `build_model` function
        model = build_model(ticker=request.ticker)
        # Load stored model
        model.load()
        # Generate prediction
        prediction_formatted = model.predict_volatility(request.n_days)
        # Add `"success"` key to `response`
        response['success'] = True
        # Add `"message"` key to `response`
        response['message'] = "Prediction generated"
        # Add `"forecast"` key to `response`
        response['forecast'] = prediction_formatted
        # Add `"message"` key to `response`

    # Create except block
    except Exception as e:
        # Add `"success"` key to `response`
        response['success'] = False
        # Add `"forecast"` key to `response`
        response['forecast'] = {}
        #  Add `"message"` key to `response`
        response['message'] = str(e)

        # Return response
    return response
