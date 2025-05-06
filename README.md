

## 1. `preprocess.py` – Cleaning & Encoding

**Purpose:** Turn raw CSV into a fully numeric, ML‑ready dataset.

1. **Load or Create Dummy Data**

   * Checks for `cgpa_data.csv`; if missing, writes a small example so you can follow along.
2. **Inspect & Handle Missing Values**

   * Prints out any null counts; warns if you need imputation.
3. **Drop Identifiers**

   * Removes `StudentID`—an arbitrary ID that doesn’t help the model learn.
4. **Encode Binary Features**

   * Maps `Yes`/`No` to `1`/`0` for columns like `TuitionAccess`, `PlaysSport`, etc.
5. **Encode Ordinal Features**

   * Converts ordered categories (`High school` → 0, `Graduate` → 1, `Postgrad` → 2; similarly for income) into numbers.
6. **One‑Hot Encode Nominal Features**

   * Turns `Gender` into separate columns (`Gender_Female`, `Gender_Male`, `Gender_Other`).
7. **Save**

   * Writes the clean data to `preprocessed_cgpa_data.csv`.

> **Why?**
> Machine learning models need purely numerical inputs. This script centralizes all your cleaning/encoding logic in one place.

---

## 2. `split_and_scale.py` – Train/Test Split & Feature Scaling

**Purpose:** Prepare your features so the model can learn effectively and fairly.

1. **Load Clean Data**

   * Reads in `preprocessed_cgpa_data.csv`.
2. **Type Corrections & NaN Handling**

   * Ensures any stray booleans or strings are numeric; drops rows that still have NaNs.
3. **Train/Test Split**

   * Uses scikit‑learn’s `train_test_split` to reserve 20% of your data for evaluation (controlled by a `random_seed` for reproducibility).
4. **Feature Scaling**

   * Fits a `StandardScaler` on the **training** features (so the model doesn’t “peek” at test data) and applies it to both train & test sets.
   * Scaling (zero mean, unit variance) is crucial for many algorithms to converge and treat all features equally.

> **Why separate splitting & scaling?**
> You must fit your scaler **only** on training data. If you scaled before splitting, information from the test set would leak into training.

---

## 3. `train_and_save.py` – Model Training & Serialization

**Purpose:** Train a regression model and save both the model and scaler for future use.

1. **Re‑use the Data Prep Function**

   * Loads, splits, and scales via the same logic as `split_and_scale.py`.
2. **Train**

   * Fits a `RandomForestRegressor` (an ensemble of decision trees) on the scaled training data.
3. **Evaluate**

   * Reports metrics like Mean Absolute Error (MAE) and R² on the test set for a sanity check.
4. **Serialize with `pickle`**

   ```python
   import pickle
   with open('rf_cgpa_model.pkl','wb') as f:
       pickle.dump(model, f)
   with open('scaler.pkl','wb') as f:
       pickle.dump(scaler, f)
   ```

   * **`pickle`** is Python’s built‑in serialization library. “Pickling” converts live Python objects (your trained model and scaler) into a byte stream you can write to disk. Later you “unpickle” to restore those objects exactly as they were.

> **Why use `pickle`?**
>
> * **Persistence:** Don’t retrain every time—just load your saved artifacts.
> * **Reusability:** Ship your model & preprocessing pipeline to other scripts or services without re‑running code.

---

## 4. `predict.py` – Loading & Inference

**Purpose:** Load your saved model/scaler and predict CGPA for brand‑new students.

1. **Load Artifacts**

   ```python
   with open('rf_cgpa_model.pkl','rb') as f:
       model = pickle.load(f)
   with open('scaler.pkl','rb') as f:
       scaler = pickle.load(f)
   ```
2. **Prepare New Data**

   * Build a `DataFrame` matching exactly the feature names and order the scaler expects.
   * The script checks for missing or extra columns and warns you.
3. **Scale & Predict**

   * Applies `scaler.transform(...)` to map new inputs to the same scale as training.
   * Calls `model.predict(...)` to output CGPA estimates.

> **Why keep prediction separate?**
> Separating training from inference makes your code modular and production‑ready: you never accidentally retrain when you’re just serving predictions.

---

### Putting It All Together

1. **`preprocess.py`** → clean raw data
2. **`split_and_scale.py`** → split & scale features
3. **`train_and_save.py`** → train model, evaluate, and **pickle** both model & scaler
4. **`predict.py`** → unpickle artifacts, prepare new student data, and make predictions

Each script has a single responsibility, making your pipeline easy to understand, debug, and extend.
